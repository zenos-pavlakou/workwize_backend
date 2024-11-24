from pkgs.system import queries as system_queries
from pydantic_models import ChatMessage
from typing import List, Dict
from dataclasses import dataclass

from llama_index.legacy.llms.openai import OpenAI


@dataclass
class Finding:
    """Structure for key findings"""
    insight: str


class FeedbackAnalyzer:
    def __init__(self, llm: OpenAI):
        self.llm = llm

    def analyze_feedback(self, feedback_items: List[str]) -> List[Finding]:
        """Extract key findings from feedback messages"""
        feedback_context = "\n".join([f"- {item}" for item in feedback_items])

        prompt = f"""As a feedback analyst, review these employee messages and provide key findings.
                    Follow these strict guidelines:

                    1. Start each finding with "Employee expressed/mentioned/indicated/shared"
                    2. Focus only on what was directly expressed, not implications
                    3. Keep each finding to a single, clear point
                    4. Be concise and specific
                    5. Avoid speculation or extrapolation
                    6. Use simple, direct language
                    7. If the employee has made any rude or unreasonable comments, do not include them in the key findings.
                    8. Do not include any key points that may make the employee look incompetent.
                    9. Try not to have multiple key findings that are essentially the same.
                    10. Try to summarize each key finding as much as possible, ideally no more than 10 words. If need be, split a key finding
                    into multiple key findings. For example, 'Employee suggested a more systematic approach to scheduling and a collaborative tool for better task visibility.'
                    could be split into shorter key findings such as: 'Employee suggested implementing a systematic scheduling approach' and 'Employee requested a collaborative 
                    tool for task visibility'

                    Employee Feedback:
                    {feedback_context}

                    Provide between 2 and 6 key findings. Format each as:
                    FINDING: [Direct, concise observation of what was expressed]

                    Example good findings:
                    - Employee expressed concern over lack of clear task ownership
                    - Employee mentioned difficulties with current project management tools
                    - Employee indicated interest in more challenging assignments

                    Example bad findings (too interpretative/speculative):
                    - Lack of clear task ownership is causing efficiency issues
                    - Project management tools need to be upgraded
                    - Team would benefit from more challenging assignments

                    Focus on capturing what was actually expressed by the employee.""".strip()

        try:
            response = self.llm.complete(prompt)
            return self.parse_findings(response.text)
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return self.generate_fallback_findings()

    def parse_findings(self, response_text: str) -> List[Finding]:
        """Parse the LLM response into a list of findings"""
        findings = []

        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('FINDING:'):
                insight = line.split(':', 1)[1].strip()
                if insight:
                    findings.append(Finding(insight=insight))

        return findings or self.generate_fallback_findings()

    @staticmethod
    def generate_fallback_findings(self) -> List[Finding]:
        """Generate fallback findings if parsing fails"""
        return [Finding(
            insight="Unable to extract feedback"
        )]


class FeedbackExtractionAgent:
    def __init__(self, api_key: str):
        self.llm = OpenAI(
            model="gpt-4",
            api_key=api_key
        )
        self.analyzer = FeedbackAnalyzer(self.llm)

    def process_conversation(self, conversation: List[Dict]) -> List[Finding]:
        employee_messages = [
            entry['message'] for entry in conversation
            if entry['from'] == 'employee'
        ]
        return self.analyzer.analyze_feedback(employee_messages)

    def generate_report(self, findings: List[Finding]) -> list[str]:
        """Generate a simple report of key findings"""
        if not findings:
            return "No key findings identified."

        report = []
        for finding in findings:
            report.append(finding.insight)

        return report

def get_user_conversation(user_id: int, session) -> list[ChatMessage]:
    return system_queries.get_user_conversation(user_id, session)

def format_user_conversation(conversation_data: list[ChatMessage]):
    if not conversation_data:
        return {}
    formatted_data = dict()
    formatted_data["user_id"] = conversation_data[0].user_id
    formatted_data["conversation"] = [
        {
            "from": "AI" if item.is_ai else "employee",
            "message": item.message
        } for item in conversation_data
    ]
    return formatted_data

def run(*, user_id: int, api_key: str, session):
    conversation = get_user_conversation(user_id, session)
    formatted_conversation = format_user_conversation(conversation)
    agent = FeedbackExtractionAgent(api_key=api_key)
    findings = agent.process_conversation(formatted_conversation['conversation'])
    report = agent.generate_report(findings)
    result = dict()
    result["user_id"] = formatted_conversation["user_id"]
    result["feedback"] = report
    return result