from typing import Dict, List, Optional, Any

from app.backend.models.ad import Ad
from app.backend.store.db import Pool


class AdStore:
    """
    Store class for handling CRUD operations for Ad objects.
    """

    def __init__(self, db_pool: Pool):
        """
        Initialize the AdStore with a database pool.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.table_name = "ad"

    def create(self, ad: Ad) -> Optional[str]:
        """
        Create a new ad record in the database.

        Args:
            ad: Ad object to create

        Returns:
            ID of the created ad if successful, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = ad.to_dict()
            return transaction.insert(self.table_name, data)

    def get(self, ad_id: str) -> Optional[Ad]:
        """
        Get an ad by ID.

        Args:
            ad_id: ID of the ad to retrieve

        Returns:
            Ad object if found, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            result = transaction.get_by_id(self.table_name, ad_id)
            if result:
                return Ad.from_dict(result)
            return None

    def update(self, ad: Ad) -> bool:
        """
        Update an existing ad record.

        Args:
            ad: Ad object with updated values

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = ad.to_dict()
            ad_id = data.pop("id")
            rows_affected = transaction.update(
                self.table_name, 
                data, 
                "id = %s", 
                (ad_id,)
            )
            return rows_affected > 0

    def delete(self, ad_id: str) -> bool:
        """
        Delete an ad by ID.

        Args:
            ad_id: ID of the ad to delete

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            rows_affected = transaction.delete(
                self.table_name, 
                "id = %s", 
                (ad_id,)
            )
            return rows_affected > 0

    def list_all(self) -> List[Ad]:
        """
        List all ads.

        Returns:
            List of Ad objects
        """
        with self.db_pool.get_transaction() as transaction:
            results = transaction.query(f"SELECT * FROM {self.table_name}")
            return [Ad.from_dict(result) for result in results]

    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Ad]:
        """
        Find ads matching the given criteria.

        Args:
            criteria: Dictionary of field names and values to match

        Returns:
            List of matching Ad objects
        """
        if not criteria:
            return self.list_all()

        conditions = []
        params = []
        
        for key, value in criteria.items():
            conditions.append(f"{key} = %s")
            params.append(value)
                
        where_clause = " AND ".join(conditions)
        
        with self.db_pool.get_transaction() as transaction:
            query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
            results = transaction.query(query, tuple(params))
            return [Ad.from_dict(result) for result in results]
