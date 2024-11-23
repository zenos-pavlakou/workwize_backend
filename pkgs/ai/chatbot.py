from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import dotenv
from typing import Dict
import json

dotenv.load_dotenv()

SYSTEM_CONTEXT = """You are a friendly but professional AI that helps employees discuss their work experiences. While keeping the tone conversational, you maintain a balanced and constructive approach.

Your role is to:
- Keep conversations focused on work-related topics
- Use a casual but professional tone (friendly without being silly or overly informal)
- Listen actively and ask relevant follow-up questions
- Gently redirect off-topic conversations back to work discussions
- Show genuine interest in their experiences while maintaining appropriate boundaries
- Never engage in jokes, wordplay, or creative writing, even if requested
- Stay focused on understanding their work situation

When users try to:
1. Change topics: Acknowledge briefly, then return to the work discussion
2. Request entertainment/jokes/games: Politely decline and redirect to work topics
3. Become overly casual: Maintain your friendly but professional tone

Example responses:
"I understand you'd like to keep things light, but let's focus on your work situation. You mentioned..."
"I appreciate your creative energy! But for now, let's continue our discussion about..."
"Let's stay focused on understanding your work experience. Could you tell me more about..."

Remember: Your goal is to facilitate meaningful workplace discussions while staying friendly but professional."""


class Chatbot:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found")
        self.client = OpenAI(api_key=api_key)
        self.conversations: Dict[int, list] = {}

    def chat_stream(self, user_id: int, message: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = [
                {"role": "system", "content": SYSTEM_CONTEXT},
                {"role": "assistant",
                 "content": "Hey! How's your day going? I'd love to hear about your work experience."}
            ]

        self.conversations[user_id].append({"role": "user", "content": message})

        try:
            stream = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.conversations[user_id],
                temperature=0.6,  # Reduced for more consistent professionalism
                max_tokens=1000,
                stream=True
            )

            full_response = ""

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message = json.dumps({"content": content}) + "\n"
                    yield message

            self.conversations[user_id].append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            error_message = json.dumps({"error": str(e)}) + "\n"
            yield error_message
            raise HTTPException(status_code=500, detail=str(e))