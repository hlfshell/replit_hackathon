

from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime


class Ad():

    def __init__(

        self,
        image: Optional[str] = None,
        copy: Optional[str] = None,
        id: Optional[str] = str(uuid4()),
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        if not image and not copy:
            raise ValueError("At least one of image or copy must be provided")
        self.image = image
        self.copy = copy
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "image": self.image,
            "copy": self.copy,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
