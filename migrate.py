from db_models import (
    Base, 
    User
)

from db_engine import engine

Base.metadata.create_all(bind=engine, tables=[User.__table__])