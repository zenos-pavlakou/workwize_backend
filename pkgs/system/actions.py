#from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.types import JSON
from fastapi import Depends,HTTPException
#from pydantic_models import ChatMessage as PydanticChatModel
from db_models import PlanOfAction as DbPlanofActionmodel
from db_engine import engine, get_db


def plan_of_actions(user_id: int,user_name: str,categorized_action_items: JSON,target_user_id:int, db: Session = Depends(get_db)):
    plan_of_actions = DbPlanofActionmodel(user_id=user_id,user_name=user_name,categorized_action_items=categorized_action_items,target_user_id=target_user_id)
    db.add(plan_of_actions)
    try :
         db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))