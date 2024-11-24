from typing import List,Dict
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, EmailStr

class ChatMessage(BaseModel):
    message: str
    user_id: int
    is_ai: bool = False  # Added with a default value
    id: int | None = None  # Optional, for when reading from DB

    class Config:
        from_attributes = True  # This allows conversion from SQLAlchemy models

class User(BaseModel):
    name: str
    is_manager: bool


class Feedback(BaseModel):
    user_id: int
    insight: str
    for_manager: bool


class PlanOfAction(BaseModel):
    user_id: int
    user_name:str
    categorized_action_items:Dict
    target_user_id: int

class RunPipelineRequest(BaseModel):
    user_id: int

class UserRequest(BaseModel):
    user_id: int


class ActionPlan(BaseModel):
    action_title: str
    action_status: str
    action_plan: List[str]
    progress_notes: List[str]

class CategoryGroup(BaseModel):
    category: str
    action_items: List[ActionPlan]

class EmployeeActionItems(BaseModel):
    user_id: int
    name: str
    categorized_action_items: List[CategoryGroup]