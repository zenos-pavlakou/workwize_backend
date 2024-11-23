import json
import os
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Set, AsyncGenerator

from pkgs.ai.chatbot import Chatbot
from db_models import Chat as DbChat
from db_engine import engine, get_db
from pydantic_models import ChatMessage as PydanticChatMessage
from pydantic_models import RunPipelineRequest 
from pkgs.system import queries as system_queries 
from pkgs.ai import pipeline 
from threading import Thread


router = APIRouter()
chatbot = Chatbot()


async def stream_and_store(
        user_id: int,
        message: str,
        db: Session,
        original_stream
) -> AsyncGenerator[str, None]:
    chunks = []

    try:
        for chunk in original_stream:
            # Pass through original chunk to client
            yield chunk

            # Store content for database
            if chunk.strip():
                content = json.loads(chunk).get('content', '')
                chunks.append(content)

        # After streaming completes, save the complete message
        complete_message = "".join(chunks)
        ai_message = DbChat(
            user_id=user_id,
            message=complete_message,
            is_ai=True
        )
        db.add(ai_message)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


@router.post("/chat")
async def chat(chat_message: PydanticChatMessage, db: Session = Depends(get_db)):
    user_id = chat_message.user_id
    message = chat_message.message

    chat_message = DbChat(user_id=user_id, message=message, is_ai=False)
    db.add(chat_message)
    try:
        db.commit()
        original_stream = chatbot.chat_stream(user_id, message)
        return StreamingResponse(
            stream_and_store(user_id, message, db, original_stream),
            media_type='text/event-stream'
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
def _run_pipeline(user_id: int, user_name: str):
    api_key = os.environ["OPENAI_API_KEY"]
    pipeline.run_pipeline(user_id, user_name, api_key)

@router.post("/run-pipeline")
async def run_pipeline(request_data: RunPipelineRequest,db: Session = Depends(get_db)):
    user=system_queries.get_user(request_data.user_id,db)
    thread = Thread(target=_run_pipeline, args=(request_data.user_id, user.name))
    thread.start()
    return 200
    
