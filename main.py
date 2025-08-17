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

# ==================== COUNSELOR CLASSES ====================

class StudentConversation(BaseModel):
    """Simple conversation tracker without rigid field extraction"""
    conversation_id: str = Field(default_factory=lambda: f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    student_context: Dict[str, Any] = Field(default_factory=dict, description="Flexible context about the student")
    conversation_flow: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    insights_discovered: List[str] = Field(default_factory=list, description="Key insights about the student")
    recommendations_given: List[Dict[str, Any]] = Field(default_factory=list, description="Recommendations provided")
    conversation_stage: str = Field(default="introduction", description="Current conversation stage")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())


class DynamicStudentProfile(BaseModel):
    """Dynamic student profile that can handle any fields"""
    name: Optional[str] = None
    age: Optional[int] = None
    academic_performance: Dict[str, Any] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    preferred_fields: List[str] = Field(default_factory=list)
    budget: Optional[int] = None
    location_preference: Optional[str] = None
    career_goals: List[str] = Field(default_factory=list)
    extracurricular: List[str] = Field(default_factory=list)
    family_background: Dict[str, Any] = Field(default_factory=dict)
    scores: Dict[str, Any] = Field(default_factory=dict)
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class DynamicCollegeCounselorBot:
    """Enhanced counselor class for FastAPI integration"""

    def __init__(self, api_key=None, name="Lauren"):
        self.name = name
        self.model = "gpt-4o"
        
        # Initialize OpenAI client if API key is provided
        if api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.use_openai = True
                print("✅ OpenAI client initialized successfully")
            except ImportError:
                print("⚠️  OpenAI library not installed, using mock responses")
                self.use_openai = False
            except Exception as e:
                print(f"⚠️  OpenAI initialization failed: {e}, using mock responses")
                self.use_openai = False
        else:
            self.use_openai = False
            print("⚠️  No API key provided, using mock responses")
        
        # Initialize conversation tracking
        self.conversation = StudentConversation()
        self.student_profile = DynamicStudentProfile()
        self.message_count = 0
        self.sufficient_info_collected = False
        self.extraction_history = []
        self.conversation_stage = "greeting"
        self.recommendations_provided = False
        self.conversation_history = []
        
        # Initialize knowledge bases
        self.college_database = self._initialize_comprehensive_college_database()
        self.career_insights = self._initialize_career_insights()

    def _initialize_comprehensive_college_database(self):
        """Initialize comprehensive college database"""
        return {
            "premier_engineering": [
                {
                    "name": "Indian Institute of Technology - Bombay",
                    "location": "Mumbai, Maharashtra",
                    "established": "1958",
                    "highlights": ["Top-ranked engineering institute", "Excellent placement record", "Strong alumni network", "World-class research facilities"],
                    "programs": ["B.Tech", "M.Tech", "Ph.D", "Dual Degree"],
                    "specialties": ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Aerospace Engineering"],
                    "admission": "JEE Advanced",
                    "fees": 250000,
                    "streams": ["Computer Science", "Electrical", "Mechanical", "Aerospace", "Chemical"],
                    "type": "Engineering",
                    "placement_stats": "Average CTC: ₹15-20 lakhs, Highest: ₹1+ crore"
                },
                {
                    "name": "Indian Institute of Technology - Delhi",
                    "location": "New Delhi",
                    "established": "1961",
                    "highlights": ["Premier technical institute", "Strong industry connections", "Research excellence", "Beautiful campus"],
                    "programs": ["B.Tech", "M.Tech", "MBA", "Ph.D"],
                    "specialties": ["Computer Science", "Engineering Physics", "Chemical Engineering", "Mathematics & Computing"],
                    "admission": "JEE Advanced",
                    "fees": 250000,
                    "streams": ["Computer Science", "Engineering Physics", "Chemical", "Mathematics"],
                    "type": "Engineering"
                },
                {
                    "name": "BITS Pilani",
                    "location": "Pilani, Rajasthan",
                    "established": "1964",
                    "highlights": ["Premier private engineering institute", "Industry-integrated programs", "Flexible curriculum", "Strong entrepreneurship culture"],
                    "programs": ["B.E.", "M.Sc.", "MBA", "Ph.D", "Dual Degree"],
                    "specialties": ["Computer Science", "Electronics", "Chemical Engineering", "Pharmacy"],
                    "admission": "BITSAT",
                    "fees": 450000,
                    "streams": ["Computer Science", "Electronics", "Chemical", "Pharmacy"],
                    "type": "Engineering"
                },
                {
                    "name": "NIT Surathkal",
                    "location": "Mangalore, Karnataka",
                    "highlights": ["Top NIT", "Excellent placement record", "Strong technical culture", "Beautiful coastal campus"],
                    "programs": ["B.Tech", "M.Tech", "MBA", "Ph.D"],
                    "admission": "JEE Main",
                    "fees": 150000,
                    "streams": ["Computer Science", "Electronics", "Mechanical", "Civil"],
                    "type": "Engineering"
                },
                {
                    "name": "BMS College of Engineering",
                    "location": "Bangalore, Karnataka",
                    "highlights": ["Autonomous college", "Strong industry connections", "Modern infrastructure", "CS specialization"],
                    "programs": ["B.E.", "M.Tech"],
                    "admission": "COMEDK/Management",
                    "fees": 400000,
                    "streams": ["Computer Science", "Information Science", "Electronics", "Mechanical"],
                    "type": "Engineering"
                }
            ],
            "medical_colleges": [
                {
                    "name": "All India Institute of Medical Sciences - Delhi",
                    "location": "New Delhi",
                    "highlights": ["Premier medical institute", "Excellent clinical exposure", "Subsidized education", "Top-notch faculty"],
                    "programs": ["MBBS", "MD/MS", "Ph.D", "Nursing"],
                    "admission": "NEET",
                    "fees": 5000,
                    "streams": ["Medicine", "Surgery", "Pediatrics", "Radiology"],
                    "type": "Medical"
                }
            ],
            "business_schools": [
                {
                    "name": "Indian Institute of Management - Ahmedabad",
                    "location": "Ahmedabad, Gujarat",
                    "highlights": ["Top MBA school in India", "Excellent faculty", "Strong alumni network", "Case-study method"],
                    "programs": ["PGP (MBA)", "Executive MBA", "Ph.D"],
                    "admission": "CAT + WAT + PI",
                    "fees": 2500000,
                    "streams": ["General Management", "Finance", "Marketing", "Operations"],
                    "type": "Management"
                }
            ]
        }

    def _initialize_career_insights(self):
        """Initialize career insights database"""
        return {
            "high_growth_careers": {
                "technology": {
                    "Software Engineer": {
                        "description": "Design and develop software applications",
                        "skills_required": ["Programming", "Problem-solving", "System design"],
                        "education_path": ["B.Tech Computer Science", "BCA + MCA", "Self-learning + certifications"],
                        "salary_range": "₹4-50 lakhs per year",
                        "growth_prospects": "Excellent - High demand, startup opportunities, global market"
                    },
                    "Data Scientist": {
                        "description": "Analyze complex data to derive business insights",
                        "skills_required": ["Statistics", "Machine Learning", "Python/R", "SQL"],
                        "education_path": ["B.Tech + Data Science certification", "Statistics/Math degree + upskilling"],
                        "salary_range": "₹6-40 lakhs per year",
                        "growth_prospects": "Very High - Every industry needs data insights"
                    }
                },
                "healthcare": {
                    "Doctor": {
                        "description": "Diagnose and treat medical conditions",
                        "skills_required": ["Medical knowledge", "Empathy", "Decision-making", "Communication"],
                        "education_path": ["MBBS + MD/MS specialization"],
                        "salary_range": "₹6-50+ lakhs per year",
                        "growth_prospects": "Stable - Always in demand"
                    }
                },
                "business": {
                    "Management Consultant": {
                        "description": "Help organizations solve complex business problems",
                        "skills_required": ["Analytical thinking", "Communication", "Industry knowledge"],
                        "education_path": ["Any graduation + MBA from top school"],
                        "salary_range": "₹8-40 lakhs per year",
                        "growth_prospects": "Excellent - High learning curve, global opportunities"
                    }
                }
            }
        }

    def _get_dynamic_system_prompt(self):
        """Generate dynamic system prompt based on conversation stage"""
        base_personality = f"""
        You are {self.name}, an expert AI college counselor with deep knowledge of Indian and global education systems. 
        You have years of experience helping students navigate their educational journey.

        Your Core Qualities:
        - Warm, encouraging, and genuinely interested in each student's success
        - Highly knowledgeable about colleges, careers, and education trends
        - Patient listener who asks thoughtful follow-up questions
        - Provides specific, actionable advice rather than generic responses
        - Shares relevant insights and stories to help students understand options
        - Balances dreams with practical realities

        Current conversation stage: {self.conversation_stage}
        Messages exchanged: {self.message_count}
        
        Based on the conversation, provide helpful, informative responses that guide the student toward making informed decisions about their education and career.
        """
        
        return base_personality

    def _update_conversation_stage(self, user_message):
        """Update conversation stage based on content and message count"""
        message_lower = user_message.lower()
        
        if self.message_count <= 2:
            self.conversation_stage = "greeting"
        elif self.message_count <= 5:
            self.conversation_stage = "information_gathering"
        elif any(word in message_lower for word in ["recommend", "suggest", "what should i", "help me choose"]):
            self.conversation_stage = "recommendation"
        elif self.message_count > 5:
            self.conversation_stage = "detailed_guidance"

    def _extract_student_information(self, user_message):
        """Extract and update student information from conversation"""
        message_lower = user_message.lower()
        updates = {}
        
        # Extract interests
        tech_keywords = ["computer", "programming", "software", "coding", "tech", "it"]
        if any(word in message_lower for word in tech_keywords):
            if "Computer Science" not in self.student_profile.preferred_fields:
                self.student_profile.preferred_fields.append("Computer Science")
                updates["tech_interest"] = True
        
        medical_keywords = ["doctor", "medical", "medicine", "healthcare", "mbbs"]
        if any(word in message_lower for word in medical_keywords):
            if "Medicine" not in self.student_profile.preferred_fields:
                self.student_profile.preferred_fields.append("Medicine")
                updates["medical_interest"] = True
        
        business_keywords = ["business", "management", "mba", "finance", "marketing"]
        if any(word in message_lower for word in business_keywords):
            if "Business" not in self.student_profile.preferred_fields:
                self.student_profile.preferred_fields.append("Business")
                updates["business_interest"] = True
        
        # Extract scores and academic info
        score_patterns = ["scored", "marks", "percentage", "cgpa", "gpa", "jee", "neet"]
        if any(pattern in message_lower for pattern in score_patterns):
            updates["academic_info_provided"] = True
        
        # Extract budget information
        budget_keywords = ["budget", "afford", "fees", "cost", "expensive", "cheap"]
        if any(word in message_lower for word in budget_keywords):
            updates["budget_discussed"] = True
        
        # Update additional context
        for key, value in updates.items():
            self.student_profile.additional_info[key] = value
        
        # Check if sufficient info is collected
        if len(self.student_profile.preferred_fields) > 0 and len(self.student_profile.additional_info) >= 2:
            self.sufficient_info_collected = True

    def chat(self, message, context):
        """Main chat function with OpenAI integration"""
        self.message_count += 1
        
        # Update conversation stage and extract information
        self._update_conversation_stage(message)
        self._extract_student_information(message)
        
        # Add to extraction history
        self.extraction_history.append({
            "message": message,
            "stage": self.conversation_stage,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if self.use_openai:
            try:
                # Prepare messages for OpenAI
                system_prompt = self._get_dynamic_system_prompt()
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
                
                # Add recent conversation context (last 4 exchanges)
                recent_history = self.conversation_history[-8:]  # Last 4 exchanges (user + assistant)
                for i in range(0, len(recent_history)-1, 2):  # Skip current message
                    if i+1 < len(recent_history):
                        messages.insert(-1, {"role": "user", "content": recent_history[i]["content"]})
                        messages.insert(-1, {"role": "assistant", "content": recent_history[i+1]["content"]})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                    frequency_penalty=0.3,
                    presence_penalty=0.2
                )
                
                assistant_response = response.choices[0].message.content
                
            except Exception as e:
                print(f"OpenAI API error: {e}")
                assistant_response = self._get_fallback_response(message)
        else:
            assistant_response = self._get_fallback_response(message)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return assistant_response

    def _get_fallback_response(self, message):
        """Provide intelligent fallback responses when OpenAI is not available"""
        message_lower = message.lower()
        
        if self.message_count == 1:
            return f"Hello! I'm {self.name}, your AI college counselor. I'm here to help you navigate your educational journey and find the best college options for your goals. Could you tell me a bit about yourself - what are you currently studying and what fields interest you most?"
        
        # Handle specific queries
        if any(word in message_lower for word in ["engineering", "iit", "jee", "computer science"]):
            return """Great choice! Engineering offers excellent career prospects. Some top options include:

🏆 **IITs** - Premier institutes with world-class education (Admission: JEE Advanced)
🎯 **NITs** - Excellent government institutes across India (Admission: JEE Main)  
⭐ **BITS Pilani** - Top private institute with industry focus (Admission: BITSAT)
🏫 **State colleges** - Good quality education at affordable fees

Computer Science is particularly hot right now with amazing placement opportunities. What's your current academic background? Are you preparing for JEE or any other entrance exams?"""

        elif any(word in message_lower for word in ["medical", "doctor", "neet", "mbbs"]):
            return """Medicine is a noble and rewarding career path! Here's what you should know:

🏥 **AIIMS** - Premier medical institutes with highly subsidized fees
🎓 **Government Medical Colleges** - Affordable with excellent clinical exposure
🏫 **Private Medical Colleges** - Good infrastructure but higher fees (₹50L - ₹1.5Cr)

Key points:
- NEET is mandatory for all medical admissions
- Start preparation early - very competitive field
- Consider specialization options after MBBS
- Alternative paths: BDS, AYUSH, Allied Health Sciences

What's your current academic performance? Have you started NEET preparation?"""

        elif any(word in message_lower for word in ["mba", "management", "business", "cat"]):
            return """Business education opens doors to diverse career opportunities!

🎯 **IIMs** - Top business schools with excellent ROI (Admission: CAT)
⭐ **ISB, XLRI, FMS** - Premier institutes with strong placements  
📈 **Sectoral MBAs** - Healthcare, Rural, Family Business specializations

Career paths:
- Management Consulting (₹15-40L starting)
- Investment Banking & Finance  
- Product Management in Tech
- General Management roles

Most MBA programs prefer 2-3 years work experience. Are you currently working or planning to work before MBA? What business areas interest you most?"""

        elif any(word in message_lower for word in ["confused", "help", "don't know", "unsure"]):
            return """It's completely normal to feel confused about career choices! Let's explore your options systematically.

Let me ask you a few questions to better understand your interests:

🤔 **Academic Performance**: How are your current grades? Which subjects do you enjoy most?
🎯 **Interests**: What activities make you lose track of time? 
💡 **Career Vision**: Where do you see yourself in 10 years?
💰 **Practical Considerations**: Any budget constraints or location preferences?
👨‍👩‍👧‍👦 **Family Input**: What does your family suggest?

Based on your responses, I can provide personalized recommendations. What would you like to share first?"""

        else:
            return """Thank you for sharing that! I'm learning about your preferences and goals.

Based on our conversation so far, I can see you're exploring your options thoughtfully. Here are some areas we could discuss further:

📚 **Academic Paths**: Engineering, Medical, Business, Liberal Arts, Sciences
🌍 **Study Locations**: India vs International options  
💼 **Career Prospects**: Emerging fields vs Traditional stable careers
💰 **Financial Planning**: Education costs, scholarships, loans

What specific aspect would you like to dive deeper into? I'm here to provide detailed insights to help you make informed decisions!"""

    def generate_personalized_recommendations(self):
        """Generate recommendations based on student profile"""
        recommendations = []
        
        # Get all colleges from database
        all_colleges = []
        for category in self.college_database.values():
            all_colleges.extend(category)
        
        # Filter and score colleges based on student preferences
        for college in all_colleges:
            score = 0
            reasons = []
            
            # Check field alignment
            if self.student_profile.preferred_fields:
                college_streams = college.get('streams', [])
                field_match = any(
                    any(pref.lower() in stream.lower() for stream in college_streams)
                    for pref in self.student_profile.preferred_fields
                )
                if field_match:
                    score += 40
                    reasons.append(f"Offers programs in {', '.join(self.student_profile.preferred_fields)}")
            
            # Budget consideration
            if self.student_profile.budget:
                college_fees = college.get('fees', 0)
                if college_fees <= self.student_profile.budget:
                    score += 30
                    reasons.append("Within budget range")
                elif college_fees <= self.student_profile.budget * 1.2:  # 20% over budget
                    score += 15
                    reasons.append("Slightly above budget but manageable")
            
            # Location preference
            if self.student_profile.location_preference:
                if self.student_profile.location_preference.lower() in college.get('location', '').lower():
                    score += 20
                    reasons.append("Preferred location")
            
            # Add base score for quality (based on highlights)
            score += len(college.get('highlights', [])) * 2
            
            if score > 20:  # Only include colleges with reasonable scores
                recommendations.append({
                    "name": college['name'],
                    "location": college['location'],
                    "fees": college.get('fees', 0),
                    "match_score": min(score, 100.0),
                    "match_reasons": reasons or ["Good overall fit based on your profile"],
                    "type": college.get('type', 'General'),
                    "admission": college.get('admission', 'Various entrance exams'),
                    "highlights": college.get('highlights', [])[:3]  # Top 3 highlights
                })
        
        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # If no specific matches, provide some default good colleges
        if not recommendations:
            default_colleges = [
                {
                    "name": "Indian Institute of Technology - Bombay",
                    "location": "Mumbai, Maharashtra",
                    "fees": 250000,
                    "match_score": 85.0,
                    "match_reasons": ["Premier engineering institute", "Excellent career prospects"],
                    "type": "Engineering",
                    "admission": "JEE Advanced"
                },
                {
                    "name": "BITS Pilani",
                    "location": "Pilani, Rajasthan",
                    "fees": 450000,
                    "match_score": 80.0,
                    "match_reasons": ["Top private institute", "Industry-focused curriculum"],
                    "type": "Engineering",
                    "admission": "BITSAT"
                },
                {
                    "name": "All India Institute of Medical Sciences",
                    "location": "New Delhi",
                    "fees": 5000,
                    "match_score": 90.0,
                    "match_reasons": ["Premier medical institute", "Highly subsidized fees"],
                    "type": "Medical",
                    "admission": "NEET"
                }
            ]
            recommendations = default_colleges
        
        return recommendations[:10]  # Return top 10 recommendations


def get_college_database():
    """Get the college database for API endpoints"""
    counselor = DynamicCollegeCounselorBot()
    colleges = []
    
    for category in counselor.college_database.values():
        for college in category:
            colleges.append({
                "name": college['name'],
                "location": college['location'],
                "type": college.get('type', 'General'),
                "fees": college.get('fees', 0),
                "streams": college.get('streams', [])
            })
    
    return colleges


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
        # Fallback to counselor without API key
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
                extraction_history = ?, conversation_history = ?, message_count = ?
            WHERE session_id = ?
        """, (
            datetime.now().isoformat(),
            profile_data,
            counselor.sufficient_info_collected,
            counselor.conversation_stage,
            extraction_history,
            conversation_history,
            counselor.message_count,
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
        
        # Get recommendations if sufficient info is collected
        recommendations = None
        if counselor.sufficient_info_collected:
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
                # Fallback to counselor without API key
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
        "conversation_stage": counselor.conversation_stage,
        "message_count": counselor.message_count
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
        print("⚠️  Warning: OpenAI API key not properly configured - using fallback responses")
    
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