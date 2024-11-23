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
from typing import List, Set
import json

from pkgs.ai.chatbot import Chatbot
from db_engine import engine, get_db

from pydantic_models import ChatMessage as PydanticChatMessage

router = APIRouter()
chatbot = Chatbot()

@router.post("/chat")
async def chat(chat_message: PydanticChatMessage, db: Session = Depends(get_db)):
    user_id = chat_message.user_id
    message = chat_message.message
    return StreamingResponse(
        chatbot.chat_stream(user_id, message),
        media_type='text/event-stream'
    )