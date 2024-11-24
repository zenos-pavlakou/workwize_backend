import os
from pkgs.ai.chatbot import Chatbot
from db_models import Chat as DbChat
from db_engine import engine, get_db
from pydantic_models import ChatMessage as PydanticChatMessage
from pydantic_models import RunPipelineRequest 
from pkgs.system import queries as system_queries 
from pkgs.ai import pipeline 
from threading import Thread
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from datetime import datetime
from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
router = APIRouter()
chatbot = Chatbot()


@router.post("/chat")
async def chat(chat_message: PydanticChatMessage, db: Session = Depends(get_db)):
    try:
        user_id = chat_message.user_id
        message = chat_message.message

        # Log incoming message for debugging
        print(f"Received message: {message} from user: {user_id}")

        try:
            # Create and store user message
            chat_message_db = DbChat(
                user_id=user_id,
                message=message,
                is_ai=False
            )
            db.add(chat_message_db)
            db.commit()

            # Get the stream from chatbot
            original_stream = chatbot.chat_stream(user_id, message)

            # Return streaming response
            return StreamingResponse(
                stream_and_store(user_id, message, db, original_stream),
                media_type='text/event-stream'
            )

        except SQLAlchemyError as db_error:
            print(f"Database error: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while storing message"
            )

    except Exception as e:
        print(f"General error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


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
            yield f"data: {chunk}\n\n"

            # Store content for database
            if chunk.strip():
                content = json.loads(chunk).get('content', '')
                if content.strip():  # Only append non-empty content
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
        print(f"Error in stream_and_store: {str(e)}")
        db.rollback()
        error_message = json.dumps({"content": f"Error: {str(e)}"})
        yield f"data: {error_message}\n\n"

    except Exception as e:
        print(f"Error in stream_and_store: {str(e)}")
        error_message = json.dumps({"content": f"Error: {str(e)}"})
        yield f"data: {error_message}\n\n"
    
def _run_pipeline(user_id: int, user_name: str):
    api_key = os.environ["OPENAI_API_KEY"]
    pipeline.run_pipeline(user_id, user_name, api_key)

@router.post("/run-pipeline")
async def run_pipeline(request_data: RunPipelineRequest,db: Session = Depends(get_db)):
    user=system_queries.get_user(request_data.user_id,db)
    thread = Thread(target=_run_pipeline, args=(request_data.user_id, user.name))
    thread.start()
    return 200
    
