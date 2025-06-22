from fastapi import FastAPI
from pydantic import BaseModel
from counselor import DynamicCollegeCounselorChatbot
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()
bot = DynamicCollegeCounselorChatbot()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = bot.chat(request.message, request.history)
        return {
            "response": response,
            "profile": bot.student_profile.model_dump(),
            "sufficient_info": bot.sufficient_info_collected
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/download-profile")
async def download_profile():
    try:
        file_path = bot.profile_filename
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="application/json", filename="student_profile.json")
        return {"error": "Profile not generated yet."}
    except Exception as e:
        return {"error": str(e)}

@app.post("/reset")
async def reset_counselor():
    try:
        bot.__init__()  # Reinitialize
        return {"status": "reset"}
    except Exception as e:
        return {"error": str(e)}
