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
from db_models import User as DbUser

from pkgs.system import queries as system_queries

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
    return await system_queries.get_user_conversation(user_id, db)