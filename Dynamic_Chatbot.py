import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import gradio as gr
from groq import Groq
from pydantic import BaseModel, Field, field_validator
import re
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Optional, Union
import re

class DynamicStudentProfile(BaseModel):
    # Core academic information
    grade_10_percentage: Optional[float] = Field(None, ge=0, le=100, description="10th standard marks percentage")
    grade_12_percentage: Optional[float] = Field(None, ge=0, le=100, description="12th standard marks percentage")
    cgpa: Optional[float] = Field(None, ge=0, le=10, description="Current CGPA if applicable")

    # Entrance exam scores
    jee_score: Optional[int] = Field(None, ge=1, description="JEE score/rank")
    neet_score: Optional[int] = Field(None, ge=1, description="NEET score/rank")
    sat_score: Optional[int] = Field(None, ge=400, le=1600, description="SAT score")
    gre_score: Optional[int] = Field(None, ge=260, le=340, description="GRE score")
    gate_score: Optional[int] = Field(None, ge=0, le=1000, description="GATE score")

    # Preferences and constraints
    budget_min: Optional[int] = Field(None, ge=0, description="Minimum budget for education")
    budget_max: Optional[int] = Field(None, ge=0, description="Maximum budget for education")
    preferred_location: Optional[str] = Field(None, description="Preferred study location")
    preferred_stream: Optional[str] = Field(None, description="Preferred academic stream/course")
    preferred_course_type: Optional[str] = Field(None, description="UG/PG/Diploma etc.")

    # Personal information
    gender: Optional[str] = Field(None, description="Student's gender")
    category: Optional[str] = Field(None, description="Reservation category")
    state_of_residence: Optional[str] = Field(None, description="State of residence")

    # Goals and interests
    career_goal: Optional[str] = Field(None, description="Career aspirations")
    specialization_interest: Optional[str] = Field(None, description="Area of specialization interest")
    extracurriculars: Optional[str] = Field(None, description="Extracurricular activities")

    # Dynamic fields for any additional extracted information
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Any other extracted information")

    # Extraction metadata
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Confidence scores for extracted fields")
    extraction_timestamps: Dict[str, str] = Field(default_factory=dict, description="When each field was extracted")

    @field_validator('budget_min', 'budget_max', mode='before')
    def convert_budget(cls, v):
        """Convert budget strings with lakhs/crores to actual numbers"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.lower().replace(',', '').replace(' ', '')
            if 'lakh' in v or 'lac' in v:
                num = re.findall(r'\d+\.?\d*', v)
                if num:
                    return int(float(num[0]) * 100000)
            elif 'crore' in v:
                num = re.findall(r'\d+\.?\d*', v)
                if num:
                    return int(float(num[0]) * 10000000)
            else:
                num = re.findall(r'\d+', v)
                if num:
                    return int(num[0])
        return v

    @field_validator('gender', mode='before')
    def normalize_gender(cls, v):
        """Normalize gender field"""
        if v is None:
            return None
        v = str(v).lower()
        if v in ['male', 'boy', 'm', 'man']:
            return 'Male'
        elif v in ['female', 'girl', 'f', 'woman']:
            return 'Female'
        else:
            return v.title()


    @field_validator('gender', mode='before')
    @classmethod
    def normalize_gender(cls, v):
        """Normalize gender field"""
        if v is None:
            return None
        v = str(v).lower()
        if v in ['male', 'boy', 'm', 'man']:
            return 'Male'
        elif v in ['female', 'girl', 'f', 'woman']:
            return 'Female'
        else:
            return v.title()


class DynamicCollegeCounselorChatbot:
    """
    Enhanced AI College Counselor with dynamic information extraction capabilities.
    Uses LLM to intelligently extract and categorize any relevant information from conversations.
    """

    def __init__(self, name="Lauren"):
        self.name = name
        self.model = "llama-3.1-8b-instant"
        
        # Check for API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        
        # Initialize dynamic student profile
        self.student_profile = DynamicStudentProfile()
        self.conversation_context = []
        self.extraction_history = []

        # Tracking flags
        self.sufficient_info_collected = False
        self.recommendations_provided = False
        self.profile_filename = None
        
        # Setup profile management
        self.profiles_dir = self.create_profiles_directory()
        self.initialize_profile_file()
        
        # Initialize conversation with system prompt
        self.conversation_history = [
            {"role": "system", "content": self._get_system_prompt()}
        ]
        
        # Enhanced college database with more diverse options
        self.colleges = self._initialize_college_database()

    def _get_system_prompt(self):
        """Generate dynamic system prompt for the counselor"""
        return f"""
        You are {self.name}, an intelligent AI college counselor specializing in Indian higher education.

        Your primary objectives:
        1. Engage in natural, friendly conversation with students
        2. Intelligently gather information about their academic background, preferences, and goals
        3. Provide personalized college recommendations when sufficient information is collected

        Key conversation principles:
        - Be warm, encouraging, and supportive
        - Ask follow-up questions naturally based on what the student shares
        - Don't overwhelm with too many questions at once
        - Acknowledge and build upon information they provide
        - Guide the conversation toward relevant details needed for recommendations

        Information you should gather (but don't ask all at once):
        - Academic performance (grades, CGPA, exam scores)
        - Preferred courses/streams and career goals
        - Budget constraints and location preferences
        - Personal background that might affect college choice
        - Any specific requirements or constraints

        Adapt your conversation style to the student's communication pattern.
        When you have enough information to make good recommendations, transition to providing them.
        """

    def _initialize_college_database(self):
        """Initialize comprehensive college database"""
        return [
            # Premier Engineering Institutes
            {"name": "IIT Bombay", "type": "Engineering", "location": "Mumbai", "fees": 800000, "min_rank": 100, "streams": ["Engineering", "Technology"], "acceptance": "Very Low"},
            {"name": "IIT Delhi", "type": "Engineering", "location": "Delhi", "fees": 750000, "min_rank": 150, "streams": ["Engineering", "Computer Science"], "acceptance": "Very Low"},
            {"name": "IIT Madras", "type": "Engineering", "location": "Chennai", "fees": 800000, "min_rank": 120, "streams": ["Engineering", "Technology"], "acceptance": "Very Low"},

            # Private Engineering
            {"name": "BITS Pilani", "type": "Engineering", "location": "Rajasthan", "fees": 1200000, "min_rank": 5000, "streams": ["Engineering", "Pharmacy", "Science"], "acceptance": "Low"},
            {"name": "VIT Vellore", "type": "Engineering", "location": "Tamil Nadu", "fees": 900000, "min_rank": 15000, "streams": ["Engineering", "Bio-Technology"], "acceptance": "Moderate"},
            {"name": "Manipal Institute of Technology", "type": "Engineering", "location": "Karnataka", "fees": 1500000, "min_rank": 20000, "streams": ["Engineering", "Medicine"], "acceptance": "Moderate"},

            # NITs
            {"name": "NIT Trichy", "type": "Engineering", "location": "Tamil Nadu", "fees": 500000, "min_rank": 3000, "streams": ["Engineering"], "acceptance": "Low"},
            {"name": "NIT Surathkal", "type": "Engineering", "location": "Karnataka", "fees": 480000, "min_rank": 3500, "streams": ["Engineering"], "acceptance": "Low"},

            # Medical Colleges
            {"name": "AIIMS Delhi", "type": "Medical", "location": "Delhi", "fees": 600000, "min_rank": 50, "streams": ["Medicine", "Nursing"], "acceptance": "Very Low"},
            {"name": "JIPMER Puducherry", "type": "Medical", "location": "Puducherry", "fees": 500000, "min_rank": 100, "streams": ["Medicine"], "acceptance": "Very Low"},

            # Universities
            {"name": "Delhi University", "type": "University", "location": "Delhi", "fees": 200000, "min_rank": None, "streams": ["Arts", "Commerce", "Science"], "acceptance": "Moderate"},
            {"name": "Jawaharlal Nehru University", "type": "University", "location": "Delhi", "fees": 300000, "min_rank": None, "streams": ["Arts", "Social Sciences"], "acceptance": "Low"},

            # Business Schools
            {"name": "IIM Ahmedabad", "type": "Management", "location": "Gujarat", "fees": 2300000, "min_rank": 99, "streams": ["MBA", "Management"], "acceptance": "Very Low"},
            {"name": "IIM Bangalore", "type": "Management", "location": "Bangalore", "fees": 2400000, "min_rank": 98, "streams": ["MBA", "Management"], "acceptance": "Very Low"},

            # Regional Options
            {"name": "Tula's Institute", "type": "Engineering", "location": "Dehradun", "fees": 600000, "min_rank": 50000, "streams": ["BCA", "MCA", "BBA", "MBA"], "acceptance": "High"},
            {"name": "Graphic Era University", "type": "University", "location": "Dehradun", "fees": 700000, "min_rank": 40000, "streams": ["Engineering", "Management"], "acceptance": "Moderate"},
        ]

    def create_profiles_directory(self):
        """Create profiles directory with error handling"""
        try:
            profiles_dir = Path('./student_profiles')
            profiles_dir.mkdir(parents=True, exist_ok=True)

            # Test write access
            test_file = profiles_dir / 'test_write.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()

            print(f"✅ Profiles directory: {profiles_dir.absolute()}")
            return profiles_dir
        except Exception as e:
            print(f"❌ Directory error: {e}")
            profiles_dir = Path(tempfile.gettempdir()) / 'student_profiles'
            profiles_dir.mkdir(parents=True, exist_ok=True)
            return profiles_dir

    def initialize_profile_file(self):
        """Initialize profile file for the session"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.profile_filename = self.profiles_dir / f"student_profile_{timestamp}.json"

            initial_profile = {
                "session_info": {
                    "created": datetime.now().isoformat(),
                    "counselor": self.name,
                    "status": "Active"
                },
                "student_profile": {},
                "extraction_history": [],
                "recommendations": []
            }

            with open(self.profile_filename, 'w', encoding='utf-8') as f:
                json.dump(initial_profile, f, indent=2)

            print(f"✅ Profile initialized: {self.profile_filename}")
        except Exception as e:
            print(f"❌ Profile initialization error: {e}")

    def dynamic_information_extraction(self, user_message):
        """
        Use LLM to dynamically extract any relevant information from user messages.
        This is the core dynamic extraction engine.
        """
        try:
            # Get current profile state
            current_profile = self.student_profile.model_dump()

            # Create extraction prompt
            extraction_prompt = f"""
            You are an expert information extraction system for educational counseling.

            CURRENT STUDENT PROFILE:
            {json.dumps({k: v for k, v in current_profile.items() if v is not None and k not in ['additional_info', 'confidence_scores', 'extraction_timestamps']}, indent=2)}

            USER MESSAGE: "{user_message}"

            Extract ALL relevant educational information from this message. Return a JSON object with these categories:

            1. ACADEMIC_PERFORMANCE: grades, percentages, CGPA, exam scores (JEE, NEET, SAT, etc.)
            2. PREFERENCES: preferred courses, streams, locations, college types
            3. CONSTRAINTS: budget (convert lakhs/crores to numbers), timeline, specific requirements
            4. PERSONAL_INFO: gender, category, state of residence, background details
            5. GOALS_INTERESTS: career goals, specialization interests, extracurriculars
            6. ADDITIONAL: any other relevant information not covered above
            7. CONFIDENCE: rate confidence (0-1) for each extracted piece of information

            IMPORTANT RULES:
            - Only extract information explicitly mentioned or clearly implied
            - Convert budget mentions: "5 lakhs" → 500000, "2 crores" → 20000000
            - Normalize exam names: "JEE Main" → "jee_score", "NEET" → "neet_score"
            - For grade ranges like "80-85%", use the average: 82.5
            - If multiple pieces of info in one category, separate them
            - Return ONLY valid JSON, no explanations

            EXAMPLE OUTPUT:
            {{
                "academic_performance": {{
                    "grade_12_percentage": {{"value": 85.5, "confidence": 0.9}}
                }},
                "preferences": {{
                    "preferred_stream": {{"value": "Computer Science", "confidence": 0.8}},
                    "preferred_location": {{"value": "Bangalore", "confidence": 0.7}}
                }},
                "constraints": {{
                    "budget_max": {{"value": 800000, "confidence": 0.9}}
                }},
                "additional": {{
                    "hobby": {{"value": "coding competitions", "confidence": 0.6}}
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.1,
                max_tokens=800,
            )
            
            extracted_text = response.choices[0].message.content.strip()
            print(f"🔍 Raw extraction: {extracted_text[:200]}...")
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                self._process_extracted_data(extracted_data, user_message)
                return True

        except Exception as e:
            print(f"❌ Extraction error: {e}")

        return False

    def _process_extracted_data(self, extracted_data, original_message):
        """Process and integrate extracted data into student profile"""

        current_data = self.student_profile.model_dump()
        timestamp = datetime.now().isoformat()

        # Field mapping for different categories
        field_mappings = {
            'academic_performance': {
                'grade_10_percentage': 'grade_10_percentage',
                'grade_12_percentage': 'grade_12_percentage',
                'cgpa': 'cgpa',
                'jee_score': 'jee_score',
                'neet_score': 'neet_score',
                'sat_score': 'sat_score',
                'gre_score': 'gre_score',
                'gate_score': 'gate_score'
            },
            'preferences': {
                'preferred_stream': 'preferred_stream',
                'preferred_location': 'preferred_location',
                'preferred_course_type': 'preferred_course_type'
            },
            'constraints': {
                'budget_min': 'budget_min',
                'budget_max': 'budget_max'
            },
            'personal_info': {
                'gender': 'gender',
                'category': 'category',
                'state_of_residence': 'state_of_residence'
            },
            'goals_interests': {
                'career_goal': 'career_goal',
                'specialization_interest': 'specialization_interest',
                'extracurriculars': 'extracurriculars'
            }
        }

        updates_made = []

        # Process each category
        for category, fields in extracted_data.items():
            if category == 'additional':
                # Handle additional information
                for key, info in fields.items():
                    if isinstance(info, dict) and 'value' in info:
                        current_data['additional_info'][key] = info['value']
                        current_data['confidence_scores'][f"additional_{key}"] = info.get('confidence', 0.5)
                        current_data['extraction_timestamps'][f"additional_{key}"] = timestamp
                        updates_made.append(f"additional_{key}: {info['value']}")
                continue

            # Process mapped fields
            mapping = field_mappings.get(category, {})
            for field_name, info in fields.items():
                if isinstance(info, dict) and 'value' in info:
                    # Map to profile field
                    profile_field = mapping.get(field_name, field_name)

                    if profile_field in current_data:
                        current_data[profile_field] = info['value']
                        current_data['confidence_scores'][profile_field] = info.get('confidence', 0.5)
                        current_data['extraction_timestamps'][profile_field] = timestamp
                        updates_made.append(f"{profile_field}: {info['value']}")
                    else:
                        # Store in additional_info if not a standard field
                        current_data['additional_info'][field_name] = info['value']
                        current_data['confidence_scores'][f"additional_{field_name}"] = info.get('confidence', 0.5)
                        current_data['extraction_timestamps'][f"additional_{field_name}"] = timestamp
                        updates_made.append(f"additional_{field_name}: {info['value']}")
        
        # Update the profile with validated data
        try:
            self.student_profile = DynamicStudentProfile(**current_data)

            # Record extraction history
            self.extraction_history.append({
                "timestamp": timestamp,
                "message": original_message,
                "extracted_fields": updates_made,
                "total_fields_now": len([k for k, v in current_data.items() if v is not None and k not in ['additional_info', 'confidence_scores', 'extraction_timestamps']])
            })

            print(f"📊 Updated fields: {updates_made}")
            self._save_profile()

        except Exception as e:
            print(f"❌ Profile validation error: {e}")

    def assess_information_sufficiency(self):
        """
        Dynamically assess if we have sufficient information for recommendations.
        Uses LLM to make intelligent decisions about readiness.
        """

        profile_data = self.student_profile.model_dump()
        non_empty_fields = {k: v for k, v in profile_data.items()
                           if v is not None and v != {} and k not in ['confidence_scores', 'extraction_timestamps']}

        assessment_prompt = f"""
        Assess if we have sufficient information to provide meaningful college recommendations.

        CURRENT STUDENT INFORMATION:
        {json.dumps(non_empty_fields, indent=2, default=str)}

        CRITERIA FOR ASSESSMENT:
        1. Academic Performance: Do we have any grades/scores?
        2. Preferences: Do we know what they want to study or where?
        3. Constraints: Do we understand their limitations (budget, location, etc.)?
        4. Goals: Do we have some sense of their career direction?

        Return JSON response:
        {{
            "sufficient_for_recommendations": true/false,
            "confidence_level": 0.0-1.0,
            "missing_critical_info": ["list", "of", "gaps"],
            "next_conversation_focus": "what to ask about next",
            "reasoning": "brief explanation"
        }}

        Be practical - we don't need perfect information, just enough to give helpful guidance.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": assessment_prompt}],
                temperature=0.2,
                max_tokens=400,
            )

            assessment_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)

            if json_match:
                assessment = json.loads(json_match.group())
                self.sufficient_info_collected = assessment.get('sufficient_for_recommendations', False)
                print(f"📋 Sufficiency assessment: {assessment}")
                return assessment

        except Exception as e:
            print(f"❌ Assessment error: {e}")

        # Fallback: simple rule-based check
        essential_fields = ['grade_12_percentage', 'preferred_stream', 'budget_max']
        has_essential = any(getattr(self.student_profile, field, None) is not None for field in essential_fields)
        self.sufficient_info_collected = has_essential

        return {
            "sufficient_for_recommendations": has_essential,
            "confidence_level": 0.5,
            "missing_critical_info": [],
            "next_conversation_focus": "basic academic information",
            "reasoning": "Fallback assessment"
        }

    def generate_personalized_recommendations(self):
        """Generate intelligent college recommendations based on collected profile"""

        profile_data = self.student_profile.model_dump()
        suitable_colleges = []

        for college in self.colleges:
            match_score = 0
            match_reasons = []

            # Academic fit
            if profile_data.get('jee_score') and college.get('min_rank'):
                if profile_data['jee_score'] <= college['min_rank']:
                    match_score += 30
                    match_reasons.append(f"JEE rank qualifies (cutoff: {college['min_rank']})")

            # Stream/course match
            if profile_data.get('preferred_stream'):
                user_stream = profile_data['preferred_stream'].lower()
                college_streams = [s.lower() for s in college.get('streams', [])]
                if any(user_stream in cs or cs in user_stream for cs in college_streams):
                    match_score += 25
                    match_reasons.append(f"Offers {profile_data['preferred_stream']}")

            # Location preference
            if profile_data.get('preferred_location'):
                user_location = profile_data['preferred_location'].lower()
                college_location = college['location'].lower()
                if user_location in college_location or college_location in user_location:
                    match_score += 20
                    match_reasons.append(f"Located in preferred area")

            # Budget fit
            if profile_data.get('budget_max'):
                if college['fees'] <= profile_data['budget_max']:
                    match_score += 15
                    match_reasons.append(f"Within budget (₹{college['fees']:,})")
                elif college['fees'] <= profile_data['budget_max'] * 1.2:  # 20% flexibility
                    match_score += 5
                    match_reasons.append(f"Slightly above budget but manageable")

            # Add base score for all colleges
            match_score += 10
            if not match_reasons:
                match_reasons.append("General recommendation")

            suitable_colleges.append({
                **college,
                'match_score': match_score,
                'match_reasons': match_reasons
            })

        # Sort by match score and return top recommendations
        suitable_colleges.sort(key=lambda x: x['match_score'], reverse=True)
        return suitable_colleges[:6]

    def chat(self, message, history):
        """
        Main chat processing function with dynamic information extraction
        """
        print(f"💬 Processing: {message[:50]}...")

        # Extract information dynamically
        extraction_success = self.dynamic_information_extraction(message)

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Assess if we have sufficient information
        if not self.sufficient_info_collected:
            assessment = self.assess_information_sufficiency()

            if self.sufficient_info_collected:
                # Generate recommendations
                recommendations = self.generate_personalized_recommendations()

                # Create recommendation prompt
                rec_prompt = f"""
                The student profile is now complete. Provide personalized college recommendations.

                STUDENT PROFILE:
                {json.dumps({k: v for k, v in self.student_profile.model_dump().items() if v is not None}, indent=2, default=str)}

                TOP COLLEGE MATCHES:
                {json.dumps(recommendations[:3], indent=2, default=str)}

                Provide a warm, comprehensive response that:
                1. Acknowledges their shared information
                2. Explains 3-4 top college recommendations with specific reasons
                3. Mentions key factors like fees, location, admission requirements
                4. Gives practical next steps for applications
                5. Mentions they can download their complete profile

                Be encouraging and specific about why each college fits their profile.
                """

                self.conversation_history.append({"role": "system", "content": rec_prompt})
                self.recommendations_provided = True

            else:
                # Continue gathering information
                next_focus = assessment.get('next_conversation_focus', 'your academic background')

                continuation_prompt = f"""
                Continue the natural conversation. The student just shared: "{message}"

                Current information collected: {len([k for k, v in self.student_profile.model_dump().items() if v is not None])} fields

                Assessment suggests focusing on: {next_focus}

                Acknowledge what they shared and naturally guide toward: {next_focus}
                Be conversational and encouraging. Don't overwhelm with questions.
                """

                self.conversation_history.append({"role": "system", "content": continuation_prompt})

        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[-10:],  # Keep recent context
                temperature=0.7,
                max_tokens=1000,
            )

            assistant_response = response.choices[0].message.content

        except Exception as e:
            assistant_response = f"I apologize, but I encountered an error: {str(e)}"
            print(f"❌ Chat error: {e}")

        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": assistant_response})

        return assistant_response

    def _save_profile(self):
        """Save current profile state to file"""
        try:
            profile_data = {
                "session_info": {
                    "updated": datetime.now().isoformat(),
                    "counselor": self.name,
                    "status": "Complete" if self.sufficient_info_collected else "In Progress"
                },
                "student_profile": self.student_profile.model_dump(),
                "extraction_history": self.extraction_history,
                "recommendations": self.generate_personalized_recommendations() if self.sufficient_info_collected else []
            }

            with open(self.profile_filename, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            print(f"❌ Save error: {e}")

    def get_profile_for_download(self):
        """Get formatted profile for download"""
        try:
            profile_data = {
                "session_info": {
                    "updated": datetime.now().isoformat(),
                    "counselor": self.name,
                    "status": "Complete" if self.sufficient_info_collected else "In Progress"
                },
                "student_profile": self.student_profile.model_dump(),
                "extraction_history": self.extraction_history,
                "recommendations": self.generate_personalized_recommendations() if self.sufficient_info_collected else []
            }
            return json.dumps(profile_data, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": f"Could not generate profile: {str(e)}"}, indent=2)


def create_chatbot_interface():
    """Create enhanced Gradio interface"""
    counselor = DynamicCollegeCounselorChatbot(name="Lauren")
    with gr.Blocks(title="Lauren - Dynamic AI College Counselor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎓 Lauren - Your Dynamic AI College Counselor")
        gr.Markdown("""
        Welcome! I'm Lauren, your AI college counselor. I use advanced conversation analysis to understand your needs and provide personalized recommendations.
        Just chat naturally about your academic background, goals, and preferences - I'll automatically extract and organize the relevant information!
        """)
        chatbot = gr.Chatbot(height=600, show_copy_button=True, type="messages")

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Hi Lauren! I'm looking for college guidance. I scored 85% in 12th grade...",
                container=False,
                scale=7
            )
            submit = gr.Button("Send", variant="primary", scale=1)

        with gr.Row():
            clear = gr.Button("New Session", scale=1)
            download_btn = gr.Button("📄 Download Profile", variant="secondary", scale=1)

        download_file = gr.File(label="Your Profile", visible=False)

        # Status display
        status_display = gr.Markdown("🤖 **Status:** Ready to chat! I'll dynamically extract information as we talk.")

        # Initial greeting
        initial_greeting = {
            "role": "assistant",
            "content": """
            👋 Hi there! I'm Lauren, your AI college counselor.
            I'm here to help you find the perfect colleges based on your unique profile and goals. What makes me special is that I can understand and organize information from natural conversation - you don't need to fill out forms!
            Just tell me about yourself, your academic background, what you're interested in studying, or any concerns you have about college selection. I'll automatically pick up on the important details and help guide you toward great options.
            What would you like to share about your educational journey? 😊
            """
        }

        def respond(message, chat_history):
            if not message.strip():
                return chat_history, gr.update(), gr.update(visible=False)
            response = counselor.chat(message, chat_history)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})

            # Update status display based on conversation state
            status_text = "📊 **Status:** Collecting information..."
            if counselor.sufficient_info_collected:
                status_text = "✅ **Status:** Ready with recommendations! You can download your profile."
            status_display_value = gr.update(value=status_text)

            # Make download button visible if sufficient info is collected
            download_visibility = gr.update(visible=counselor.sufficient_info_collected)

            return chat_history, status_display_value, download_visibility

        def download_profile():
            profile_path = counselor.profile_filename
            return gr.update(value=str(profile_path), visible=True)

        def new_session():
            # Reset the counselor instance for a new session
            counselor.__init__()
            return [], gr.update(visible=False), gr.update(value="🤖 **Status:** Ready to chat! I'll dynamically extract information as we talk.")

        # Set up event handlers
        submit.click(respond, [msg, chatbot], [chatbot, status_display, download_btn])
        clear.click(new_session, outputs=[chatbot, download_file, status_display])
        download_btn.click(download_profile, outputs=[download_file])

        # Display initial greeting
        chatbot.value = [initial_greeting]

    return app

# Example usage
if __name__ == "__main__":
    app = create_chatbot_interface()
    app.launch()
