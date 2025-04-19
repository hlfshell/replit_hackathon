from typing import Dict, List, Optional, Any
from uuid import uuid4

from app.backend.models.rating import Rating
from app.backend.store.db import Pool


class RatingStore:
    """
    Store class for handling CRUD operations for Rating objects.
    """

    def __init__(self, db_pool: Pool):
        """
        Initialize the RatingStore with a database pool.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.table_name = "rating"

    def create(self, rating: Rating) -> Optional[str]:
        """
        Create a new rating record in the database.

        Args:
            rating: Rating object to create

        Returns:
            ID of the created rating if successful, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = rating.to_dict()
            
            # Convert personality and ad fields to their respective IDs
            data["personality_id"] = data.pop("personality")
            data["ad_id"] = data.pop("ad")
            
            return transaction.insert(self.table_name, data)

    def get(self, rating_id: str) -> Optional[Rating]:
        """
        Get a rating by ID.

        Args:
            rating_id: ID of the rating to retrieve

        Returns:
            Rating object if found, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT 
                    r.id, 
                    r.personality_id as personality, 
                    r.ad_id as ad, 
                    r.thought, 
                    r.emotional_response, 
                    r.emotions, 
                    r.effectiveness
                FROM {self.table_name} r
                WHERE r.id = %s
            """
            results = transaction.query(query, (rating_id,))
            if results:
                return Rating.from_dict(results[0])
            return None

    def update(self, rating: Rating) -> bool:
        """
        Update an existing rating record.

        Args:
            rating: Rating object with updated values

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = rating.to_dict()
            rating_id = data.pop("id")
            
            # Convert personality and ad fields to their respective IDs
            data["personality_id"] = data.pop("personality")
            data["ad_id"] = data.pop("ad")
            
            rows_affected = transaction.update(
                self.table_name, 
                data, 
                "id = %s", 
                (rating_id,)
            )
            return rows_affected > 0

    def delete(self, rating_id: str) -> bool:
        """
        Delete a rating by ID.

        Args:
            rating_id: ID of the rating to delete

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            rows_affected = transaction.delete(
                self.table_name, 
                "id = %s", 
                (rating_id,)
            )
            return rows_affected > 0

    def list_all(self) -> List[Rating]:
        """
        List all ratings.

        Returns:
            List of Rating objects
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT 
                    r.id, 
                    r.personality_id as personality, 
                    r.ad_id as ad, 
                    r.thought, 
                    r.emotional_response, 
                    r.emotions, 
                    r.effectiveness
                FROM {self.table_name} r
            """
            results = transaction.query(query)
            return [Rating.from_dict(result) for result in results]

    def get_ratings_by_personality(self, personality_id: str) -> List[Rating]:
        """
        Get all ratings for a specific personality.

        Args:
            personality_id: ID of the personality

        Returns:
            List of Rating objects
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT 
                    r.id, 
                    r.personality_id as personality, 
                    r.ad_id as ad, 
                    r.thought, 
                    r.emotional_response, 
                    r.emotions, 
                    r.effectiveness
                FROM {self.table_name} r
                WHERE r.personality_id = %s
            """
            results = transaction.query(query, (personality_id,))
            return [Rating.from_dict(result) for result in results]

    def get_ratings_by_ad(self, ad_id: str) -> List[Rating]:
        """
        Get all ratings for a specific ad.

        Args:
            ad_id: ID of the ad

        Returns:
            List of Rating objects
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT 
                    r.id, 
                    r.personality_id as personality, 
                    r.ad_id as ad, 
                    r.thought, 
                    r.emotional_response, 
                    r.emotions, 
                    r.effectiveness
                FROM {self.table_name} r
                WHERE r.ad_id = %s
            """
            results = transaction.query(query, (ad_id,))
            return [Rating.from_dict(result) for result in results]

    def get_ratings_by_effectiveness(self, effectiveness: str) -> List[Rating]:
        """
        Get all ratings with a specific effectiveness value.

        Args:
            effectiveness: Effectiveness value to search for

        Returns:
            List of Rating objects
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT 
                    r.id, 
                    r.personality_id as personality, 
                    r.ad_id as ad, 
                    r.thought, 
                    r.emotional_response, 
                    r.emotions, 
                    r.effectiveness
                FROM {self.table_name} r
                WHERE r.effectiveness = %s
            """
            results = transaction.query(query, (effectiveness,))
            return [Rating.from_dict(result) for result in results]
