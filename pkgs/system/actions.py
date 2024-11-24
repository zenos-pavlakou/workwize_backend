from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.types import JSON
from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends
from db_models import PlanOfAction as DbPlanOfActionModel
from db_models import PlanOfAction as DbPlanOfAction
from db_models import Chat as DbChat
from db_engine import engine, get_db


def plan_of_actions(
        user_id: int,
        user_name: str,
        categorized_action_items: Dict[str, Any],
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


def delete_chat_and_plan_of_actions_of_employee(user_id: int, db: Session = Depends(get_db)):
    try:
        # Delete plan of actions
        deleted_plans = db.query(DbPlanOfAction).filter(
            DbPlanOfAction.user_id == user_id
        ).delete(synchronize_session=False)

        # Delete chats
        deleted_chats = db.query(DbChat).filter(
            DbChat.user_id == user_id
        ).delete(synchronize_session=False)

        # Commit the transaction
        db.commit()

        return {
            "status": "success",
            "deleted_records": {
                "plans_of_action": deleted_plans,
                "chats": deleted_chats
            }
        }

    except Exception as e:
        # Rollback in case of error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete records: {str(e)}"
        )