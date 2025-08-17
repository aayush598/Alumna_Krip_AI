import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import gradio as gr
from openai import OpenAI
from pydantic import BaseModel, Field
import re
from pathlib import Path
import tempfile
import random

class StudentConversation(BaseModel):
    """Simple conversation tracker without rigid field extraction"""
    conversation_id: str = Field(default_factory=lambda: f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    student_context: Dict[str, Any] = Field(default_factory=dict, description="Flexible context about the student")
    conversation_flow: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    insights_discovered: List[str] = Field(default_factory=list, description="Key insights about the student")
    recommendations_given: List[Dict[str, Any]] = Field(default_factory=list, description="Recommendations provided")
    conversation_stage: str = Field(default="introduction", description="Current conversation stage")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())


class DynamicCollegeCounselorBot:
    """
    A truly dynamic AI College Counselor that focuses on natural conversation
    and provides comprehensive guidance without rigid information extraction.
    """

    def __init__(self, name="Lauren", api_key=None):
        self.name = name
        self.model = "gpt-3.5-turbo"
        
        if not api_key:
            raise ValueError("API key must be provided directly to the constructor")
        
        self.client = OpenAI(api_key=api_key)
        
        # Initialize flexible conversation tracking
        self.conversation = StudentConversation()
        self.message_count = 0
        
        # Enhanced knowledge base
        self.educational_knowledge = self._initialize_knowledge_base()
        self.college_database = self._initialize_comprehensive_college_database()
        self.career_insights = self._initialize_career_insights()
        self.admission_strategies = self._initialize_admission_strategies()
        
        # Setup session management
        self.session_dir = self._create_session_directory()
        
        # Dynamic conversation system
        self.conversation_topics = {
            "introduction": ["personal_interests", "academic_background", "future_aspirations"],
            "exploration": ["career_exploration", "college_types", "location_preferences", "financial_planning"],
            "deep_dive": ["specific_programs", "admission_requirements", "scholarship_opportunities"],
            "recommendation": ["personalized_suggestions", "application_strategy", "next_steps"]
        }

    def _initialize_knowledge_base(self):
        """Comprehensive educational knowledge base"""
        return {
            "indian_education_system": {
                "school_boards": {
                    "CBSE": "Central Board of Secondary Education - Most widely accepted, good for competitive exams",
                    "ICSE": "Indian Certificate of Secondary Education - English-focused, comprehensive curriculum",
                    "State_Boards": "State-specific curricula, often more affordable and region-focused"
                },
                "streams": {
                    "Science": {
                        "PCM": "Physics, Chemistry, Mathematics - For Engineering, Technology, Pure Sciences",
                        "PCB": "Physics, Chemistry, Biology - For Medical, Life Sciences, Biotechnology",
                        "PCMB": "All four subjects - Keeps maximum options open"
                    },
                    "Commerce": "Accounting, Business Studies, Economics - For Business, Finance, Law",
                    "Arts/Humanities": "Literature, History, Psychology, Sociology - For Liberal Arts, Journalism, Civil Services"
                },
                "competitive_exams": {
                    "Engineering": {
                        "JEE_Main": "Joint Entrance Examination for NITs, IIITs, GFTIs",
                        "JEE_Advanced": "For IITs - taken after qualifying JEE Main",
                        "BITSAT": "For BITS Pilani campuses",
                        "VITEEE": "For VIT Universities",
                        "SRMJEEE": "For SRM Universities"
                    },
                    "Medical": {
                        "NEET": "National Eligibility cum Entrance Test for MBBS, BDS",
                        "AIIMS": "For AIIMS institutes (now merged with NEET)",
                        "JIPMER": "For JIPMER (now merged with NEET)"
                    },
                    "Management": {
                        "CAT": "Common Admission Test for IIMs",
                        "XAT": "Xavier Aptitude Test for XLRI and other institutes",
                        "SNAP": "Symbiosis National Aptitude Test",
                        "NMAT": "NMIMS Management Aptitude Test"
                    }
                }
            },
            "global_education": {
                "standardized_tests": {
                    "SAT": "Scholastic Assessment Test for US undergraduate admissions",
                    "GRE": "Graduate Record Examinations for US graduate schools",
                    "GMAT": "Graduate Management Admission Test for MBA programs",
                    "IELTS": "International English Language Testing System",
                    "TOEFL": "Test of English as a Foreign Language"
                },
                "popular_destinations": {
                    "USA": "World-class universities, research opportunities, diverse programs",
                    "Canada": "Excellent education, immigration opportunities, affordable compared to US",
                    "UK": "Prestigious universities, shorter degree duration, rich academic tradition",
                    "Australia": "High quality education, post-study work opportunities, multicultural environment",
                    "Germany": "Excellent engineering programs, low tuition fees, strong industry connections"
                }
            },
            "career_guidance": {
                "emerging_fields": [
                    "Artificial Intelligence & Machine Learning",
                    "Data Science & Analytics",
                    "Cybersecurity",
                    "Sustainable Energy & Environment",
                    "Biotechnology & Genetic Engineering",
                    "Digital Marketing & E-commerce",
                    "UI/UX Design",
                    "Cloud Computing & DevOps",
                    "Blockchain Technology",
                    "Mental Health & Counseling"
                ],
                "traditional_stable_fields": [
                    "Medicine & Healthcare",
                    "Engineering (Civil, Mechanical, Electrical)",
                    "Teaching & Education",
                    "Banking & Finance",
                    "Government Services",
                    "Law & Legal Services",
                    "Agriculture & Food Technology"
                ]
            }
        }

    def _initialize_comprehensive_college_database(self):
        """Extensive college database with detailed information"""
        return {
            "premier_engineering": [
                {
                    "name": "IIT Bombay",
                    "location": "Mumbai, Maharashtra",
                    "established": "1958",
                    "highlights": ["Top-ranked engineering institute", "Excellent placement record", "Strong alumni network", "World-class research facilities"],
                    "programs": ["B.Tech", "M.Tech", "Ph.D", "Dual Degree"],
                    "specialties": ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Aerospace Engineering"],
                    "admission": "JEE Advanced",
                    "approximate_fees": "₹2.5 lakhs per year",
                    "placement_stats": "Average CTC: ₹15-20 lakhs, Highest: ₹1+ crore",
                    "campus_life": "Vibrant technical festivals (Techfest, Mood Indigo), sports facilities, diverse student body"
                },
                {
                    "name": "IIT Delhi",
                    "location": "New Delhi",
                    "established": "1961",
                    "highlights": ["Premier technical institute", "Strong industry connections", "Research excellence", "Beautiful campus"],
                    "programs": ["B.Tech", "M.Tech", "MBA", "Ph.D"],
                    "specialties": ["Computer Science", "Engineering Physics", "Chemical Engineering", "Mathematics & Computing"],
                    "admission": "JEE Advanced",
                    "approximate_fees": "₹2.5 lakhs per year",
                    "placement_stats": "Average CTC: ₹18 lakhs, Top companies: Google, Microsoft, Goldman Sachs",
                    "unique_features": "Close to Delhi's business district, excellent metro connectivity"
                },
                {
                    "name": "BITS Pilani",
                    "location": "Pilani, Rajasthan (+ Goa, Hyderabad, Dubai)",
                    "established": "1964",
                    "highlights": ["Premier private engineering institute", "Industry-integrated programs", "Flexible curriculum", "Strong entrepreneurship culture"],
                    "programs": ["B.E.", "M.Sc.", "MBA", "Ph.D", "Dual Degree"],
                    "specialties": ["Computer Science", "Electronics", "Chemical Engineering", "Pharmacy"],
                    "admission": "BITSAT",
                    "approximate_fees": "₹4.5 lakhs per year",
                    "unique_features": ["Practice School program", "No reservation policy", "High-caliber peer group"]
                }
            ],
            "nits_iiits": [
                {
                    "name": "NIT Trichy",
                    "location": "Tiruchirappalli, Tamil Nadu",
                    "highlights": ["Top NIT", "Excellent placement record", "Strong technical culture", "Beautiful campus"],
                    "programs": ["B.Tech", "M.Tech", "MBA", "Ph.D"],
                    "admission": "JEE Main",
                    "approximate_fees": "₹1.8 lakhs per year",
                    "specialties": ["Computer Science", "Electronics", "Mechanical Engineering"]
                },
                {
                    "name": "IIIT Hyderabad",
                    "location": "Hyderabad, Telangana",
                    "highlights": ["Premier IT institute", "Research-focused", "Industry partnerships", "Small batch sizes"],
                    "programs": ["B.Tech", "M.Tech", "Ph.D", "Dual Degree"],
                    "admission": "JEE Main + IIIT Hyderabad test",
                    "approximate_fees": "₹2.5 lakhs per year",
                    "specialties": ["Computer Science", "Electronics", "Computational Natural Sciences"]
                }
            ],
            "medical_colleges": [
                {
                    "name": "AIIMS Delhi",
                    "location": "New Delhi",
                    "highlights": ["Premier medical institute", "Excellent clinical exposure", "Subsidized education", "Top-notch faculty"],
                    "programs": ["MBBS", "MD/MS", "Ph.D", "Nursing"],
                    "admission": "NEET",
                    "approximate_fees": "₹5,000 per year (highly subsidized)",
                    "unique_features": ["Attached to top hospital", "Research opportunities", "National importance"]
                },
                {
                    "name": "CMC Vellore",
                    "location": "Vellore, Tamil Nadu",
                    "highlights": ["Christian minority institution", "Excellent clinical training", "Service-oriented approach", "Strong ethical foundation"],
                    "programs": ["MBBS", "MD/MS", "Ph.D"],
                    "admission": "NEET + CMC entrance",
                    "approximate_fees": "₹3 lakhs per year",
                    "unique_features": ["Focus on rural healthcare", "Strong alumni network"]
                }
            ],
            "business_schools": [
                {
                    "name": "IIM Ahmedabad",
                    "location": "Ahmedabad, Gujarat",
                    "highlights": ["Top MBA school in India", "Excellent faculty", "Strong alumni network", "Case-study method"],
                    "programs": ["PGP (MBA)", "Executive MBA", "Ph.D"],
                    "admission": "CAT + Written Analysis + Personal Interview",
                    "approximate_fees": "₹25 lakhs for 2 years",
                    "placement_stats": "Average CTC: ₹25+ lakhs, Consulting and Finance focus"
                },
                {
                    "name": "ISB Hyderabad",
                    "location": "Hyderabad, Telangana",
                    "highlights": ["World-class infrastructure", "Global curriculum", "Strong industry connections", "One-year MBA"],
                    "programs": ["PGP", "Executive MBA", "Ph.D"],
                    "admission": "GMAT/GRE + Essays + Interview",
                    "approximate_fees": "₹36 lakhs for 1 year",
                    "unique_features": ["One-year intensive program", "International exchange programs"]
                }
            ],
            "liberal_arts_universities": [
                {
                    "name": "Ashoka University",
                    "location": "Sonipat, Haryana",
                    "highlights": ["Liberal arts education", "Small class sizes", "Interdisciplinary approach", "World-class faculty"],
                    "programs": ["UG Liberal Arts", "Masters programs", "Ph.D"],
                    "admission": "Aptitude test + Interview + Essays",
                    "approximate_fees": "₹8-12 lakhs per year",
                    "specialties": ["Economics", "Political Science", "Psychology", "Computer Science"]
                },
                {
                    "name": "Flame University",
                    "location": "Pune, Maharashtra",
                    "highlights": ["Liberal education model", "Industry exposure", "Creative programs", "Beautiful campus"],
                    "programs": ["Liberal Arts", "Design", "Business", "Communication"],
                    "admission": "FLAME entrance test + Interview",
                    "approximate_fees": "₹6-10 lakhs per year"
                }
            ]
        }

    def _initialize_career_insights(self):
        """Comprehensive career guidance information"""
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
                    },
                    "Cybersecurity Specialist": {
                        "description": "Protect organizations from digital threats",
                        "skills_required": ["Network security", "Ethical hacking", "Risk assessment"],
                        "education_path": ["B.Tech IT/CS + Security certifications", "Specialized cybersecurity programs"],
                        "salary_range": "₹5-35 lakhs per year",
                        "growth_prospects": "Excellent - Growing cyber threats, regulatory requirements"
                    }
                },
                "healthcare": {
                    "Doctor": {
                        "description": "Diagnose and treat medical conditions",
                        "skills_required": ["Medical knowledge", "Empathy", "Decision-making", "Communication"],
                        "education_path": ["MBBS + MD/MS specialization"],
                        "salary_range": "₹6-50+ lakhs per year (varies by specialization)",
                        "growth_prospects": "Stable - Always in demand, respect in society"
                    },
                    "Clinical Psychologist": {
                        "description": "Help people with mental health issues",
                        "skills_required": ["Psychology", "Counseling", "Empathy", "Communication"],
                        "education_path": ["BA/BSc Psychology + MA + M.Phil/Ph.D"],
                        "salary_range": "₹3-20 lakhs per year",
                        "growth_prospects": "High - Growing awareness of mental health"
                    }
                },
                "business": {
                    "Management Consultant": {
                        "description": "Help organizations solve complex business problems",
                        "skills_required": ["Analytical thinking", "Communication", "Industry knowledge"],
                        "education_path": ["Any graduation + MBA from top school", "Bachelor's + relevant experience"],
                        "salary_range": "₹8-40 lakhs per year",
                        "growth_prospects": "Excellent - High learning curve, global opportunities"
                    },
                    "Digital Marketing Manager": {
                        "description": "Promote products/services through digital channels",
                        "skills_required": ["Marketing", "Analytics", "Creativity", "Tech-savvy"],
                        "education_path": ["Any graduation + digital marketing certifications", "MBA in Marketing"],
                        "salary_range": "₹4-25 lakhs per year",
                        "growth_prospects": "Very High - Digital transformation of businesses"
                    }
                }
            },
            "entrepreneurship": {
                "startup_ecosystem": {
                    "current_trends": ["EdTech", "FinTech", "HealthTech", "E-commerce", "SaaS"],
                    "support_available": ["Incubators", "Angel investors", "Government schemes", "Mentorship programs"],
                    "skills_needed": ["Business acumen", "Leadership", "Risk-taking", "Networking"]
                }
            }
        }

    def _initialize_admission_strategies(self):
        """Comprehensive admission guidance"""
        return {
            "exam_preparation": {
                "JEE": {
                    "timeline": "Start from Class 11, intensive preparation for 2 years",
                    "key_subjects": ["Physics", "Chemistry", "Mathematics"],
                    "strategy": ["Strong conceptual foundation", "Regular practice", "Mock tests", "Time management"],
                    "resources": ["NCERT books", "Reference books (HC Verma, IE Irodov)", "Online platforms", "Coaching institutes"]
                },
                "NEET": {
                    "timeline": "Start from Class 11, consistent preparation",
                    "key_subjects": ["Physics", "Chemistry", "Biology"],
                    "strategy": ["NCERT mastery", "Previous year analysis", "Regular revision", "Biology memorization techniques"],
                    "resources": ["NCERT", "MTG publications", "Aakash modules", "Online test series"]
                }
            },
            "application_process": {
                "documentation": ["Academic transcripts", "Test scores", "Essays/SOPs", "Recommendation letters", "Certificates"],
                "timeline_management": "Start applications 6-8 months before deadlines",
                "essay_tips": ["Be authentic", "Show growth mindset", "Specific examples", "Connect to career goals"]
            },
            "financial_planning": {
                "scholarships": {
                    "government": ["National Merit Scholarship", "State government schemes", "Minority scholarships"],
                    "private": ["Tata Scholarships", "JN Tata Endowment", "Inlaks Scholarships"],
                    "institutional": "Most colleges offer merit and need-based scholarships"
                },
                "education_loans": {
                    "banks": "All major banks offer education loans",
                    "coverage": "Up to ₹1.5 crores for foreign studies",
                    "considerations": ["Interest rates", "Moratorium period", "Collateral requirements"]
                }
            }
        }

    def _create_session_directory(self):
        """Create session directory for saving conversations"""
        try:
            session_dir = Path('./counseling_sessions')
            session_dir.mkdir(parents=True, exist_ok=True)
            return session_dir
        except Exception as e:
            print(f"Directory creation error: {e}")
            return Path(tempfile.gettempdir()) / 'counseling_sessions'

    def _get_dynamic_system_prompt(self):
        """Generate dynamic system prompt based on conversation stage"""
        base_personality = f"""
        You are {self.name}, an expert AI college counselor with deep knowledge of Indian and global education systems. You have years of experience helping students navigate their educational journey.

        Your Core Qualities:
        - Warm, encouraging, and genuinely interested in each student's success
        - Highly knowledgeable about colleges, careers, and education trends
        - Patient listener who asks thoughtful follow-up questions
        - Provides specific, actionable advice rather than generic responses
        - Shares relevant insights and stories to help students understand options
        - Balances dreams with practical realities

        Your Knowledge Areas:
        - All major Indian colleges and universities (IITs, NITs, IIMs, medical colleges, liberal arts, etc.)
        - International education opportunities (US, Canada, UK, Australia, Germany, etc.)
        - Career trends and job market insights
        - Admission strategies and exam preparation
        - Scholarships and financial aid options
        - Industry connections and placement trends
        """

        stage_specific_guidance = {
            "introduction": """
            Current Focus: Getting to know the student as a person
            - Be curious about their interests, hobbies, and what excites them
            - Understand their family background and support system  
            - Learn about their current academic situation naturally
            - Share relevant insights about education trends when appropriate
            - Don't rush into detailed academic questioning
            """,
            
            "exploration": """
            Current Focus: Exploring possibilities and building awareness
            - Help them discover career options they might not know about
            - Share insights about emerging fields and job market trends
            - Discuss different types of colleges and educational approaches
            - Explain how their interests could translate into career paths
            - Provide context about various streams and specializations
            """,
            
            "deep_dive": """
            Current Focus: Detailed guidance on specific options
            - Provide comprehensive information about colleges and programs they're interested in
            - Explain admission requirements and preparation strategies
            - Discuss financial aspects including scholarships and loans
            - Share placement statistics and career outcomes
            - Help them understand the pros and cons of different choices
            """,
            
            "recommendation": """
            Current Focus: Personalized recommendations and action planning
            - Synthesize all information to provide tailored recommendations
            - Create a practical timeline for applications and preparation
            - Suggest specific next steps and resources
            - Help prioritize options based on their goals and constraints
            - Provide ongoing encouragement and support
            """
        }

        return f"{base_personality}\n\n{stage_specific_guidance.get(self.conversation.conversation_stage, stage_specific_guidance['introduction'])}"

    def _update_conversation_stage(self, user_message):
        """Intelligently update conversation stage based on dialogue flow"""
        message_lower = user_message.lower()
        
        # Analyze conversation depth and content
        if self.message_count <= 3:
            self.conversation.conversation_stage = "introduction"
        elif any(word in message_lower for word in ["interested in", "want to know about", "tell me about", "which college", "career options"]):
            if self.conversation.conversation_stage == "introduction":
                self.conversation.conversation_stage = "exploration"
            elif self.conversation.conversation_stage == "exploration":
                self.conversation.conversation_stage = "deep_dive"
        elif any(word in message_lower for word in ["recommend", "suggest", "what should i", "help me choose", "confused"]) and self.message_count > 5:
            self.conversation.conversation_stage = "recommendation"
        elif "specific" in message_lower or "details about" in message_lower:
            self.conversation.conversation_stage = "deep_dive"

    def _extract_conversation_insights(self, user_message):
        """Extract key insights from conversation naturally without rigid structure"""
        insights = []
        message_lower = user_message.lower()
        
        # Identify interests and preferences naturally
        if any(subject in message_lower for subject in ["computer", "programming", "software", "coding", "tech"]):
            insights.append("Shows interest in technology and programming")
        
        if any(word in message_lower for word in ["doctor", "medical", "medicine", "help people", "healthcare"]):
            insights.append("Interested in healthcare/medical field")
        
        if any(word in message_lower for word in ["business", "entrepreneur", "startup", "management", "finance"]):
            insights.append("Shows business/entrepreneurial inclination")
        
        if any(word in message_lower for word in ["creative", "design", "art", "write", "draw"]):
            insights.append("Has creative interests")
        
        # Academic context
        if any(grade in message_lower for grade in ["12th", "class 12", "grade 12", "senior"]):
            insights.append("Currently in final year of school")
        
        if any(exam in message_lower for exam in ["jee", "neet", "sat", "boards"]):
            insights.append(f"Preparing for competitive exams")
        
        # Add insights to conversation context
        for insight in insights:
            if insight not in self.conversation.insights_discovered:
                self.conversation.insights_discovered.append(insight)
        
        # Store context flexibly
        context_updates = {}
        
        # Look for budget mentions
        budget_keywords = ["budget", "afford", "expensive", "cost", "fees", "money"]
        if any(word in message_lower for word in budget_keywords):
            context_updates["budget_discussed"] = True
        
        # Look for location preferences
        location_keywords = ["prefer", "want to go", "location", "city", "state", "abroad", "foreign"]
        if any(word in message_lower for word in location_keywords):
            context_updates["location_preferences_mentioned"] = True
        
        # Update context
        self.conversation.student_context.update(context_updates)

    def _get_relevant_information(self, user_message):
        """Get relevant information from knowledge base based on user query"""
        message_lower = user_message.lower()
        relevant_info = []
        
        # Engineering-related queries
        if any(word in message_lower for word in ["engineering", "iit", "nit", "jee", "bits", "technical"]):
            relevant_info.append("engineering_colleges")
            
        # Medical-related queries  
        if any(word in message_lower for word in ["medical", "doctor", "neet", "mbbs", "aiims", "medicine"]):
            relevant_info.append("medical_colleges")
            
        # Business/MBA related
        if any(word in message_lower for word in ["mba", "management", "business", "iim", "cat"]):
            relevant_info.append("business_schools")
            
        # Career guidance
        if any(word in message_lower for word in ["career", "job", "future", "opportunities", "salary"]):
            relevant_info.append("career_insights")
            
        # International education
        if any(word in message_lower for word in ["abroad", "international", "us", "uk", "canada", "australia", "foreign"]):
            relevant_info.append("international_education")

        return relevant_info

    def _generate_informative_context(self, user_message, relevant_topics):
        """Generate rich contextual information to make the bot more informative"""
        context_info = []
        
        for topic in relevant_topics:
            if topic == "engineering_colleges":
                context_info.append("""
                ENGINEERING EDUCATION CONTEXT:
                India has a robust engineering education system with over 4000 engineering colleges. The hierarchy typically is:
                - IITs (23 institutes) - Premier institutes with global recognition
                - NITs (31 institutes) - Excellent government institutes with regional diversity  
                - IIITs (25 institutes) - Focused on IT and allied areas
                - State Government colleges - Good quality, affordable education
                - Private colleges - Varying quality, some excellent ones like BITS, VIT, Manipal
                
                Current industry demands: AI/ML, Data Science, Cybersecurity, Cloud Computing, IoT
                Placement trends: Average packages have increased 15-20% in top tier colleges
                """)
                
            elif topic == "medical_colleges":
                context_info.append("""
                MEDICAL EDUCATION CONTEXT:
                India produces the largest number of doctors globally but has intense competition:
                - AIIMS (Multiple locations) - Premier medical institutes, highly subsidized
                - Government medical colleges - Affordable, good clinical exposure
                - Private medical colleges - Expensive (₹50 lakhs - ₹1.5 crore) but good infrastructure
                
                Specialization trends: High demand for radiology, anesthesia, dermatology
                Alternative paths: AYUSH (Ayurveda, Homeopathy), Physiotherapy, Medical Technology
                International opportunities: USMLE for US practice, PLAB for UK
                """)
                
            elif topic == "business_schools":
                context_info.append("""
                BUSINESS EDUCATION CONTEXT:
                MBA landscape in India is highly competitive with diverse opportunities:
                - IIMs (20 institutes) - Premier business schools with excellent ROI
                - Tier-1 private schools - ISB, XLRI, FMS, JBIMS offer excellent placements
                - Sectoral MBA programs - Hospital management, Rural management, Family business
                
                Industry trends: Consulting, Finance, and Product Management roles are hot
                Salary insights: Top IIMs average ₹25+ lakhs, Tier-1 schools ₹15-20 lakhs
                Alternative: Executive MBA for working professionals
                """)
                
            elif topic == "career_insights":
                context_info.append("""
                CURRENT JOB MARKET INSIGHTS:
                - Technology sector continues to dominate with 30%+ growth in AI/Data Science roles
                - Healthcare professionals in high demand post-pandemic
                - Sustainability and green energy creating new career paths
                - Creator economy and digital marketing booming
                - Traditional engineering branches evolving with automation and IoT
                
                Future-proof skills: Critical thinking, adaptability, digital literacy, emotional intelligence
                Emerging job titles: Prompt Engineers, Sustainability Analysts, User Experience Researchers
                """)
                
            elif topic == "international_education":
                context_info.append("""
                INTERNATIONAL EDUCATION TRENDS:
                - USA: Still most popular, but visa policies affect decisions. Strong STEM programs.
                - Canada: Growing preference due to immigration-friendly policies
                - UK: Shorter degree duration, work visa improvements attracting students
                - Germany: Free/low-cost education, strong in engineering and technology
                - Australia: Points-based immigration system, excellent quality of life
                
                Cost comparison: Germany/France (₹15-20 lakhs total) vs USA (₹70+ lakhs)
                Scholarship opportunities: Fulbright, DAAD, Chevening, Australia Awards
                """)
        
        return "\n".join(context_info)

    def chat(self, message, history):
        """Enhanced chat function with dynamic knowledge sharing"""
        self.message_count += 1
        print(f"💬 Message {self.message_count}: {message[:50]}...")
        
        # Update conversation stage dynamically
        self._update_conversation_stage(message)
        
        # Extract insights naturally
        self._extract_conversation_insights(message)
        
        # Get relevant information for enriched response
        relevant_topics = self._get_relevant_information(message)
        context_info = self._generate_informative_context(message, relevant_topics)
        
        # Add to conversation history
        self.conversation.conversation_flow.append({
            "user": message,
            "timestamp": datetime.now().isoformat(),
            "stage": self.conversation.conversation_stage
        })
        
        # Prepare enhanced system prompt
        system_prompt = self._get_dynamic_system_prompt()
        
        # Add contextual information if relevant
        if context_info:
            system_prompt += f"\n\nRELEVANT CONTEXT FOR THIS CONVERSATION:\n{context_info}"
        
        # Add insights about the student
        if self.conversation.insights_discovered:
            insights_text = "\n".join(self.conversation.insights_discovered)
            system_prompt += f"\n\nSTUDENT INSIGHTS DISCOVERED:\n{insights_text}"
        
        # Prepare conversation messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Add recent conversation history for context (last 6 messages)
        recent_flow = self.conversation.conversation_flow[-3:]
        for entry in recent_flow[:-1]:  # Exclude current message
            if "assistant_response" in entry:
                messages.insert(-1, {"role": "assistant", "content": entry["assistant_response"]})
                messages.insert(-1, {"role": "user", "content": entry["user"]})
        
        try:
            # Generate response with enhanced context
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=1000,
                frequency_penalty=0.3,
                presence_penalty=0.2
            )
            
            assistant_response = response.choices[0].message.content
            
            # Store assistant response
            self.conversation.conversation_flow[-1]["assistant_response"] = assistant_response
            self.conversation.last_updated = datetime.now().isoformat()
            
            # Save conversation periodically
            if self.message_count % 3 == 0:  # Save every 3 messages
                self._save_conversation()
                
        except Exception as e:
            assistant_response = f"I apologize, but I encountered a technical issue. Let me help you in a different way - could you tell me more about what specific aspect of college selection you'd like to discuss? I have extensive knowledge about various colleges and career paths that I'd love to share with you!"
            print(f"❌ Chat error: {e}")
        
        return assistant_response

    def _save_conversation(self):
        """Save conversation to file"""
        try:
            filename = self.session_dir / f"session_{self.conversation.conversation_id}.json"
            conversation_data = self.conversation.model_dump()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            print(f"❌ Save error: {e}")

    def get_conversation_summary(self):
        """Generate a summary of the counseling session"""
        try:
            insights = self.conversation.insights_discovered
            context = self.conversation.student_context
            stage = self.conversation.conversation_stage
            
            summary = {
                "session_id": self.conversation.conversation_id,
                "counseling_stage": stage,
                "total_interactions": len(self.conversation.conversation_flow),
                "key_insights": insights,
                "student_context": context,
                "recommendations_provided": len(self.conversation.recommendations_given),
                "session_duration": f"{self.message_count} messages exchanged",
                "last_updated": self.conversation.last_updated
            }
            
            return json.dumps(summary, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": f"Could not generate summary: {str(e)}"}, indent=2)

    def provide_specific_college_info(self, college_category, college_name=None):
        """Provide detailed information about specific colleges"""
        college_info = ""
        
        if college_category in self.college_database:
            colleges = self.college_database[college_category]
            
            if college_name:
                # Find specific college
                for college in colleges:
                    if college_name.lower() in college["name"].lower():
                        college_info = f"""
**{college['name']}** ({college['location']})

🎯 **Key Highlights:**
{chr(10).join(['• ' + highlight for highlight in college['highlights']])}

📚 **Programs Offered:** {', '.join(college['programs'])}

🏆 **Specialties:** {', '.join(college.get('specialties', ['Various programs available']))}

💰 **Approximate Fees:** {college['approximate_fees']}

📊 **Admission Process:** {college['admission']}

{('📈 **Placement Statistics:** ' + college['placement_stats']) if 'placement_stats' in college else ''}

{('🏫 **Campus Life:** ' + college['campus_life']) if 'campus_life' in college else ''}

{('✨ **Unique Features:** ' + college['unique_features']) if 'unique_features' in college else ''}
"""
                        break
            else:
                # Provide overview of category
                college_info = f"**{college_category.replace('_', ' ').title()} Colleges:**\n\n"
                for college in colleges[:3]:  # Show first 3 colleges
                    college_info += f"• **{college['name']}** - {college['location']}\n"
                    college_info += f"  Fees: {college['approximate_fees']} | Admission: {college['admission']}\n\n"
        
        return college_info

    def get_career_guidance(self, field=None):
        """Provide detailed career guidance"""
        if field and field in self.career_insights["high_growth_careers"]:
            careers = self.career_insights["high_growth_careers"][field]
            guidance = f"**{field.title()} Career Options:**\n\n"
            
            for career, details in careers.items():
                guidance += f"**{career}:**\n"
                guidance += f"📝 {details['description']}\n"
                guidance += f"🛠️ **Skills:** {', '.join(details['skills_required'])}\n"
                guidance += f"🎓 **Education:** {', '.join(details['education_path'])}\n"
                guidance += f"💰 **Salary:** {details['salary_range']}\n"
                guidance += f"📈 **Growth:** {details['growth_prospects']}\n\n"
            
            return guidance
        else:
            # General career guidance
            return """
**High-Growth Career Fields:**

🖥️ **Technology:** Software Engineering, Data Science, Cybersecurity, AI/ML
💊 **Healthcare:** Medicine, Psychology, Healthcare Technology, Biotechnology  
💼 **Business:** Management Consulting, Digital Marketing, Product Management
🎨 **Creative:** UX/UI Design, Content Creation, Digital Media
🌱 **Emerging:** Sustainability, EdTech, FinTech, Social Entrepreneurship

Each field offers unique opportunities and growth potential. Would you like me to dive deeper into any specific area?
"""

    def reset_conversation(self):
        """Reset for a new counseling session"""
        self.conversation = StudentConversation()
        self.message_count = 0
        print("🔄 New counseling session started")


def create_dynamic_chatbot_interface(api_key):
    """Create enhanced Gradio interface for the dynamic counselor"""
    if not api_key:
        raise ValueError("API key must be provided to create the chatbot interface")
    
    counselor = DynamicCollegeCounselorBot(name="Lauren", api_key=api_key)
    
    with gr.Blocks(title="Lauren - Dynamic AI College Counselor", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🌟 Lauren - Your Dynamic AI College Counselor")
        gr.Markdown("""
        Hi! I'm Lauren, your knowledgeable AI college counselor with deep expertise in Indian and global education systems. 
        
        I'm here to have meaningful conversations about your educational journey, share comprehensive insights about colleges and careers, 
        and help you make informed decisions. I adapt to your interests and provide detailed, relevant information as we chat!
        
        Just start by introducing yourself - I'm excited to learn about your aspirations! 🚀
        """)
        
        # Main chat interface
        chatbot = gr.Chatbot(height=650, show_copy_button=True, type="messages")
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Hi Lauren! I'm exploring college options and would love your guidance...",
                container=False,
                scale=7
            )
            submit = gr.Button("Send", variant="primary", scale=1)
        
        # Enhanced controls
        with gr.Row():
            clear = gr.Button("🔄 New Session", scale=1)
            download_btn = gr.Button("📋 Download Summary", variant="secondary", scale=1)
            college_info_btn = gr.Button("🏫 Ask About Colleges", scale=1)
            career_info_btn = gr.Button("💼 Career Guidance", scale=1)
        
        # Quick info buttons
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("**Quick Info:**")
                engineering_btn = gr.Button("🔧 Engineering Colleges", size="sm")
                medical_btn = gr.Button("⚕️ Medical Colleges", size="sm")
                business_btn = gr.Button("💼 Business Schools", size="sm")
            
            with gr.Column(scale=1):
                gr.Markdown("**Career Fields:**")
                tech_careers_btn = gr.Button("💻 Technology Careers", size="sm")
                health_careers_btn = gr.Button("🏥 Healthcare Careers", size="sm")
                business_careers_btn = gr.Button("📈 Business Careers", size="sm")
        
        # Status and downloads
        status_display = gr.Markdown("💫 **Status:** Ready for an insightful conversation! Tell me about yourself.")
        download_file = gr.File(label="Session Summary", visible=False)
        
        # Enhanced initial greeting
        initial_greeting = {
            "role": "assistant", 
            "content": """
Hi there! 👋 I'm Lauren, your AI college counselor, and I'm genuinely excited to help you navigate your educational journey!

I have extensive knowledge about:
🎓 **Indian Education**: IITs, NITs, IIMs, Medical colleges, Liberal arts universities, and 4000+ engineering colleges
🌍 **Global Opportunities**: US, UK, Canada, Australia, Germany - admissions, scholarships, and career prospects  
💼 **Career Insights**: Emerging fields, salary trends, industry demands, and future job market
📚 **Admission Strategies**: Exam preparation, application processes, essays, and interviews

I'm not just here to collect information from you - I'm here to share my knowledge, provide insights, and have meaningful conversations about your future!

So, let's start! What's your name, and what's currently on your mind about your educational journey? Are you exploring college options, thinking about career paths, or maybe considering studying abroad? I'm all ears! 😊
"""
        }

        def respond(message, chat_history):
            if not message.strip():
                return chat_history, gr.update(), gr.update(visible=False)
            
            response = counselor.chat(message, chat_history)
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})
            
            # Update status
            stage_messages = {
                "introduction": "👋 Getting to know you - sharing insights as we chat!",
                "exploration": "🔍 Exploring possibilities together - I'm sharing relevant knowledge!",
                "deep_dive": "🎯 Diving deep into specific options - providing detailed guidance!",
                "recommendation": "✨ Crafting personalized recommendations - almost ready for your summary!"
            }
            
            status_text = f"💫 **Status:** {stage_messages.get(counselor.conversation.conversation_stage, 'Having a great educational conversation!')}"
            status_display_value = gr.update(value=status_text)
            
            # Show download button after substantial conversation
            download_visibility = gr.update(visible=(counselor.message_count >= 5))
            
            return chat_history, status_display_value, download_visibility

        def get_college_info(chat_history, category):
            info = counselor.provide_specific_college_info(category)
            if info:
                chat_history.append({"role": "assistant", "content": info})
            return chat_history

        def get_career_info(chat_history, field):
            info = counselor.get_career_guidance(field)
            chat_history.append({"role": "assistant", "content": info})
            return chat_history

        def download_summary():
            summary = counselor.get_conversation_summary()
            temp_file = counselor.session_dir / f"session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            return gr.update(value=str(temp_file), visible=True)

        def new_session():
            counselor.reset_conversation()
            return [initial_greeting], gr.update(visible=False), gr.update(value="💫 **Status:** Fresh start! Ready for a new educational conversation.")

        def clear_input():
            return ""

        # Event handlers
        submit.click(respond, [msg, chatbot], [chatbot, status_display, download_btn]).then(clear_input, outputs=[msg])
        msg.submit(respond, [msg, chatbot], [chatbot, status_display, download_btn]).then(clear_input, outputs=[msg])
        
        # Quick action buttons
        engineering_btn.click(lambda h: get_college_info(h, "premier_engineering"), [chatbot], [chatbot])
        medical_btn.click(lambda h: get_college_info(h, "medical_colleges"), [chatbot], [chatbot])
        business_btn.click(lambda h: get_college_info(h, "business_schools"), [chatbot], [chatbot])
        
        tech_careers_btn.click(lambda h: get_career_info(h, "technology"), [chatbot], [chatbot])
        health_careers_btn.click(lambda h: get_career_info(h, "healthcare"), [chatbot], [chatbot])
        business_careers_btn.click(lambda h: get_career_info(h, "business"), [chatbot], [chatbot])
        
        # Main controls
        clear.click(new_session, outputs=[chatbot, download_file, status_display])
        download_btn.click(download_summary, outputs=[download_file])
        
        # Set initial greeting
        chatbot.value = [initial_greeting]
    
    return app


# Example usage
if __name__ == "__main__":
    # Replace with your actual OpenAI API key
    YOUR_API_KEY = "Enter your API Key Here"
    
    app = create_dynamic_chatbot_interface(YOUR_API_KEY)
    app.launch(debug=True, share=True)