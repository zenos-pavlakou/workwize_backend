from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

__all__ = ["User", "Chat"]  # Include both classes


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_manager = Column(Boolean, default=True)

    # Add the back reference for the relationship
    chats = relationship("Chat", back_populates="user")


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    is_ai = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="chats")