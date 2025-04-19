from uuid import uuid4
from typing import Optional, List, Dict, Any


class CategoryAssignment():

    def __init__(
        self,
        personality: str,
        category: str,
        id: Optional[str] = str(uuid4()),
    ):
        self.id = id
        self.personality = personality
        self.category = category

    def to_dict(self):
        return {
            "id": self.id,
            "personality": self.personality,
            "category": self.category,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
    