from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


usr = os.environ["DB_USERNAME"]
pswd = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]


engine = create_engine(f'postgresql://{usr}:{pswd}@{host}:25060/defaultdb')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()