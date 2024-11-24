import json
import os
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Set
import json

from db_engine import engine, get_db

from pydantic_models import User as PydanticUser
from pydantic_models import UserRequest
from pydantic_models import EmployeeActionItems as PydanticEmployeeActionItems
from db_models import User as DbUser

from pkgs.system import queries as system_queries
from pkgs.system import actions as system_actions

router = APIRouter()


@router.post("/users")
async def add_user_to_db(user: PydanticUser, db: Session = Depends(get_db)):
    # If the user does not exist, add them to the database
    new_user = DbUser(name=user.name, is_manager=user.is_manager)
    db.add(new_user)
    try:
        db.commit()
        return {"status": "User added"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{user_id}")
async def get_conversation(user_id: int, db: Session = Depends(get_db)):
    return system_queries.get_user_conversation(user_id, db)

@router.get("/employees/{user_id}")
async def get_employee_action_plan(user_id: int, db: Session = Depends(get_db)) -> PydanticEmployeeActionItems | None:
    return system_queries.get_user_action_plan(user_id, db)

@router.get("/employees")
async def get_manager_action_plan(db: Session = Depends(get_db)) -> list[PydanticEmployeeActionItems] | None:
    return system_queries.get_manager_action_plan(db)

@router.delete("/chat-and-plan-of-action")
async def delete_chat_and_plan_of_action(user: UserRequest, db: Session = Depends(get_db)):
    system_actions.delete_chat_and_plan_of_actions_of_employee(user.user_id, db)


