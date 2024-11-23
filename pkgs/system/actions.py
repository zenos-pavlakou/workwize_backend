from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.types import JSON
# from fastapi import Depends,HTTPException
# from fastapi.responses import StreamingResponse
from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends
#from pydantic_models import ChatMessage as PydanticChatModel
from db_models import PlanOfAction as DbPlanOfActionModel
from db_engine import engine, get_db

# router = APIRouter()

def plan_of_actions(
    user_id: int,
    user_name: str,
    categorized_action_items: Dict[str, Any],  # Changed from JSON to Dict[str, Any]
    target_user_id: int,
    db: Session = Depends(get_db)
):
    plans_of_action = DbPlanOfActionModel(
        user_id=user_id,
        user_name=user_name,
        categorized_action_items=categorized_action_items,
        target_user_id=target_user_id
    )
    db.add(plans_of_action)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
