from typing import List
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, EmailStr

class ChatMessage(BaseModel):
    message: str
    user_id: int

class User(BaseModel):
    name: str
    is_manager: bool