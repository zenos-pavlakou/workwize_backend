from pkgs.ai import feedback_identifier, feedback_router, manager_insights_categorizer, employee_insights_categorizer, coach
from pprint import pprint
from db_engine import SessionLocal
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List


def transform_pipeline_results(pipeline_results: Dict[str, Any], user_id: int, user_name: str) -> Dict[str, Any]:
    """
    Transform pipeline results into a standardized format with categorized action items.

    Args:
        pipeline_results: Results from the feedback pipeline
        user_id: ID of the user
        user_name: Name of the user

    Returns:
        Dict containing user info and categorized action items
    """

    # Initialize the output structure
    transformed_results = {
        "user_id": user_id,
        "name": user_name,
        "categorized_action_items": []
    }

    # Combine all action plans from both employee and manager sections
    all_categories = {}

    # Process employee action plans
    if 'employee' in pipeline_results and 'action_plans' in pipeline_results['employee']:
        for category, items in pipeline_results['employee']['action_plans'].items():
            if category not in all_categories:
                all_categories[category] = []

            for item in items:
                action_item = {
                    "action_title": item['action_title'],
                    "action_status": "pending review",
                    "action_plan": item['actions'],
                    "progress_notes": []
                }
                all_categories[category].append(action_item)

    # Process manager action plans
    if 'manager' in pipeline_results and 'action_plans' in pipeline_results['manager']:
        for category, items in pipeline_results['manager']['action_plans'].items():
            if category not in all_categories:
                all_categories[category] = []

            for item in items:
                action_item = {
                    "action_title": item['action_title'],
                    "action_status": "pending review",
                    "action_plan": item['actions'],
                    "progress_notes": []
                }
                all_categories[category].append(action_item)

    # Convert the categories dictionary to the required list format
    categorized_items = []
    for category, items in all_categories.items():
        category_entry = {
            "category": category,
            "action_items": items
        }
        categorized_items.append(category_entry)

    transformed_results["categorized_action_items"] = categorized_items

    return transformed_results

def run_pipeline(user_id: int, user_name: str, api_key: str) -> Dict[str, Any]:
    session = SessionLocal()
    # Get initial feedback
    feedback = feedback_identifier.run(user_id=user_id, api_key=api_key, session=session)

    # Route feedback
    routed_feedback = feedback_router.run(feedback_data=feedback, api_key=api_key)
    manager_insights = routed_feedback['applicable_to_manager']
    employee_insights = routed_feedback['applicable_to_user']

    # Create dictionary to store results
    results = {
        'manager': None,
        'employee': None
    }

    # Create tasks dictionary to keep track of which future is for which categorizer
    future_tasks = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both tasks and store them with identifiers
        manager_task = executor.submit(
            manager_insights_categorizer.run,
            feedback_items=manager_insights,
            api_key=api_key
        )
        future_tasks[manager_task] = 'manager'

        employee_task = executor.submit(
            employee_insights_categorizer.run,
            feedback_items=employee_insights,
            api_key=api_key
        )
        future_tasks[employee_task] = 'employee'

        # Process results as they complete
        for future in as_completed([manager_task, employee_task]):
            task_type = future_tasks[future]
            try:
                result = future.result()
                results[task_type] = result
            except Exception as e:
                print(f"Error processing {task_type} insights: {str(e)}")
                results[task_type] = {
                    "error": str(e),
                    "categorized_insights": {}
                }
    results = coach.run(results, api_key)
    results = transform_pipeline_results(results, user_id, user_name)
    pprint(results)
    return results
