from app.backend.store.db import Pool
from app.backend.store.ad_store import AdStore
from app.backend.store.category_store import CategoryStore
from app.backend.store.personality_store import PersonalityStore
from app.backend.store.rating_store import RatingStore


class Store:
    """
    Main store class that provides access to all individual stores.
    This class serves as a facade for all database operations.
    """

    def __init__(self, db_pool: Pool):
        """
        Initialize the Store with a database pool and create all individual stores.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        
        # Initialize all individual stores
        self.ad = AdStore(db_pool)
        self.category = CategoryStore(db_pool)
        self.personality = PersonalityStore(db_pool)
        self.rating = RatingStore(db_pool)
    