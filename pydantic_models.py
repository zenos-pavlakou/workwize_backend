from typing import List
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, EmailStr

class User(BaseModel):
    id: int
    name: str
    is_manager: bool