from db_models import (
    Base,
    User,
    Chat,
    PlanOfAction
)

from db_engine import engine

Base.metadata.create_all(bind=engine, tables=[User.__table__])
Base.metadata.create_all(bind=engine, tables=[Chat.__table__])
Base.metadata.create_all(bind=engine,tables=[PlanOfAction.__table__])