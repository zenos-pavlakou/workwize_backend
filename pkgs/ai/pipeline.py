from pkgs.ai import feedback_identifier

from db_engine import SessionLocal


def run_pipeline(user_id: int, api_key: str):
    session = SessionLocal()
    feedback = feedback_identifier.run(user_id=user_id, api_key=api_key, session=session)
