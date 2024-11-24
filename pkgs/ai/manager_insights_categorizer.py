from typing import List, Dict
from llama_index.legacy.llms.openai import OpenAI


class ManagerInsightsCategorizer:
    def __init__(self, llm: OpenAI):
        self.llm = llm
        self.categories = {
            "Task Management": [
                "task delegation",
                "workload distribution",
                "assignment clarity",
                "project allocation",
                "resource management",
                "deadline management",
                "task prioritization",
                "work distribution balance"
            ],
            "Communication Effectiveness": [
                "feedback delivery",
                "information sharing",
                "team updates",
                "communication clarity",
                "meeting effectiveness",
                "response timeliness",
                "communication channels",
                "status reporting"
            ],
            "Team Development": [
                "growth opportunities",
                "skill utilization",
                "career advancement",
                "mentoring needs",
                "training opportunities",
                "talent development",
                "role progression",
                "team capability building"
            ],
            "Process Improvement": [
                "workflow efficiency",
                "operational bottlenecks",
                "process optimization",
                "team coordination",
                "project management",
                "quality control",
                "productivity enhancement",
                "system effectiveness"
            ],
            "Work Environment": [
                "team dynamics",
                "workplace atmosphere",
                "collaboration issues",
                "team morale",
                "conflict management",
                "workplace behavior",
                "team cohesion",
                "professional conduct"
            ]
        }

    def categorize_insights(self, feedback_items: List[str]) -> Dict[str, List[str]]:
        """Categorize manager-relevant feedback items"""
        if not feedback_items:
            return {}

        category_desc = "\n".join([
            f"# {cat}:\n" + "\n".join(f"- {subcat}" for subcat in subcats)
            for cat, subcats in self.categories.items()
        ])

        feedback_list = "\n".join([f"Item {i + 1}: {item}" for i, item in enumerate(feedback_items)])

        prompt = f"""As a management feedback analyst, categorize each feedback item into the most appropriate management category.

Categories and their themes:
{category_desc}

Classification Rules:
1. Task Management focuses on:
   - How work is assigned and distributed
   - Clarity of assignments and expectations
   - Workload balance issues
   - Project and resource allocation

2. Communication Effectiveness covers:
   - Quality and clarity of manager communication
   - Information sharing practices
   - Meeting and update effectiveness
   - Responsiveness to team needs

3. Team Development includes:
   - Growth and advancement opportunities
   - Skill development and utilization
   - Career progression concerns
   - Training and mentoring needs

4. Process Improvement relates to:
   - Workflow and operational issues
   - Team coordination challenges
   - Project management practices
   - System and process effectiveness

5. Work Environment encompasses:
   - Team dynamics and morale
   - Workplace atmosphere issues
   - Professional conduct concerns
   - Collaboration challenges

Feedback items to categorize:
{feedback_list}

Provide classification in this format:
ITEM: [exact feedback text]
CATEGORY: [exact category name]

Focus on actionable insights for management improvement."""

        try:
            response = self.llm.complete(prompt)
            categorized = self.parse_categorization(response.text)
            if not categorized:
                return self.generate_fallback_categorization(feedback_items)
            return categorized
        except Exception as e:
            print(f"Categorization error: {str(e)}")
            return self.generate_fallback_categorization(feedback_items)

    def parse_categorization(self, response_text: str) -> Dict[str, List[str]]:
        """Parse the LLM response into categorized insights"""
        categorized = {category: [] for category in self.categories.keys()}

        current_item = None
        current_category = None

        for line in response_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('ITEM:'):
                current_item = line.split(':', 1)[1].strip()
            elif line.startswith('CATEGORY:'):
                current_category = line.split(':', 1)[1].strip()
                if current_item and current_category in categorized:
                    categorized[current_category].append(current_item)
                    current_item = None

        return {k: v for k, v in categorized.items() if v}

    def generate_fallback_categorization(self, items: List[str]) -> Dict[str, List[str]]:
        """Generate fallback categorization when parsing fails"""
        categorized = {category: [] for category in self.categories.keys()}

        for item in items:
            item_lower = item.lower()

            # Basic keyword matching for fallback
            if any(word in item_lower for word in ["task", "assignment", "workload", "delegation"]):
                categorized["Task Management"].append(item)
            elif any(word in item_lower for word in ["communication", "information", "meeting", "update"]):
                categorized["Communication Effectiveness"].append(item)
            elif any(word in item_lower for word in ["growth", "development", "career", "skill"]):
                categorized["Team Development"].append(item)
            elif any(word in item_lower for word in ["process", "workflow", "efficiency", "operation"]):
                categorized["Process Improvement"].append(item)
            elif any(word in item_lower for word in ["team", "environment", "atmosphere", "morale"]):
                categorized["Work Environment"].append(item)

        return {k: v for k, v in categorized.items() if v}


def run(feedback_items: List[str], api_key: str) -> Dict:
    """
    Process manager-relevant feedback items and categorize them.

    Args:
        feedback_items (List[str]): List of feedback items to categorize
        api_key (str): OpenAI API key

    Returns:
        Dict: Categorized feedback
    """
    try:
        categorizer = ManagerInsightsCategorizer(OpenAI(
            model="gpt-3.5-turbo",
            api_key=api_key
        ))

        categorized_feedback = categorizer.categorize_insights(feedback_items)

        return {
            "categorized_insights": categorized_feedback
        }
    except Exception as e:
        print(f"Error in manager insights categorization: {str(e)}")
        return {
            "categorized_insights": {}
        }