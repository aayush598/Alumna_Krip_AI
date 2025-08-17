from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import json
import sqlite3
from datetime import datetime
import tempfile
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Import your existing modules (make sure these files exist)
try:
    from counselor import DynamicCollegeCounselorBot, DynamicStudentProfile
    from student_profile import DynamicStudentProfile  # Fallback import
    from college_database import get_college_database
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️  Creating mock classes for testing purposes")
    
    # Mock classes for testing when modules are missing
    class DynamicStudentProfile:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        
        def model_dump(self):
            return self.__dict__
    
    class DynamicCollegeCounselorBot:
        def __init__(self, api_key=None):
            self.name = "AI Counselor"
            self.student_profile = DynamicStudentProfile()
            self.sufficient_info_collected = False
            self.extraction_history = []
            self.conversation_stage = "greeting"
            self.message_count = 0
            self.recommendations_provided = False
        
        def chat(self, message, context):
            # Simple mock response
            responses = [
                "Thank you for sharing that information. Could you tell me more about your preferred field of study?",
                "That's great! What's your budget range for college fees?",
                "Based on your preferences, I can help you find suitable colleges. What location do you prefer?",
                "Excellent! With your scores and preferences, here are some recommendations I can provide."
            ]
            
            # Simulate info collection
            if len(self.extraction_history) >= 3:
                self.sufficient_info_collected = True
            
            response = responses[min(len(self.extraction_history), len(responses)-1)]
            self.extraction_history.append({"message": message, "response": response})
            
            return response
        
        def generate_personalized_recommendations(self):
            # Mock recommendations
            return [
                {
                    "name": "Indian Institute of Technology - Madras",
                    "location": "Chennai, Tamil Nadu",
                    "fees": 200000,
                    "match_score": 95.0,
                    "match_reasons": ["Excellent placement record", "Top tier institution", "Strong CS program"]
                },
                {
                    "name": "NIT Surathkal",
                    "location": "Mangalore, Karnataka", 
                    "fees": 150000,
                    "match_score": 90.0,
                    "match_reasons": ["Good placement record", "Within budget", "Preferred location"]
                },
                {
                    "name": "BMS College of Engineering",
                    "location": "Bangalore, Karnataka",
                    "fees": 400000,
                    "match_score": 85.0,
                    "match_reasons": ["Modern infrastructure", "Good industry connections", "CS specialization"]
                }
            ]
    
    def get_college_database():
        # Mock college database
        return [
            {
                "name": "Indian Institute of Technology - Madras",
                "location": "Chennai, Tamil Nadu",
                "type": "Engineering",
                "fees": 200000,
                "streams": ["Computer Science", "Mechanical", "Electrical", "Civil"]
            },
            {
                "name": "NIT Surathkal", 
                "location": "Mangalore, Karnataka",
                "type": "Engineering",
                "fees": 150000,
                "streams": ["Computer Science", "Electronics", "Mechanical"]
            }
        ]

# ==================== PYDANTIC MODELS ====================

class ChatMessage(BaseModel):
    message: str = Field(..., description="User's message to the counselor")
    session_id: Optional[str] = Field(None, description="Optional session ID for maintaining context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Counselor's response")
    session_id: str = Field(..., description="Session ID for this conversation")
    profile: Dict[str, Any] = Field(..., description="Current student profile data")
    sufficient_info: bool = Field(..., description="Whether enough info has been collected")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="College recommendations if available")

class SessionInfo(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    status: str = Field(..., description="Session status (active/completed)")
    message_count: int = Field(..., description="Number of messages in this session")

class ProfileUpdateRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to update")
    profile_data: Dict[str, Any] = Field(..., description="Profile data to update")

class RecommendationRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID (optional)")
    profile_data: Optional[Dict[str, Any]] = Field(None, description="Custom profile data for recommendations")
    max_results: int = Field(10, description="Maximum number of recommendations to return")

class CollegeFilter(BaseModel):
    stream: Optional[str] = Field(None, description="Preferred stream/course")
    location: Optional[str] = Field(None, description="Preferred location")
    max_fees: Optional[int] = Field(None, description="Maximum fees budget")
    college_type: Optional[str] = Field(None, description="Type of college (Engineering/Medical/University/Management)")

# ==================== FASTAPI APP SETUP ====================

app = FastAPI(
    title="Alumna Krip AI - College Counselor API",
    description="Intelligent college counseling API that provides personalized recommendations through conversational AI",
    version="1.0.0",
    contact={
        "name": "Aayush Gid",
        "email": "aayushgid598@gmail.com",
        "url": "https://github.com/aayush598"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== API KEY CONFIGURATION ====================

# Set your OpenAI API key here - replace with your actual key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
# ==================== DATABASE SETUP ====================

DB_NAME = "counselor_api.db"

def init_database():
    """Initialize SQLite database with required tables"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                status TEXT,
                message_count INTEGER DEFAULT 0,
                profile_data TEXT,
                sufficient_info BOOLEAN DEFAULT FALSE,
                conversation_stage TEXT DEFAULT 'greeting',
                extraction_history TEXT DEFAULT '[]',
                conversation_history TEXT DEFAULT '[]'
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                user_message TEXT,
                bot_response TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # API logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                timestamp TEXT,
                request_data TEXT,
                response_data TEXT,
                status_code INTEGER,
                error_message TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

def log_api_call(endpoint: str, request_data: str, response_data: str, status_code: int, error_message: str = None):
    """Log API calls to database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_logs (endpoint, timestamp, request_data, response_data, status_code, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            endpoint,
            datetime.now().isoformat(),
            request_data,
            response_data,
            status_code,
            error_message
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

# Initialize database on startup
init_database()

# ==================== SESSION MANAGEMENT ====================

active_sessions: Dict[str, DynamicCollegeCounselorBot] = {}

def get_or_create_session(session_id: str = None) -> tuple[str, DynamicCollegeCounselorBot]:
    if session_id and session_id in active_sessions:
        return session_id, active_sessions[session_id]
    
    # Check DB for session
    if session_id:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT profile_data, sufficient_info, conversation_stage, extraction_history, conversation_history 
                FROM sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                profile_data_json, sufficient_info, conversation_stage, extraction_history_json, conversation_history_json = row
                
                # Restore counselor from database
                counselor = DynamicCollegeCounselorBot(api_key=OPENAI_API_KEY)
                
                # Restore profile
                if profile_data_json:
                    profile_data = json.loads(profile_data_json)
                    counselor.student_profile = DynamicStudentProfile(**profile_data)
                
                # Restore other states
                counselor.sufficient_info_collected = bool(sufficient_info)
                counselor.conversation_stage = conversation_stage or "greeting"
                
                if extraction_history_json:
                    counselor.extraction_history = json.loads(extraction_history_json)
                
                if conversation_history_json:
                    counselor.conversation_history = json.loads(conversation_history_json)
                
                active_sessions[session_id] = counselor
                return session_id, counselor
        except Exception as e:
            print(f"Session fetch error: {e}")
    
    # Create new session
    new_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(active_sessions)}"
    
    try:
        counselor = DynamicCollegeCounselorBot(api_key=OPENAI_API_KEY)
        active_sessions[new_session_id] = counselor
    except Exception as e:
        print(f"Error creating counselor: {e}")
        # Fallback to mock counselor if real one fails
        counselor = DynamicCollegeCounselorBot()
        active_sessions[new_session_id] = counselor
    
    # Save session to database
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, created_at, updated_at, status, profile_data, conversation_stage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_session_id,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            "active",
            json.dumps({}),
            "greeting"
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Session creation error: {e}")
    
    return new_session_id, counselor

def update_session_in_db(session_id: str, counselor: DynamicCollegeCounselorBot):
    """Update session data in database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Prepare data for storage
        profile_data = json.dumps(counselor.student_profile.model_dump())
        extraction_history = json.dumps(counselor.extraction_history)
        
        # Store conversation history (limit to recent messages to prevent excessive storage)
        recent_conversation = counselor.conversation_history[-20:] if hasattr(counselor, 'conversation_history') else []
        conversation_history = json.dumps(recent_conversation)
        
        cursor.execute("""
            UPDATE sessions 
            SET updated_at = ?, profile_data = ?, sufficient_info = ?, conversation_stage = ?, 
                extraction_history = ?, conversation_history = ?
            WHERE session_id = ?
        """, (
            datetime.now().isoformat(),
            profile_data,
            counselor.sufficient_info_collected,
            getattr(counselor, 'conversation_stage', 'greeting'),
            extraction_history,
            conversation_history,
            session_id
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Session update error: {e}")

# ==================== API ENDPOINTS ====================

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to Alumna Krip AI - College Counselor API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat - Start or continue a counseling conversation",
            "recommendations": "/recommendations - Get college recommendations", 
            "profile": "/profile/{session_id} - Get student profile",
            "sessions": "/sessions - List all sessions",
            "colleges": "/colleges - Get college database"
        },
        "documentation": "/docs"
    }

@app.post("/chat", response_model=ChatResponse, tags=["Counseling"])
async def chat_with_counselor(request: ChatMessage, background_tasks: BackgroundTasks):
    """
    Main chat endpoint for counseling conversation
    """
    try:
        # Get or create session
        session_id, counselor = get_or_create_session(request.session_id)
        
        # Process the message using the actual counselor logic
        response = counselor.chat(request.message, [])
        
        # Update sufficient info flag based on conversation stage
        if hasattr(counselor, 'conversation_stage'):
            if counselor.conversation_stage == "ready_for_recommendations":
                counselor.sufficient_info_collected = True
        
        # Get recommendations if sufficient info is collected
        recommendations = None
        if counselor.sufficient_info_collected or (hasattr(counselor, 'conversation_stage') and counselor.conversation_stage == "ready_for_recommendations"):
            try:
                recommendations = counselor.generate_personalized_recommendations()
            except Exception as e:
                print(f"Recommendation generation error: {e}")
                recommendations = None
        
        # Prepare response
        chat_response = ChatResponse(
            response=response,
            session_id=session_id,
            profile=counselor.student_profile.model_dump(),
            sufficient_info=counselor.sufficient_info_collected,
            recommendations=recommendations
        )
        
        # Background tasks
        background_tasks.add_task(update_session_in_db, session_id, counselor)
        background_tasks.add_task(log_api_call, "/chat", json.dumps(request.dict()), json.dumps(chat_response.dict()), 200)
        
        # Save message to database
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (session_id, timestamp, user_message, bot_response)
                VALUES (?, ?, ?, ?)
            """, (session_id, datetime.now().isoformat(), request.message, response))
            
            # Update message count
            cursor.execute("""
                UPDATE sessions SET message_count = message_count + 1 WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Message logging error: {e}")
        
        return chat_response
        
    except Exception as e:
        log_api_call("/chat", json.dumps(request.dict()), str(e), 500, str(e))
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.post("/recommendations", tags=["Recommendations"])
async def get_recommendations(request: RecommendationRequest):
    """
    Get college recommendations based on profile data
    """
    try:
        counselor = None
        
        if request.session_id and request.session_id in active_sessions:
            counselor = active_sessions[request.session_id]
        elif request.profile_data:
            # Create temporary counselor with provided profile data
            try:
                counselor = DynamicCollegeCounselorBot(api_key=OPENAI_API_KEY)
                counselor.student_profile = DynamicStudentProfile(**request.profile_data)
                counselor.sufficient_info_collected = True
            except Exception as e:
                print(f"Error creating counselor for recommendations: {e}")
                # Fallback to mock counselor
                counselor = DynamicCollegeCounselorBot()
                counselor.student_profile = DynamicStudentProfile(**request.profile_data)
                counselor.sufficient_info_collected = True
        else:
            raise HTTPException(status_code=400, detail="Either session_id or profile_data must be provided")
        
        recommendations = counselor.generate_personalized_recommendations()
        
        # Limit results
        limited_recommendations = recommendations[:request.max_results] if recommendations else []
        
        return {
            "recommendations": limited_recommendations,
            "total_found": len(recommendations) if recommendations else 0,
            "returned": len(limited_recommendations),
            "profile_used": counselor.student_profile.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@app.get("/profile/{session_id}", tags=["Profile"])
async def get_student_profile(session_id: str):
    """
    Get student profile for a specific session
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    counselor = active_sessions[session_id]
    return {
        "session_id": session_id,
        "profile": counselor.student_profile.model_dump(),
        "sufficient_info": counselor.sufficient_info_collected,
        "extraction_history": counselor.extraction_history,
        "conversation_stage": getattr(counselor, 'conversation_stage', 'unknown'),
        "message_count": getattr(counselor, 'message_count', 0)
    }

@app.put("/profile/{session_id}", tags=["Profile"])
async def update_student_profile(session_id: str, request: ProfileUpdateRequest):
    """
    Update student profile data for a session
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        counselor = active_sessions[session_id]
        
        # Update profile with provided data
        current_profile = counselor.student_profile.model_dump()
        current_profile.update(request.profile_data)
        
        counselor.student_profile = DynamicStudentProfile(**current_profile)
        
        # Update in database
        update_session_in_db(session_id, counselor)
        
        return {
            "message": "Profile updated successfully",
            "session_id": session_id,
            "updated_profile": counselor.student_profile.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update error: {str(e)}")

@app.get("/sessions", response_model=List[SessionInfo], tags=["Session Management"])
async def list_sessions():
    """
    List all active and stored sessions
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, created_at, status, message_count
            FROM sessions
            ORDER BY created_at DESC
        """)
        sessions = cursor.fetchall()
        conn.close()
        
        session_list = []
        for session in sessions:
            session_info = SessionInfo(
                session_id=session[0],
                created_at=session[1],
                status="active" if session[0] in active_sessions else session[2],
                message_count=session[3]
            )
            session_list.append(session_info)
        
        return session_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session listing error: {str(e)}")

@app.delete("/sessions/{session_id}", tags=["Session Management"])
async def delete_session(session_id: str):
    """
    Delete a specific session
    """
    try:
        # Remove from active sessions
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        # Update status in database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions SET status = 'deleted', updated_at = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        conn.commit()
        conn.close()
        
        return {"message": f"Session {session_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session deletion error: {str(e)}")

@app.get("/colleges", tags=["College Database"])
async def get_colleges(
    stream: Optional[str] = None,
    location: Optional[str] = None, 
    max_fees: Optional[int] = None,
    college_type: Optional[str] = None
):
    """
    Get college database with optional filtering
    """
    try:
        colleges = get_college_database()
        
        # Apply filters if provided
        if any([stream, location, max_fees, college_type]):
            filtered_colleges = []
            for college in colleges:
                include = True
                
                if stream:
                    if not any(stream.lower() in s.lower() for s in college.get('streams', [])):
                        include = False
                
                if location and include:
                    if location.lower() not in college.get('location', '').lower():
                        include = False
                
                if max_fees and include:
                    if college.get('fees', 0) > max_fees:
                        include = False
                
                if college_type and include:
                    if college_type.lower() != college.get('type', '').lower():
                        include = False
                
                if include:
                    filtered_colleges.append(college)
            
            colleges = filtered_colleges
        
        return {
            "colleges": colleges,
            "total_count": len(colleges)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"College database error: {str(e)}")

@app.get("/analytics", tags=["Analytics"])
async def get_analytics():
    """
    Get basic analytics about API usage
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Active sessions
        active_session_count = len(active_sessions)
        
        # Total messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # Sessions with sufficient info
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE sufficient_info = TRUE")
        completed_sessions = cursor.fetchone()[0]
        
        # API calls by endpoint
        cursor.execute("""
            SELECT endpoint, COUNT(*) as count
            FROM api_logs
            WHERE endpoint IS NOT NULL
            GROUP BY endpoint
            ORDER BY count DESC
        """)
        endpoint_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_session_count,
            "total_messages": total_messages,
            "completed_sessions": completed_sessions,
            "completion_rate": f"{(completed_sessions/total_sessions*100):.1f}%" if total_sessions > 0 else "0%",
            "endpoint_usage": [{"endpoint": ep[0], "calls": ep[1]} for ep in endpoint_stats]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

# ==================== STARTUP/SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize API on startup"""
    print("🚀 Alumna Krip AI - College Counselor API is starting up...")
    print(f"📊 Database: {DB_NAME}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    
    # Test OpenAI API key
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  Warning: OpenAI API key not properly configured - using mock responses")
    
    print("✅ API is ready to serve requests!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 API is shutting down...")
    # Save any pending session data
    for session_id, counselor in active_sessions.items():
        update_session_in_db(session_id, counselor)
    print("✅ Cleanup completed!")

# ==================== MAIN RUNNER ====================

if __name__ == "__main__":
    print("Starting Alumna Krip AI - College Counselor API...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )