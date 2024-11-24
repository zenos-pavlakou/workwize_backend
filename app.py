from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db_engine import SessionLocal

from routes.ai import router as ai_router
from routes.system import router as system_router
from pkgs.system import queries as system_queries
from pkgs.system import actions as system_actions
from pkgs.ai import pipeline
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://radbytes.org:5000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:3000",
        "http://206.189.114.61:5000",
        "https://radbytes.org",
        "https://radbytes.org:443",
        "https://www.radbytes.org",
        "https://www.radbytes.org:443",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(system_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
    # openai_api_key = os.environ["OPENAI_API_KEY"]
    # pipeline.run_pipeline(user_id=2, user_name="Zoe Carr", api_key=openai_api_key)
    # openai_api_key = os.environ["OPENAI_API_KEY"]
    # data = feedback_identifier.run(user_id=1, api_key=openai_api_key)
    # from pprint import pprint
    # pprint(data)
    #system_actions.plan_of_actions(1,"BOB",{1:"abc"},1,SessionLocal())
    #user_id: int,user_name: str,categorized_action_items: JSON,target_user_id:int, db: Session = Depends(get_db)
    #system_queries.get_personal_plan_of_actions(1,SessionLocal())
    # pprint(system_queries.get_user(1,SessionLocal()))