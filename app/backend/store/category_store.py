from typing import Dict, List, Optional, Any
from uuid import uuid4

from app.backend.models.category_assignment import CategoryAssignment
from app.backend.store.db import Pool


class CategoryStore:
    """
    Store class for handling CRUD operations for Category and CategoryAssignment objects.
    """

    def __init__(self, db_pool: Pool):
        """
        Initialize the CategoryStore with a database pool.

        Args:
            db_pool: Database connection pool
        """
        self.db_pool = db_pool
        self.category_table = "category"
        self.assignment_table = "category_assignment"

    # Category CRUD operations
    def create_category(self, name: str, description: Optional[str] = None) -> Optional[str]:
        """
        Create a new category.

        Args:
            name: Name of the category
            description: Optional description of the category

        Returns:
            ID of the created category if successful, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = {
                "id": str(uuid4()),
                "name": name,
                "description": description
            }
            return transaction.insert(self.category_table, data)

    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by ID.

        Args:
            category_id: ID of the category to retrieve

        Returns:
            Category data if found, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            return transaction.get_by_id(self.category_table, category_id)

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a category by name.

        Args:
            name: Name of the category to retrieve

        Returns:
            Category data if found, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            results = transaction.query(
                f"SELECT * FROM {self.category_table} WHERE name = %s", 
                (name,)
            )
            return results[0] if results else None

    def update_category(self, category_id: str, name: str, description: Optional[str] = None) -> bool:
        """
        Update an existing category.

        Args:
            category_id: ID of the category to update
            name: New name for the category
            description: New description for the category

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            data = {"name": name}
            if description is not None:
                data["description"] = description
                
            rows_affected = transaction.update(
                self.category_table, 
                data, 
                "id = %s", 
                (category_id,)
            )
            return rows_affected > 0

    def delete_category(self, category_id: str) -> bool:
        """
        Delete a category by ID.

        Args:
            category_id: ID of the category to delete

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            # This will cascade delete all assignments
            rows_affected = transaction.delete(
                self.category_table, 
                "id = %s", 
                (category_id,)
            )
            return rows_affected > 0

    def list_all_categories(self) -> List[Dict[str, Any]]:
        """
        List all categories.

        Returns:
            List of category data dictionaries
        """
        with self.db_pool.get_transaction() as transaction:
            return transaction.query(f"SELECT * FROM {self.category_table}")

    # CategoryAssignment CRUD operations
    def create_assignment(self, assignment: CategoryAssignment) -> Optional[str]:
        """
        Create a new category assignment.

        Args:
            assignment: CategoryAssignment object to create

        Returns:
            ID of the created assignment if successful, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            # First, ensure the category exists or get its ID
            category_data = self.get_category_by_name(assignment.category)
            if not category_data:
                # Create the category if it doesn't exist
                category_id = self.create_category(assignment.category)
                if not category_id:
                    return None
            else:
                category_id = category_data["id"]
                
            # Now create the assignment with the category ID
            data = {
                "id": assignment.id,
                "personality_id": assignment.personality,
                "category_id": category_id
            }
            return transaction.insert(self.assignment_table, data)

    def get_assignment(self, assignment_id: str) -> Optional[CategoryAssignment]:
        """
        Get a category assignment by ID.

        Args:
            assignment_id: ID of the assignment to retrieve

        Returns:
            CategoryAssignment object if found, None otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT a.id, a.personality_id as personality, c.name as category
                FROM {self.assignment_table} a
                JOIN {self.category_table} c ON a.category_id = c.id
                WHERE a.id = %s
            """
            results = transaction.query(query, (assignment_id,))
            if results:
                return CategoryAssignment.from_dict(results[0])
            return None

    def delete_assignment(self, assignment_id: str) -> bool:
        """
        Delete a category assignment by ID.

        Args:
            assignment_id: ID of the assignment to delete

        Returns:
            True if successful, False otherwise
        """
        with self.db_pool.get_transaction() as transaction:
            rows_affected = transaction.delete(
                self.assignment_table, 
                "id = %s", 
                (assignment_id,)
            )
            return rows_affected > 0

    def get_assignments_by_personality(self, personality_id: str) -> List[CategoryAssignment]:
        """
        Get all category assignments for a personality.

        Args:
            personality_id: ID of the personality

        Returns:
            List of CategoryAssignment objects
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT a.id, a.personality_id as personality, c.name as category
                FROM {self.assignment_table} a
                JOIN {self.category_table} c ON a.category_id = c.id
                WHERE a.personality_id = %s
            """
            results = transaction.query(query, (personality_id,))
            return [CategoryAssignment.from_dict(result) for result in results]

    def get_personalities_by_category(self, category_name: str) -> List[str]:
        """
        Get all personality IDs assigned to a category.

        Args:
            category_name: Name of the category

        Returns:
            List of personality IDs
        """
        with self.db_pool.get_transaction() as transaction:
            query = f"""
                SELECT a.personality_id
                FROM {self.assignment_table} a
                JOIN {self.category_table} c ON a.category_id = c.id
                WHERE c.name = %s
            """
            results = transaction.query(query, (category_name,))
            return [result["personality_id"] for result in results]
