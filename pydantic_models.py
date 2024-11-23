from typing import List
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