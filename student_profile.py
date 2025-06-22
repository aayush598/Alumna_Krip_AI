from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

from utils import convert_budget, normalize_gender

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
    def convert_budget_field(cls, v):
        return convert_budget(v)

    @field_validator('gender', mode='before')
    def normalize_gender_field(cls, v):
        return normalize_gender(v)
