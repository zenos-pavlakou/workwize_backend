from typing import Dict, List, Any
from llama_index.legacy.llms.openai import OpenAI
from random import randint


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

    def _generate_action_plans(self, insights: Dict[str, List[str]], role_type: str, employee_name: str) -> Dict[
        str, Dict[str, Any]]:
        """Generate action titles and action steps for each category of insights"""
        action_plans = {}
        employee_name = employee_name.split(" ")[0]

        # Generate random min and max action counts
        min_actions = randint(2, 3)
        max_actions = randint(4, 5)

        for category, feedback_items in insights.items():
            if not feedback_items:
                continue

            category_plans = []
            for feedback in feedback_items:
                # Customize prompts based on role type
                if role_type == 'employee':
                    title_prompt = f"""Based on this {category} feedback, generate a concise, specific action plan title (3-7 words).
    Write it from an informal perspective, as if you are the person who will take these actions. For example, say things like Improve Your Skills in X.

    Feedback: {feedback}

    Respond with only the title on a single line. Example:
    'Enhance Your Cloud Computing Skills' or 'Improve Your Team Communication'"""

                    steps_prompt = f"""Convert this {category} feedback into specific action steps. 
    Write the steps from a first-person perspective, as actions you will take personally.
    Provide {min_actions}-{max_actions} clear, actionable steps for improvement.

    IMPORTANT: Only suggest specific courses if the feedback explicitly mentions a desire or need for training/learning.
    If and only if training is mentioned in the feedback, include a specific course recommendation with platform and instructor.
    Focus on practical, hands-on actions that can be taken immediately rather than defaulting to formal training.

    Example formats:
    When training IS mentioned in feedback:
    ACTION: Enroll in AWS Solutions Architect Professional by Adrian Cantrill on learn.cantrill.io
    ACTION: Apply new cloud architecture patterns in the current project redesign

    When training is NOT mentioned:
    ACTION: Schedule weekly code reviews with senior developers
    ACTION: Document three key learnings from each project completion
    ACTION: Take the lead on the next client presentation

    Lastly, in the ACTIONS, do not use the word 'my'. Use the word 'your' instead.

    Feedback: {feedback}

    Respond with only action steps, one per line, starting with 'ACTION:'. Be specific and concrete."""

                else:  # manager
                    title_prompt = f"""Based on this {category} feedback, generate a concise, specific action plan title (3-7 words) 
    for actions you as a manager will take regarding {employee_name}.

    Feedback: {feedback}

    Respond with only the title on a single line. Example:
    'Review {employee_name}'s Task Distribution' or 'Support {employee_name}'s Skill Development'"""

                    steps_prompt = f"""Convert this {category} feedback into specific action steps that you as a manager will take.
    Use {employee_name}'s name instead of saying "the employee".
    Provide {min_actions}-{max_actions} clear, actionable steps for improvement.

    IMPORTANT: Only suggest specific courses if the feedback explicitly mentions a need for training/learning opportunities.
    If and only if training is specifically relevant to the feedback, include a specific course recommendation.
    Focus on actionable management steps rather than defaulting to training solutions.

    Example formats:
    When training IS mentioned in feedback:
    ACTION: Enroll {employee_name} in Executive Leadership by Wharton Business School on Coursera
    ACTION: Create monthly mentoring sessions to reinforce leadership training concepts

    When training is NOT mentioned:
    ACTION: Schedule bi-weekly 1:1s with {employee_name} to provide regular feedback
    ACTION: Assign {employee_name} as technical lead for the upcoming client project
    ACTION: Create opportunities for {employee_name} to mentor junior team members

    Feedback: {feedback}

    Respond with only action steps, one per line, starting with 'ACTION:'. Be specific and concrete."""

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
        model="gpt-3.5-turbo",
        api_key=api_key
    ))

    transformed_feedback = coach.transform_feedback(feedback_results, employee_name)
    return transformed_feedback