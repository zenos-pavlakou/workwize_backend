from sqlalchemy import create_engine, Column,JSON ,Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

__all__ = ["User", "Chat","PlanOfAction"]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_manager = Column(Boolean, default=True)

    # Add the back reference for the relationship
    chats = relationship("Chat", back_populates="user")
    #relation to PlanofAction
    plan_of_actions=relationship("PlanOfAction", back_populates="user")


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    is_ai = Column(Boolean, nullable=False)
    user = relationship("User", back_populates="chats")

class PlanOfAction(Base):
    __tablename__ = 'plan_of_actions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_name = Column(String(50), nullable=False)  # Matching the size with User.name
    categorized_action_items = Column(JSON, nullable=True)
    target_user_id = Column(Integer, nullable=False)

    
    # Relationship with User table
    user = relationship("User", back_populates="plan_of_actions")