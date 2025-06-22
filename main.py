from fastapi import FastAPI, Request
from pydantic import BaseModel
from counselor import DynamicCollegeCounselorChatbot
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
bot = DynamicCollegeCounselorChatbot()

# Allow CORS (if you're using a frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        bot_response = bot.chat(request.message, request.history)
        return {
            "response": bot_response,
            "profile": bot.student_profile.model_dump(),
            "sufficient_info": bot.sufficient_info_collected
        }
    except Exception as e:
        return {"error": str(e)}
