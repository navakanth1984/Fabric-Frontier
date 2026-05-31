import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import requests

# Load environment variables
env_path = Path("c:/Users/navka/navakanth001/.env")
load_dotenv(dotenv_path=env_path)

import sqlite3
from datetime import datetime

# Database Setup for Intent Tracking (CRM Step 5)
DB_PATH = Path("c:/Users/navka/navakanth001/nthdimensionacademy/intent_tracking.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions
                 (timestamp TEXT, role TEXT, message TEXT, intent_tags TEXT)''')
    conn.commit()
    conn.close()

init_db()

def log_interaction(role, message, intent_tags=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO interactions VALUES (?, ?, ?, ?)",
              (datetime.now().isoformat(), role, message, intent_tags))
    conn.commit()
    conn.close()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clients
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# Load Agent Persona and Curriculum References (DP-600 & DP-700)
persona_path = Path("c:/Users/navka/navakanth001/nthdimensionacademy/ACADEMY_AGENT.md")
dp700_path = Path("c:/Users/navka/navakanth001/nthdimensionacademy/DP700_LEARNING_PATH.md")
dp600_path = Path("c:/Users/navka/navakanth001/nthdimensionacademy/DP600_LEARNING_PATH.md")

with open(persona_path, "r", encoding="utf-8") as f:
    AGENT_PERSONA = f.read()

if dp700_path.exists():
    with open(dp700_path, "r", encoding="utf-8") as f:
        dp700_content = f.read()
    AGENT_PERSONA += f"\n\n## DP-700 Curriculum Reference (Learning Path):\n{dp700_content}"

if dp600_path.exists():
    with open(dp600_path, "r", encoding="utf-8") as f:
        dp600_content = f.read()
    AGENT_PERSONA += f"\n\n## DP-600 Curriculum Reference (Learning Path):\n{dp600_content}"

class ChatRequest(BaseModel):
    message: str
    history: list = []

class VoiceRequest(BaseModel):
    text: str
    target_language: str = "te-IN" # Default to Telugu

@app.post("/api/chat")
async def chat_with_guide(request: ChatRequest):
    try:
        log_interaction("user", request.message)
        messages = [
            {"role": "system", "content": AGENT_PERSONA},
        ]
        # Add history if provided
        messages.extend(request.history)
        messages.append({"role": "user", "content": request.message})

        completion = nvidia_client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=messages,
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
        )

        response_text = completion.choices[0].message.content
        log_interaction("assistant", response_text)
        return {"response": response_text}
    except Exception as e:
        print(f"ERROR in chat_with_guide: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice")
async def generate_voice(request: VoiceRequest):
    """Integrate Sarvam AI for Multilingual TTS"""
    try:
        url = "https://api.sarvam.ai/text-to-speech"
        payload = {
            "inputs": [request.text],
            "target_language_code": request.target_language,
            "speaker": "meera", # High-quality Indian female voice
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v1"
        }
        headers = {
            "api-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
