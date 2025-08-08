import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import gradio as gr
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
import re
from pathlib import Path
import tempfile

# Removed the dotenv import since we're not using environment variables anymore
# from dotenv import load_dotenv

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
    Enhanced AI College Counselor with natural conversation flow and selective information extraction.
    """

    def __init__(self, name="Lauren", api_key=None):
        self.name = name
        self.model = "gpt-3.5-turbo"
        
        # Use provided API key or raise error
        if not api_key:
            raise ValueError("API key must be provided directly to the constructor")
        
        self.client = OpenAI(api_key=api_key)
        
        # Initialize dynamic student profile
        self.student_profile = DynamicStudentProfile()
        self.conversation_context = []
        self.extraction_history = []

        # Conversation state tracking
        self.conversation_stage = "greeting"  # greeting -> getting_to_know -> information_gathering -> recommendations
        self.message_count = 0
        self.last_extraction_attempt = 0
        
        # Tracking flags
        self.sufficient_info_collected = False
        self.recommendations_provided = False
        self.profile_filename = None
        
        # Setup profile management
        self.profiles_dir = self.create_profiles_directory()
        self.initialize_profile_file()
        
        # Initialize conversation with a natural system prompt
        self.conversation_history = [
            {"role": "system", "content": self._get_natural_system_prompt()}
        ]
        
        # Enhanced college database with more diverse options
        self.colleges = self._initialize_college_database()

    def _get_natural_system_prompt(self):
        """Generate a natural, conversational system prompt"""
        return f"""
        You are {self.name}, a friendly and experienced college counselor who specializes in helping Indian students find the right colleges and courses.

        Your personality:
        - Warm, approachable, and genuinely interested in helping students
        - Patient and understanding - you know college selection can be stressful
        - Professional but not overly formal - like talking to a helpful older sibling
        - Encouraging and positive, always highlighting possibilities

        Your conversation approach:
        1. Start with a genuine greeting and get to know the student as a person
        2. Show interest in their background, dreams, and concerns naturally
        3. Ask follow-up questions based on what they share, not from a checklist
        4. Only move to specific academic details once rapport is established
        5. Provide recommendations when you have enough information, not before

        Key principles:
        - Have natural conversations - don't rush to collect data
        - Ask ONE question at a time, not multiple
        - Show genuine interest in their responses
        - Acknowledge their concerns and validate their feelings
        - Share encouragement and insights naturally
        - Only extract information when it's clearly relevant and explicitly mentioned

        Remember: You're counseling a person, not filling out a form. Build trust first, then gather information naturally.

        Important Boundaries:
        Reject any requests for vulgar, inappropriate, offensive, or unrelated content.
        
        If a student asks about anything unrelated to education or career guidance (e.g., vulgar jokes, adult content, or unrelated topics), gently redirect them to stay focused on their educational goals.
        
        Always maintain a safe, respectful, and age-appropriate environment.
        
        Respond professionally but kindly when guiding students away from off-topic or inappropriate requests.
        
        ✅ Remember: You are here to guide, support, and empower students on their educational journey.
        ❌ You are not here to entertain, joke inappropriately, or respond to unrelated or offensive topics.
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

    def should_extract_information(self, user_message):
        """
        Determine if this message contains information worth extracting.
        Only extract when there's clear educational/academic content.
        """
        # Don't extract from greetings or very short messages
        if len(user_message.split()) < 3:
            return False
            
        # Don't extract too frequently
        if self.message_count - self.last_extraction_attempt < 2:
            return False
            
        # Look for educational keywords
        educational_keywords = [
            'grade', 'marks', 'percentage', 'cgpa', 'score', 'rank',
            'jee', 'neet', 'sat', 'gate', 'exam', 'test',
            'engineering', 'medical', 'commerce', 'arts', 'science',
            'college', 'university', 'course', 'stream', 'branch',
            'budget', 'fees', 'cost', 'lakhs', 'crores',
            'location', 'city', 'state', 'prefer',
            'career', 'job', 'future', 'goal', 'interest'
        ]
        
        message_lower = user_message.lower()
        has_educational_content = any(keyword in message_lower for keyword in educational_keywords)
        
        return has_educational_content

    def smart_information_extraction(self, user_message):
        """
        Smarter information extraction that only activates when relevant content is detected.
        """
        if not self.should_extract_information(user_message):
            return False

        try:
            # Get current profile state
            current_profile = self.student_profile.model_dump()

            # Create focused extraction prompt
            extraction_prompt = f"""
            Extract ONLY clear, specific educational information from this student message.

            STUDENT MESSAGE: "{user_message}"

            CURRENT PROFILE (don't duplicate):
            {json.dumps({k: v for k, v in current_profile.items() if v is not None and k not in ['additional_info', 'confidence_scores', 'extraction_timestamps']}, indent=2)}

            Extract ONLY if information is:
            1. Explicitly mentioned (not implied or assumed)
            2. Educational/academic in nature
            3. Not already in the current profile
            4. Specific and clear (not vague)

            Return JSON with extracted information:
            {{
                "academic_scores": {{"field_name": {{"value": actual_value, "confidence": 0.0-1.0}}}},
                "preferences": {{"field_name": {{"value": "actual_value", "confidence": 0.0-1.0}}}},
                "constraints": {{"field_name": {{"value": actual_value, "confidence": 0.0-1.0}}}},
                "personal": {{"field_name": {{"value": "actual_value", "confidence": 0.0-1.0}}}},
                "goals": {{"field_name": {{"value": "actual_value", "confidence": 0.0-1.0}}}}
            }}

            If no clear educational information is found, return: {{"no_extraction": true}}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.1,
                max_tokens=500,
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                
                # Check if extraction found anything meaningful
                if extracted_data.get('no_extraction'):
                    return False
                    
                # Process extracted data if meaningful content found
                if any(category for category in extracted_data.values() if isinstance(category, dict) and category):
                    self._process_extracted_data(extracted_data, user_message)
                    self.last_extraction_attempt = self.message_count
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
            'academic_scores': {
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
            'personal': {
                'gender': 'gender',
                'category': 'category',
                'state_of_residence': 'state_of_residence'
            },
            'goals': {
                'career_goal': 'career_goal',
                'specialization_interest': 'specialization_interest',
                'extracurriculars': 'extracurriculars'
            }
        }

        updates_made = []

        # Process each category
        for category, fields in extracted_data.items():
            if not isinstance(fields, dict):
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

            if updates_made:
                print(f"📊 Updated fields: {updates_made}")
                self._save_profile()

        except Exception as e:
            print(f"❌ Profile validation error: {e}")

    def assess_conversation_readiness(self):
        """
        Assess if we're ready to provide recommendations based on conversation stage and information.
        """
        profile_data = self.student_profile.model_dump()
        non_empty_fields = {k: v for k, v in profile_data.items()
                           if v is not None and v != {} and k not in ['confidence_scores', 'extraction_timestamps']}

        # Need at least some basic information before recommendations
        if len(non_empty_fields) < 3:
            return False

        # Check for minimum viable information
        has_academic_info = any(field in non_empty_fields for field in ['grade_12_percentage', 'cgpa', 'jee_score', 'neet_score'])
        has_preference_info = any(field in non_empty_fields for field in ['preferred_stream', 'career_goal', 'preferred_location'])
        
        return has_academic_info and has_preference_info

    def update_conversation_stage(self, user_message):
        """Update conversation stage based on message content and history"""
        message_lower = user_message.lower()
        
        # Determine stage transitions
        if self.message_count <= 2 and any(greeting in message_lower for greeting in ['hi', 'hello', 'hey', 'good']):
            self.conversation_stage = "greeting"
        elif self.conversation_stage == "greeting" and self.message_count <= 4:
            self.conversation_stage = "getting_to_know"
        elif any(keyword in message_lower for keyword in ['grade', 'marks', 'score', 'college', 'course', 'stream']):
            self.conversation_stage = "information_gathering"
        elif self.assess_conversation_readiness():
            self.conversation_stage = "ready_for_recommendations"

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
                match_reasons.append("General recommendation based on profile")

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
        Main chat processing function with natural conversation flow
        """
        self.message_count += 1
        print(f"💬 Message {self.message_count}: {message[:50]}...")

        # Update conversation stage
        self.update_conversation_stage(message)
        
        # Only attempt extraction if appropriate
        extraction_attempted = False
        if self.conversation_stage in ["information_gathering", "ready_for_recommendations"]:
            extraction_attempted = self.smart_information_extraction(message)

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Generate appropriate response based on conversation stage
        try:
            if self.conversation_stage == "ready_for_recommendations" and not self.recommendations_provided:
                # Generate recommendations
                recommendations = self.generate_personalized_recommendations()
                
                # Add context for recommendation response
                context_prompt = f"""
                The student is ready for personalized recommendations. Based on our conversation and their profile:

                KEY STUDENT INFO:
                {json.dumps({k: v for k, v in self.student_profile.model_dump().items() if v is not None and k not in ['additional_info', 'confidence_scores', 'extraction_timestamps']}, indent=2, default=str)}

                TOP MATCHES:
                {json.dumps(recommendations[:3], indent=2, default=str)}

                Provide a warm, comprehensive response that:
                1. Acknowledges their patience and the information they've shared
                2. Presents 3-4 specific college recommendations with clear reasons
                3. Explains key factors like admission requirements, fees, and fit
                4. Gives practical next steps for research and applications
                5. Remains encouraging and supportive

                Be specific about why each college matches their profile and goals.
                """
                
                self.conversation_history.append({"role": "system", "content": context_prompt})
                self.recommendations_provided = True
            
            # Generate natural response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[-8:],  # Keep recent context but not too much
                temperature=0.8,  # More natural and varied responses
                max_tokens=800,
                frequency_penalty=0.3,  # Reduce repetition
                presence_penalty=0.2    # Encourage topic variety
            )

            assistant_response = response.choices[0].message.content

        except Exception as e:
            assistant_response = f"I apologize, but I encountered a technical issue. Could you please share that again? I'm here to help you with your college search!"
            print(f"❌ Chat error: {e}")

        # Add response to history (but keep it manageable)
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        # Keep conversation history manageable
        if len(self.conversation_history) > 20:
            # Keep system prompt and recent messages
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-15:]

        return assistant_response

    def _save_profile(self):
        """Save current profile state to file"""
        try:
            if self.conversation_stage == "ready_for_recommendations":
                self.sufficient_info_collected = True
                
            profile_data = {
                "session_info": {
                    "updated": datetime.now().isoformat(),
                    "counselor": self.name,
                    "conversation_stage": self.conversation_stage,
                    "message_count": self.message_count,
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
                    "conversation_stage": self.conversation_stage,
                    "total_messages": self.message_count,
                    "status": "Complete" if self.sufficient_info_collected else "In Progress"
                },
                "student_profile": self.student_profile.model_dump(),
                "extraction_history": self.extraction_history,
                "recommendations": self.generate_personalized_recommendations() if self.sufficient_info_collected else []
            }
            return json.dumps(profile_data, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": f"Could not generate profile: {str(e)}"}, indent=2)


def create_chatbot_interface(api_key):
    """Create enhanced Gradio interface with natural conversation flow"""
    if not api_key:
        raise ValueError("API key must be provided to create the chatbot interface")
    
    counselor = DynamicCollegeCounselorChatbot(name="Lauren", api_key=api_key)
    
    with gr.Blocks(title="Lauren - Your Natural AI College Counselor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎓 Lauren - Your AI College Counselor")
        gr.Markdown("""
        Hi! I'm Lauren, your friendly AI college counselor. I'm here to have a natural conversation about your educational journey and help you discover the perfect colleges for your goals.
        
        Just start by saying hello and telling me a bit about yourself. No need to fill out forms - we'll chat naturally and I'll learn about your needs as we go! 😊
        """)
        
        chatbot = gr.Chatbot(height=600, show_copy_button=True, type="messages")

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Hi Lauren! I'm a student looking for guidance with college selection...",
                container=False,
                scale=7
            )
            submit = gr.Button("Send", variant="primary", scale=1)

        with gr.Row():
            clear = gr.Button("New Session", scale=1)
            download_btn = gr.Button("📄 Download Profile", variant="secondary", scale=1, visible=False)

        download_file = gr.File(label="Your Profile", visible=False)

        # Status display
        status_display = gr.Markdown("💫 **Status:** Ready to chat! Just say hello and let's get to know each other.")

        # Natural initial greeting
        initial_greeting = {
            "role": "assistant",
            "content": """
            Hi there! 👋 I'm Lauren, your AI college counselor, and I'm so glad you're here!

            I know that choosing the right college can feel overwhelming - there are so many options, requirements to consider, and big decisions to make. But don't worry, that's exactly what I'm here for! 

            I'd love to get to know you first. What's your name? And what brings you here today - are you currently in 12th grade, thinking about your next steps after graduation, or maybe exploring options for higher studies?

            There's no rush at all. We can take this conversation at whatever pace feels comfortable for you! 😊
            """
        }

        def respond(message, chat_history):
            if not message.strip():
                return chat_history, gr.update(), gr.update(visible=False)
            
            response = counselor.chat(message, chat_history)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})

            # Update status display based on conversation stage
            stage_messages = {
                "greeting": "👋 Getting to know you - feel free to share at your own pace!",
                "getting_to_know": "💭 Learning about your interests and background...",
                "information_gathering": "📚 Understanding your academic profile and preferences...",
                "ready_for_recommendations": "✅ Ready with personalized recommendations! You can download your profile."
            }
            
            status_text = f"💫 **Status:** {stage_messages.get(counselor.conversation_stage, 'Having a great conversation!')}"
            status_display_value = gr.update(value=status_text)

            # Make download button visible when recommendations are ready
            download_visibility = gr.update(visible=(counselor.conversation_stage == "ready_for_recommendations"))

            return chat_history, status_display_value, download_visibility

        def download_profile():
            if counselor.profile_filename and counselor.profile_filename.exists():
                return gr.update(value=str(counselor.profile_filename), visible=True)
            else:
                # Create a temporary file with profile data
                profile_content = counselor.get_profile_for_download()
                temp_file = counselor.profiles_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(profile_content)
                return gr.update(value=str(temp_file), visible=True)

        def new_session():
            # Reset the counselor instance for a new session
            nonlocal counselor
            counselor = DynamicCollegeCounselorChatbot(name="Lauren", api_key=api_key)
            return [initial_greeting], gr.update(visible=False), gr.update(value="💫 **Status:** Ready to chat! Just say hello and let's get to know each other.")

        def clear_input():
            return ""

        # Set up event handlers
        submit.click(respond, [msg, chatbot], [chatbot, status_display, download_btn]).then(clear_input, outputs=[msg])
        msg.submit(respond, [msg, chatbot], [chatbot, status_display, download_btn]).then(clear_input, outputs=[msg])
        clear.click(new_session, outputs=[chatbot, download_file, status_display])
        download_btn.click(download_profile, outputs=[download_file])

        # Display initial greeting
        chatbot.value = [initial_greeting]

    return app

# Example usage
if __name__ == "__main__":
    # Replace this with your actual OpenAI API key
    YOUR_API_KEY = ""
    
    app = create_chatbot_interface(YOUR_API_KEY)
    app.launch(debug=True)
