from fastapi import FastAPI
from pydantic import BaseModel
from counselor import DynamicCollegeCounselorChatbot
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import sqlite3
from datetime import datetime

# === Initialize FastAPI and Middleware ===
app = FastAPI()
bot = DynamicCollegeCounselorChatbot()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Database Setup ===
DB_NAME = "logs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            timestamp TEXT,
            message TEXT,
            response TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_to_db(endpoint: str, message: str, response: str, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (endpoint, timestamp, message, response, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        endpoint,
        datetime.now().isoformat(),
        message,
        response,
        status
    ))
    conn.commit()
    conn.close()

init_db()

# === Request Model ===
class ChatRequest(BaseModel):
    message: str
    history: list = []

# === Endpoints ===

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = bot.chat(request.message, request.history)
        log_to_db(
            endpoint="/chat",
            message=request.message,
            response=response,
            status="success"
        )
        return {
            "response": response,
            "profile": bot.student_profile.model_dump(),
            "sufficient_info": bot.sufficient_info_collected
        }
    except Exception as e:
        log_to_db("/chat", request.message, str(e), "error")
        return {"error": str(e)}

@app.get("/download-profile")
async def download_profile():
    try:
        file_path = bot.profile_filename
        if os.path.exists(file_path):
            log_to_db("/download-profile", "-", "Downloaded student_profile.json", "success")
            return FileResponse(file_path, media_type="application/json", filename="student_profile.json")
        log_to_db("/download-profile", "-", "Profile not found", "error")
        return {"error": "Profile not generated yet."}
    except Exception as e:
        log_to_db("/download-profile", "-", str(e), "error")
        return {"error": str(e)}

@app.post("/reset")
async def reset_counselor():
    try:
        bot.__init__()  # Reinitialize
        log_to_db("/reset", "-", "Bot reset", "success")
        return {"status": "reset"}
    except Exception as e:
        log_to_db("/reset", "-", str(e), "error")
        return {"error": str(e)}

@app.get("/logs")
async def get_logs():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100")
        logs = cursor.fetchall()
        conn.close()
        return {
            "logs": [
                {
                    "id": log[0],
                    "endpoint": log[1],
                    "timestamp": log[2],
                    "message": log[3],
                    "response": log[4],
                    "status": log[5]
                } for log in logs
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/profile")
async def get_profile():
    try:
        profile_data = bot.student_profile.model_dump()
        log_to_db("/profile", "-", "Fetched student profile", "success")
        return profile_data
    except Exception as e:
        log_to_db("/profile", "-", str(e), "error")
        return {"error": str(e)}
