from dataclasses import dataclass
from typing import List, Dict
from llama_index.legacy.llms.openai import OpenAI


class FeedbackRoutingAgent:
    def __init__(self, llm: OpenAI):
        self.llm = llm

    def route_feedback(self, feedback_data: Dict) -> Dict:
        """
        Routes feedback items to manager and/or employee dashboard based on relevance.
        """
        prompt = f"""As a feedback routing specialist, categorize each feedback item based on its relevance to managers and/or employees.
                    Remove anything that might be a conduct violation or HR case. For example, ignore things that 
                    indicate harassment or inappropriate comments.

                    Guidelines for categorization:

                    Manager-only relevant feedback includes:
                    - Issues with task delegation or assignment
                    - Team organization concerns
                    - Resource allocation problems
                    - Workplace environment issues that need manager intervention
                    - Management style feedback

                    Employee-only relevant feedback includes:
                    - Personal skill development interests without leadership component
                    - Individual performance goals
                    - Personal work preferences
                    - Self-improvement areas not related to leadership

                    Feedback relevant to both includes:
                    - Leadership development aspirations
                    - Career growth plans involving team management
                    - Communication improvement needs
                    - Team dynamics issues where both parties need awareness
                    - Professional development needs that require manager support

                    Feedback items to categorize:
                    {feedback_data['feedback']}

                    For each item, respond in the format:
                    ROUTING: [MANAGER_ONLY or EMPLOYEE_ONLY or BOTH]: [Original feedback text]
                    """

        try:
            response = self.llm.complete(prompt)
            return self._parse_routing(response.text, feedback_data['user_id'])
        except Exception as e:
            print(f"Error in routing: {str(e)}")
            return self._generate_fallback_routing(feedback_data)

    def _parse_routing(self, response_text: str, user_id: int) -> Dict:
        """Parse the LLM response into categorized feedback with support for multiple classifications"""
        manager_feedback = []
        employee_feedback = []

        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('ROUTING:'):
                # Remove 'ROUTING:' prefix
                content = line[8:].strip()
                # Split by first colon to separate routing from feedback
                routing, feedback = content.split(':', 1)
                routing = routing.strip()
                feedback = feedback.strip()

                # Handle different routing cases
                if routing == 'MANAGER_ONLY':
                    manager_feedback.append(feedback)
                elif routing == 'EMPLOYEE_ONLY':
                    employee_feedback.append(feedback)
                elif routing == 'BOTH':
                    manager_feedback.append(feedback)
                    employee_feedback.append(feedback)

        return {
            "applicable_to_manager": manager_feedback,
            "applicable_to_user": employee_feedback,
            "user_id": user_id,
            "routing_summary": {
                "manager_only": len([f for f in manager_feedback if f not in employee_feedback]),
                "employee_only": len([f for f in employee_feedback if f not in manager_feedback]),
                "shared": len([f for f in manager_feedback if f in employee_feedback])
            }
        }

    @staticmethod
    def _generate_fallback_routing(feedback_data: Dict) -> Dict:
        """Generate fallback routing if parsing fails"""
        return {
            "applicable_to_manager": [],
            "applicable_to_user": feedback_data['feedback'],
            "user_id": feedback_data['user_id'],
            "routing_summary": {
                "manager_only": 0,
                "employee_only": len(feedback_data['feedback']),
                "shared": 0
            }
        }


class FeedbackProcessor:
    def __init__(self, api_key: str):
        self.llm = OpenAI(
            model="gpt-4",
            api_key=api_key
        )
        self.router = FeedbackRoutingAgent(self.llm)

    def process_feedback(self, feedback_data: Dict) -> Dict:
        """Process feedback and route to appropriate dashboards"""
        return self.router.route_feedback(feedback_data)


def run(*, feedback_data: Dict, api_key: str) -> Dict:
    """
    Process feedback data and route it to appropriate dashboards.

    Args:
        feedback_data (Dict): Dictionary containing 'feedback' list and 'user_id'
        api_key (str): OpenAI API key

    Returns:
        Dict: Processed feedback with routing information and summary statistics
    """
    processor = FeedbackProcessor(api_key=api_key)
    result = processor.process_feedback(feedback_data)
    return result