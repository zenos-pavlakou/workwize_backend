from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

from . import config

__all__ = ["User"]

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_manager = Column(Boolean, default=True)

def init_db():
    engine = create_engine(config.DB_URL)
    Base.metadata.create_all(engine)
    return engine

# Add this line at the bottom to execute the function
if __name__ == "__main__":
    engine = init_db()