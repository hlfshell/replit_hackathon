
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime


class Rating():
    
    def __init__(
        self,
        personality: str,
        ad: str,
        thought: str,
        emotional_response: str,
        emotions: str,
        effectiveness: str,
        id: Optional[str] = str(uuid4()),
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.personality = personality
        self.ad = ad
        self.thought = thought
        self.emotional_response = emotional_response
        self.emotions = emotions
        self.effectiveness = effectiveness
        self.created_at = created_at
        self.updated_at = updated_at
        
    def to_dict(self):
        return {
            "id": self.id,
            "personality": self.personality,
            "ad": self.ad,
            "thought": self.thought,
            "emotional_response": self.emotional_response,
            "emotions": self.emotions,
            "effectiveness": self.effectiveness,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)