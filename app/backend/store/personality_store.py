from typing import Dict, List, Optional, Any
from uuid import uuid4

from app.backend.models.personality import Personality
from app.backend.store.db import Pool


class PersonalityStore:
    """
    Store class for handling CRUD operations for Personality objects.
    """

    def __init__(self, db_pool: Pool):
        """
        Initialize the PersonalityStore with a database pool.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.table_name = "personality"

    def create(self, personality: Personality) -> Optional[str]:
        """
        Create a new personality record in the database.

        Args:
            personality: Personality object to create

        Returns:
            ID of the created personality if successful, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = personality.to_dict()
            return transaction.insert(self.table_name, data)

    def get(self, personality_id: str) -> Optional[Personality]:
        """
        Get a personality by ID.

        Args:
            personality_id: ID of the personality to retrieve

        Returns:
            Personality object if found, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            result = transaction.get_by_id(self.table_name, personality_id)
            if result:
                return Personality.from_dict(result)
            return None

    def update(self, personality: Personality) -> bool:
        """
        Update an existing personality record.

        Args:
            personality: Personality object with updated values

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = personality.to_dict()
            personality_id = data.pop("id")
            rows_affected = transaction.update(
                self.table_name, 
                data, 
                "id = %s", 
                (personality_id,)
            )
            return rows_affected > 0

    def delete(self, personality_id: str) -> bool:
        """
        Delete a personality by ID.

        Args:
            personality_id: ID of the personality to delete

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            rows_affected = transaction.delete(
                self.table_name, 
                "id = %s", 
                (personality_id,)
            )
            return rows_affected > 0

    def list_all(self) -> List[Personality]:
        """
        List all personalities.

        Returns:
            List of Personality objects
        """
        with self.db_pool.get_transaction() as transaction:
            results = transaction.query(f"SELECT * FROM {self.table_name}")
            return [Personality.from_dict(result) for result in results]

    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Personality]:
        """
        Find personalities matching the given criteria.

        Args:
            criteria: Dictionary of field names and values to match

        Returns:
            List of matching Personality objects
        """
        if not criteria:
            return self.list_all()

        conditions = []
        params = []
        
        for key, value in criteria.items():
            if isinstance(value, list):
                # Handle array fields
                conditions.append(f"{key} @> %s")
                params.append(value)
            else:
                conditions.append(f"{key} = %s")
                params.append(value)
                
        where_clause = " AND ".join(conditions)
        
        with self.db_pool.get_transaction() as transaction:
            query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
            results = transaction.query(query, tuple(params))
            return [Personality.from_dict(result) for result in results]
