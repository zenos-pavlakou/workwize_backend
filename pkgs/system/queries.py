from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic_models import ChatMessage as PydanticChatModel
from pydantic_models import PlanOfAction as PydanticPlanOfAction
from pydantic_models import User as PydanticUserModel
from db_models import Chat as DbChatModel
from db_models import PlanOfAction as DbPlanOfActionModel
from pydantic_models import EmployeeActionItems as PydanticEmployeeActionItems
from pydantic_models import CategoryGroup as PydanticCategoryGroup
from pydantic_models import ActionPlan as PydanticActionPlan
from db_models import User as DbUserModel
from db_engine import engine, get_db
import json


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
    return pydantic_plan_of_actions

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
    return pydantic_plan_of_actions

def get_user(user_id: int,db: Session = Depends(get_db)) ->PydanticUserModel:
    user = (
        db.query(DbUserModel).filter(DbUserModel.id == user_id)
        .one_or_none()
    )
    result=PydanticUserModel(name=user.name,is_manager=user.is_manager)
    return result


def get_user_action_plan(user_id: int, db: Session = Depends(get_db)) -> PydanticEmployeeActionItems | None:
    # Get the action plan from database
    action_plan = (
        db.query(DbPlanOfActionModel)
        .filter(DbPlanOfActionModel.target_user_id == user_id)
        .filter(DbPlanOfActionModel.user_id == user_id)
        .one_or_none()
    )

    if not action_plan:
        return None

    # Get the raw value
    raw_data = getattr(action_plan, 'categorized_action_items', None)

    # Extract the inner categorized_action_items array
    categorized_items = raw_data.get('categorized_action_items', []) if isinstance(raw_data, dict) else []

    return PydanticEmployeeActionItems(
        user_id=action_plan.target_user_id,
        name=action_plan.user_name,
        categorized_action_items=[
            PydanticCategoryGroup(
                category=category_group["category"],
                action_items=[
                    PydanticActionPlan(
                        action_title=item["action_title"],
                        action_status=item["action_status"],
                        action_plan=item["action_plan"],
                        progress_notes=item["progress_notes"]
                    )
                    for item in category_group["action_items"]
                ]
            )
            for category_group in categorized_items
        ]
    )


def get_manager_action_plan(db: Session = Depends(get_db)) -> list[PydanticEmployeeActionItems]:
    # Get all action plans where target_user_id is 1
    action_plans = (
        db.query(DbPlanOfActionModel)
        .filter(DbPlanOfActionModel.target_user_id == 1)
        .all()
    )

    if not action_plans:
        return []

    result = []
    for action_plan in action_plans:
        # Get the raw value
        raw_data = getattr(action_plan, 'categorized_action_items', None)

        # Extract the inner categorized_action_items array
        categorized_items = raw_data.get('categorized_action_items', []) if isinstance(raw_data, dict) else []

        employee_action_items = PydanticEmployeeActionItems(
            user_id=action_plan.user_id,
            name=action_plan.user_name,
            categorized_action_items=[
                PydanticCategoryGroup(
                    category=category_group["category"],
                    action_items=[
                        PydanticActionPlan(
                            action_title=item["action_title"],
                            action_status=item["action_status"],
                            action_plan=item["action_plan"],
                            progress_notes=item["progress_notes"]
                        )
                        for item in category_group["action_items"]
                    ]
                )
                for category_group in categorized_items
            ]
        )
        result.append(employee_action_items)

    return result