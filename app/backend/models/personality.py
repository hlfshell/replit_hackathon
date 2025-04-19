from uuid import uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime

class Personality:

    def __init__(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        location: Optional[str] = None,
        education_level: Optional[str] = None,
        marital_status: Optional[str] = None,
        children: Optional[int] = None,

        # Professional Details
        occupation: Optional[str] = None,
        job_title: Optional[str] = None,
        industry: Optional[str] = None,
        income: Optional[float] = None,
        seniority_level: Optional[str] = None,

        # Psychographics
        personality_traits: Optional[List[str]] = None,
        values: Optional[List[str]] = None,
        attitudes: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        lifestyle: Optional[List[str]] = None,
        habits: Optional[List[str]] = None,
        frustrations: Optional[List[str]] = None,

        # One sentence summary
        summary: Optional[str] = None,

        id: Optional[str] = str(uuid4()),

        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.location = location
        self.education_level = education_level
        self.marital_status = marital_status
        self.children = children
        self.occupation = occupation
        self.job_title = job_title
        self.industry = industry
        self.income = income
        self.seniority_level = seniority_level
        self.personality_traits = personality_traits
        self.values = values
        self.attitudes = attitudes
        self.interests = interests
        self.lifestyle = lifestyle
        self.habits = habits
        self.frustrations = frustrations
        self.summary = summary
        self.created_at = created_at
        self.updated_at = updated_at    
                
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "location": self.location,
            "education_level": self.education_level,
            "marital_status": self.marital_status,
            "occupation": self.occupation,
            "job_title": self.job_title,
            "industry": self.industry,
            "income": self.income,
            "seniority_level": self.seniority_level,
            "personality_traits": self.personality_traits,
            "values": self.values,
            "children": self.children,
            "attitudes": self.attitudes,
            "interests": self.interests,
            "lifestyle": self.lifestyle,
            "habits": self.habits,
            "frustrations": self.frustrations,
            "summary": self.summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)