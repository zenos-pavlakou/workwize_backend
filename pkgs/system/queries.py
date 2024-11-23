from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic_models import ChatMessage as PydanticChatModel
from pydantic_models import PlanOfAction as PydanticPlanOfAction
from db_models import Chat as DbChatModel
from db_models import PlanOfAction as DbPlanOfActionModel
from db_engine import engine, get_db


def get_user_conversation(
        user_id: int,
        db: Session = Depends(get_db)
) -> List[PydanticChatModel]:
    """
    Get all feedback items for a specific user.

    Args:
        user_id (int): The ID of the user to get feedback for
        db (Session): Database session dependency

    Returns:
        List[PydanticFeedbackModel]: List of feedback items converted to Pydantic models
    """
    # Query all chat items for the user
    chat_items = (
        db.query(DbChatModel)
        .filter(DbChatModel.user_id == user_id)
        .all()
    )

    # Convert to Pydantic models
    pydantic_chat_items = [
        PydanticChatModel(
            id=item.id,
            user_id=item.user_id,
            message=item.message
        )
        for item in chat_items
    ]

    return pydantic_chat_items

def get_personal_plan_of_actions(user_id: int,db: Session = Depends(get_db)):
    plan_of_actions = (
        db.query(DbPlanOfActionModel)
        .filter(DbPlanOfActionModel.user_id == user_id)
        .all()
    )
     # Convert to Pydantic models
    pydantic_plan_of_actions = [
        PydanticPlanOfAction(
            user_id= actions.user_id,
            user_name= actions.user_name ,
            categorized_action_items=actions.categorized_action_items,
            target_user_id= actions.target_user_id,
        )
        for actions in plan_of_actions
    ]

def get_plan_of_actions(db: Session = Depends(get_db)):
    plan_of_actions = (
        db.query(DbPlanOfActionModel)
        .all()
    )
     # Convert to Pydantic models
    pydantic_plan_of_actions = [
        PydanticPlanOfAction(
            user_id= actions.user_id,
            user_name= actions.user_name ,
            categorized_action_items=actions.categorized_action_items,
            target_user_id= actions.target_user_id,
        )
        for actions in plan_of_actions
    ]