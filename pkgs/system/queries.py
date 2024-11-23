from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic_models import ChatMessage as PydanticChatModel
from db_models import Chat as DbChatModel
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