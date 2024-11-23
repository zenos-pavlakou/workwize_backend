from typing import Dict, List, Any
from llama_index.legacy.llms.openai import OpenAI


class FeedbackCoach:
    def __init__(self, llm: OpenAI):
        self.llm = llm

    def transform_feedback(self, feedback_results: Dict[str, Dict[str, Dict[str, List[str]]]], employee_name: str) -> Dict[
        str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """
        Transform categorized feedback into action titles and action steps

        Args:
            feedback_results: Dict in format:
            {
                'employee': {'categorized_insights': {'category': ['feedback items']}},
                'manager': {'categorized_insights': {'category': ['feedback items']}}
            }
            employee_name: Name of the employee
        """
        transformed_feedback = {
            'employee': {'action_plans': {}},
            'manager': {'action_plans': {}}
        }

        if 'employee' in feedback_results:
            employee_insights = feedback_results['employee']['categorized_insights']
            transformed_feedback['employee']['action_plans'] = self._generate_action_plans(
                insights=employee_insights,
                role_type='employee',
                employee_name=employee_name
            )

        if 'manager' in feedback_results:
            manager_insights = feedback_results['manager']['categorized_insights']
            transformed_feedback['manager']['action_plans'] = self._generate_action_plans(
                insights=manager_insights,
                role_type='manager',
                employee_name=employee_name
            )

        return transformed_feedback

    def _generate_action_plans(self, insights: Dict[str, List[str]], role_type: str, employee_name: str) -> Dict[str, Dict[str, Any]]:
        """Generate action titles and action steps for each category of insights"""
        action_plans = {}
        employee_name = employee_name.split(" ")[0]

        for category, feedback_items in insights.items():
            if not feedback_items:
                continue

            category_plans = []
            for feedback in feedback_items:
                # Customize prompts based on role type
                if role_type == 'employee':
                    title_prompt = f"""Based on this {category} feedback, generate a concise, specific action plan title (3-7 words).
Write it from a first-person perspective, as if you are the person who will take these actions.

Feedback: {feedback}

Respond with only the title on a single line. Example:
'Enhance My Cloud Computing Skills' or 'Improve My Team Communication'"""

                    steps_prompt = f"""Convert this {category} feedback into specific action steps. 
Write the steps from a first-person perspective, as actions you will take personally.
Provide 2-3 clear, actionable steps for improvement.

Feedback: {feedback}

Respond with only action steps, one per line, starting with 'ACTION:'. Be specific and concrete. Example:
ACTION: Enroll in an advanced cloud computing certification course
ACTION: Practice new skills by building a cloud-native application"""

                else:  # manager
                    title_prompt = f"""Based on this {category} feedback, generate a concise, specific action plan title (3-7 words) 
for actions you as a manager will take regarding {employee_name}.

Feedback: {feedback}

Respond with only the title on a single line. Example:
'Review {employee_name}'s Task Distribution' or 'Support {employee_name}'s Skill Development'"""

                    steps_prompt = f"""Convert this {category} feedback into specific action steps that you as a manager will take.
Use {employee_name}'s name instead of saying "the employee".
Provide 2-3 clear, actionable steps for improvement.

Feedback: {feedback}

Respond with only action steps, one per line, starting with 'ACTION:'. Be specific and concrete. Example:
ACTION: Schedule a meeting with {employee_name} to discuss their workload distribution
ACTION: Create opportunities for {employee_name} to lead team projects"""

                title_response = self.llm.complete(title_prompt)
                action_title = title_response.text.strip().strip("'").strip('"')

                steps_response = self.llm.complete(steps_prompt)
                actions = self._parse_actions(steps_response.text)

                category_plans.append({
                    'action_title': action_title,
                    'actions': actions
                })

            action_plans[category] = category_plans

        return action_plans

    def _parse_actions(self, response_text: str) -> List[str]:
        """Parse the LLM response into a list of action steps"""
        actions = []

        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('ACTION:'):
                action = line[7:].strip()
                if action:
                    actions.append(action)

        return actions


def run(feedback_results: Dict[str, Any], api_key: str, employee_name: str) -> Dict[str, Any]:
    """Process feedback results and generate action titles with action steps."""
    coach = FeedbackCoach(OpenAI(
        model="gpt-4",
        api_key=api_key
    ))

    transformed_feedback = coach.transform_feedback(feedback_results, employee_name)
    return transformed_feedback