from typing import List
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, EmailStr

class User(BaseModel):
    name: str
    is_manager: bool