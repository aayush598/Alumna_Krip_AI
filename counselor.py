import os
import json
import re
from datetime import datetime
from pathlib import Path
import tempfile
from typing import List, Dict, Any

from dotenv import load_dotenv
from groq import Groq

from student_profile import DynamicStudentProfile
from college_database import get_college_database

# Load environment variables
load_dotenv()

class DynamicCollegeCounselorChatbot:
    def __init__(self, name="Lauren"):
        self.name = name
        self.model = "llama-3.1-8b-instant"
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)

        self.student_profile = DynamicStudentProfile()
        self.conversation_context = []
        self.extraction_history = []

        self.sufficient_info_collected = False
        self.recommendations_provided = False
        self.profile_filename = None

        self.profiles_dir = self.create_profiles_directory()
        self.initialize_profile_file()

        self.conversation_history = [
            {"role": "system", "content": self._get_system_prompt()}
        ]

        self.colleges = get_college_database()

    def _get_system_prompt(self):
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

    def create_profiles_directory(self):
        try:
            profiles_dir = Path('./student_profiles')
            profiles_dir.mkdir(parents=True, exist_ok=True)
            test_file = profiles_dir / 'test_write.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            print(f"✅ Profiles directory: {profiles_dir.absolute()}")
            return profiles_dir
        except Exception as e:
            print(f"❌ Directory error: {e}")
            fallback_dir = Path(tempfile.gettempdir()) / 'student_profiles'
            fallback_dir.mkdir(parents=True, exist_ok=True)
            return fallback_dir

    def initialize_profile_file(self):
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
        try:
            current_profile = self.student_profile.model_dump()
            prompt = f"""
            You are an expert information extraction system for educational counseling.

            CURRENT STUDENT PROFILE:
            {json.dumps({k: v for k, v in current_profile.items() if v is not None and k not in ['additional_info', 'confidence_scores', 'extraction_timestamps']}, indent=2)}

            USER MESSAGE: "{user_message}"

            Extract ALL relevant educational information from this message. Return a JSON object with these categories:
            academic_performance, preferences, constraints, personal_info, goals_interests, additional, confidence

            IMPORTANT:
            - Convert budgets like '5 lakhs' → 500000
            - Normalize exam names
            - Output valid JSON only

            EXAMPLE OUTPUT:
            {{
              "academic_performance": {{
                "grade_12_percentage": {{"value": 85.5, "confidence": 0.9}}
              }},
              ...
            }}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )

            extracted_text = response.choices[0].message.content.strip()
            match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                self._process_extracted_data(data, user_message)
                return True

        except Exception as e:
            print(f"❌ Extraction error: {e}")
        return False

    def _process_extracted_data(self, extracted_data, original_message):
        current_data = self.student_profile.model_dump()
        timestamp = datetime.now().isoformat()
        updates_made = []

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

        for category, fields in extracted_data.items():
            if category == 'additional':
                for key, info in fields.items():
                    if isinstance(info, dict) and 'value' in info:
                        current_data['additional_info'][key] = info['value']
                        current_data['confidence_scores'][f"additional_{key}"] = info.get('confidence', 0.5)
                        current_data['extraction_timestamps'][f"additional_{key}"] = timestamp
                        updates_made.append(f"additional_{key}: {info['value']}")
                continue

            mapping = field_mappings.get(category, {})
            for field_name, info in fields.items():
                if isinstance(info, dict) and 'value' in info:
                    profile_field = mapping.get(field_name, field_name)
                    if profile_field in current_data:
                        current_data[profile_field] = info['value']
                        current_data['confidence_scores'][profile_field] = info.get('confidence', 0.5)
                        current_data['extraction_timestamps'][profile_field] = timestamp
                        updates_made.append(f"{profile_field}: {info['value']}")
                    else:
                        current_data['additional_info'][field_name] = info['value']
                        current_data['confidence_scores'][f"additional_{field_name}"] = info.get('confidence', 0.5)
                        current_data['extraction_timestamps'][f"additional_{field_name}"] = timestamp
                        updates_made.append(f"additional_{field_name}: {info['value']}")

        try:
            self.student_profile = DynamicStudentProfile(**current_data)
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
        profile_data = self.student_profile.model_dump()
        non_empty = {k: v for k, v in profile_data.items() if v and k not in ['confidence_scores', 'extraction_timestamps']}

        prompt = f"""
        Assess if we have sufficient information for recommendations.

        STUDENT DATA:
        {json.dumps(non_empty, indent=2)}

        Return:
        {{
          "sufficient_for_recommendations": true/false,
          "confidence_level": 0.0-1.0,
          "missing_critical_info": [],
          "next_conversation_focus": "field",
          "reasoning": "explanation"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=400
            )

            text = response.choices[0].message.content.strip()
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                self.sufficient_info_collected = result.get("sufficient_for_recommendations", False)
                return result

        except Exception as e:
            print(f"❌ Assessment error: {e}")

        essential = ['grade_12_percentage', 'preferred_stream', 'budget_max']
        has_info = any(getattr(self.student_profile, f, None) for f in essential)
        self.sufficient_info_collected = has_info
        return {
            "sufficient_for_recommendations": has_info,
            "confidence_level": 0.5,
            "missing_critical_info": [],
            "next_conversation_focus": "academic info",
            "reasoning": "Fallback"
        }

    def generate_personalized_recommendations(self):
        profile = self.student_profile.model_dump()
        matches = []

        for college in self.colleges:
            score = 0
            reasons = []

            if profile.get('jee_score') and college.get('min_rank'):
                if profile['jee_score'] <= college['min_rank']:
                    score += 30
                    reasons.append("JEE rank qualifies")

            if profile.get('preferred_stream'):
                user_stream = profile['preferred_stream'].lower()
                if any(user_stream in s.lower() for s in college.get('streams', [])):
                    score += 25
                    reasons.append("Stream matched")

            if profile.get('preferred_location') and profile['preferred_location'].lower() in college['location'].lower():
                score += 20
                reasons.append("Location matched")

            if profile.get('budget_max'):
                if college['fees'] <= profile['budget_max']:
                    score += 15
                    reasons.append("Within budget")
                elif college['fees'] <= profile['budget_max'] * 1.2:
                    score += 5
                    reasons.append("Slightly above budget")

            score += 10
            if not reasons:
                reasons.append("General recommendation")

            matches.append({
                **college,
                "match_score": score,
                "match_reasons": reasons
            })

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:6]

    def chat(self, message, history):
        print(f"💬 Processing: {message[:50]}...")
        self.dynamic_information_extraction(message)
        self.conversation_history.append({"role": "user", "content": message})

        if not self.sufficient_info_collected:
            result = self.assess_information_sufficiency()

            if self.sufficient_info_collected:
                recs = self.generate_personalized_recommendations()
                prompt = f"""
                The profile is now complete. Generate a warm, detailed response based on:

                PROFILE:
                {json.dumps(self.student_profile.model_dump(), indent=2)}

                TOP MATCHES:
                {json.dumps(recs[:3], indent=2)}
                """
                self.conversation_history.append({"role": "system", "content": prompt})
            else:
                focus = result.get("next_conversation_focus", "your education")
                follow_up = f"Let's continue. Tell me more about {focus}."
                self.conversation_history.append({"role": "system", "content": follow_up})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[-10:],
                temperature=0.7,
                max_tokens=1000
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Sorry, I encountered an error: {str(e)}"
            print(f"❌ Chat error: {e}")

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def _save_profile(self):
        try:
            data = {
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
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"❌ Save error: {e}")

    def get_profile_for_download(self):
        try:
            return json.dumps({
                "session_info": {
                    "updated": datetime.now().isoformat(),
                    "counselor": self.name,
                    "status": "Complete" if self.sufficient_info_collected else "In Progress"
                },
                "student_profile": self.student_profile.model_dump(),
                "extraction_history": self.extraction_history,
                "recommendations": self.generate_personalized_recommendations() if self.sufficient_info_collected else []
            }, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
