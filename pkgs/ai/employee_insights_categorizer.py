from typing import List, Dict
from llama_index.legacy.llms.openai import OpenAI


class EmployeeInsightsCategorizer:
    def __init__(self, llm: OpenAI):
        self.llm = llm
        self.categories = {
            "Professional Upskilling": [
                "skill development",
                "training and certifications",
                "knowledge expansion",
                "competency building",
                "professional education",
                "domain expertise",
                "industry knowledge",
                "specialized capabilities"
            ],
            "Leadership Development": [
                "leadership skills",
                "team management",
                "mentoring abilities",
                "project leadership",
                "decision making",
                "delegation skills",
                "strategic thinking",
                "people management"
            ],
            "Career Growth": [
                "role progression",
                "career path planning",
                "promotion opportunities",
                "responsibility expansion",
                "professional goals",
                "career transition",
                "specialization interests",
                "industry knowledge"
            ],
            "Project Interests": [
                "project type preferences",
                "innovative projects",
                "research opportunities",
                "cross-functional work",
                "project scope",
                "technical challenges",
                "creative opportunities",
                "project ownership"
            ],
            "Work Style Preferences": [
                "task preferences",
                "working environment",
                "collaboration style",
                "time management",
                "productivity patterns",
                "work-life balance",
                "remote work",
                "autonomous work"
            ]
        }

    def categorize_insights(self, feedback_items: List[str]) -> Dict[str, List[str]]:
        """Categorize employee-relevant feedback items"""
        if not feedback_items:
            return {}

        category_desc = "\n".join([
            f"# {cat}:\n" + "\n".join(f"- {subcat}" for subcat in subcats)
            for cat, subcats in self.categories.items()
        ])

        feedback_list = "\n".join([f"Item {i + 1}: {item}" for i, item in enumerate(feedback_items)])

        prompt = f"""As a career development analyst, categorize each feedback item into the most appropriate personal development category.

Categories and their themes:
{category_desc}

Classification Rules:
1. Professional Upskilling focuses on:
   - Any specific skills the employee wants to learn or improve
   - Interest in new methodologies or practices
   - Professional certifications or training
   - Knowledge gaps they want to fill
   - Both technical and non-technical skill development

2. Leadership Development includes:
   - Interest in leading teams or projects
   - Desire to improve management skills
   - Mentoring and guidance abilities
   - Strategic and decision-making capabilities

3. Career Growth relates to:
   - Long-term career aspirations
   - Desired role changes or promotions
   - Professional development goals
   - Career path planning

4. Project Interests covers:
   - Types of projects they want to work on
   - Desired level of project responsibility
   - Interest in specific project areas
   - Project scope preferences

5. Work Style Preferences encompasses:
   - Preferred working methods
   - Collaboration preferences
   - Work environment needs
   - Work-life balance considerations

Feedback items to categorize:
{feedback_list}

Provide classification in this format:
ITEM: [exact feedback text]
CATEGORY: [exact category name]

Focus on personal development opportunities and career aspirations."""

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

            # Updated keyword matching for fallback
            if any(word in item_lower for word in ["skill", "training", "learning", "knowledge", "certification", "education"]):
                categorized["Professional Upskilling"].append(item)
            elif any(word in item_lower for word in ["leadership", "leading", "management", "mentor"]):
                categorized["Leadership Development"].append(item)
            elif any(word in item_lower for word in ["career", "growth", "promotion", "progression"]):
                categorized["Career Growth"].append(item)
            elif any(word in item_lower for word in ["project", "innovative", "research", "challenge"]):
                categorized["Project Interests"].append(item)
            elif any(word in item_lower for word in ["work style", "environment", "collaboration", "balance"]):
                categorized["Work Style Preferences"].append(item)

        return {k: v for k, v in categorized.items() if v}


def run(feedback_items: List[str], api_key: str) -> Dict:
    """
    Process employee-relevant feedback items and categorize them.

    Args:
        feedback_items (List[str]): List of feedback items to categorize
        api_key (str): OpenAI API key

    Returns:
        Dict: Categorized feedback
    """
    try:
        categorizer = EmployeeInsightsCategorizer(OpenAI(
            model="gpt-3.5-turbo",
            api_key=api_key
        ))

        categorized_feedback = categorizer.categorize_insights(feedback_items)

        return {
            "categorized_insights": categorized_feedback
        }
    except Exception as e:
        print(f"Error in employee insights categorization: {str(e)}")
        return {
            "categorized_insights": {}
        }