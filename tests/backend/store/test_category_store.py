import pytest
from uuid import uuid4

from app.backend.models.category_assignment import CategoryAssignment
from app.backend.models.personality import Personality
from app.backend.store import Store


def test_category_create_and_get(store: Store):
    """Test creating and retrieving a category"""
    # Create a test category
    category_name = f"Test Category {uuid4()}"
    category_description = "A test category for unit testing"
    
    # Save to database
    category_id = store.category.create_category(category_name, category_description)
    
    # Verify ID was returned
    assert category_id is not None
    
    # Verify we can retrieve it by ID
    category = store.category.get_category(category_id)
    assert category is not None
    assert category["name"] == category_name
    assert category["description"] == category_description
    
    # Verify we can retrieve it by name
    category_by_name = store.category.get_category_by_name(category_name)
    assert category_by_name is not None
    assert category_by_name["id"] == category_id


def test_category_update(store: Store):
    """Test updating a category"""
    # Create a test category
    category_name = f"Update Category {uuid4()}"
    category_id = store.category.create_category(category_name)
    
    # Update the category
    new_name = f"Updated Category {uuid4()}"
    new_description = "Updated description"
    success = store.category.update_category(category_id, new_name, new_description)
    
    # Verify update was successful
    assert success is True
    
    # Verify changes were saved
    updated = store.category.get_category(category_id)
    assert updated["name"] == new_name
    assert updated["description"] == new_description


def test_category_delete(store: Store):
    """Test deleting a category"""
    # Create a test category
    category_name = f"Delete Category {uuid4()}"
    category_id = store.category.create_category(category_name)
    
    # Verify it exists
    assert store.category.get_category(category_id) is not None
    
    # Delete it
    success = store.category.delete_category(category_id)
    assert success is True
    
    # Verify it's gone
    assert store.category.get_category(category_id) is None


def test_category_list_all(store: Store):
    """Test listing all categories"""
    # Create unique test identifier
    test_id = str(uuid4())[:8]
    
    # Create multiple test categories
    category_names = [
        f"List Category {test_id} - 1",
        f"List Category {test_id} - 2",
        f"List Category {test_id} - 3"
    ]
    
    category_ids = [
        store.category.create_category(name) for name in category_names
    ]
    
    # Get all categories
    all_categories = store.category.list_all_categories()
    
    # Verify all our test categories are in the results
    found_names = set()
    for category in all_categories:
        if any(test_name in category["name"] for test_name in category_names):
            found_names.add(category["name"])
    
    assert len(found_names) == len(category_names)


def test_category_assignment_create_and_get(store: Store):
    """Test creating and retrieving a category assignment"""
    # First create a personality
    personality = Personality(name="Category Assignment Test")
    personality_id = store.personality.create(personality)
    
    # Create a unique category name
    category_name = f"Assignment Category {uuid4()}"
    
    # Create the assignment
    assignment = CategoryAssignment(
        personality=personality_id,
        category=category_name
    )
    
    # Save to database
    assignment_id = store.category.create_assignment(assignment)
    
    # Verify ID was returned
    assert assignment_id is not None
    
    # Verify we can retrieve it
    retrieved = store.category.get_assignment(assignment_id)
    assert retrieved is not None
    assert retrieved.personality == personality_id
    assert retrieved.category == category_name


def test_category_assignment_delete(store: Store):
    """Test deleting a category assignment"""
    # First create a personality
    personality = Personality(name="Assignment Delete Test")
    personality_id = store.personality.create(personality)
    
    # Create a unique category name
    category_name = f"Delete Assignment Category {uuid4()}"
    
    # Create the assignment
    assignment = CategoryAssignment(
        personality=personality_id,
        category=category_name
    )
    
    # Save to database
    assignment_id = store.category.create_assignment(assignment)
    
    # Verify it exists
    assert store.category.get_assignment(assignment_id) is not None
    
    # Delete it
    success = store.category.delete_assignment(assignment_id)
    assert success is True
    
    # Verify it's gone
    assert store.category.get_assignment(assignment_id) is None


def test_get_assignments_by_personality(store: Store):
    """Test getting all category assignments for a personality"""
    # Create a personality
    personality = Personality(name="Multiple Categories Test")
    personality_id = store.personality.create(personality)
    
    # Create unique category names
    test_id = str(uuid4())[:8]
    category_names = [
        f"Personality Category {test_id} - 1",
        f"Personality Category {test_id} - 2",
        f"Personality Category {test_id} - 3"
    ]
    
    # Create assignments
    for category_name in category_names:
        assignment = CategoryAssignment(
            personality=personality_id,
            category=category_name
        )
        store.category.create_assignment(assignment)
    
    # Get assignments for the personality
    assignments = store.category.get_assignments_by_personality(personality_id)
    
    # Verify we got all the assignments
    found_categories = set(a.category for a in assignments)
    assert len(found_categories.intersection(set(category_names))) == len(category_names)


def test_get_personalities_by_category(store: Store):
    """Test getting all personalities assigned to a category"""
    # Create a unique category name
    category_name = f"Shared Category {uuid4()}"
    
    # Create multiple personalities
    personalities = [
        Personality(name="Category Personality 1"),
        Personality(name="Category Personality 2"),
        Personality(name="Category Personality 3")
    ]
    
    personality_ids = [store.personality.create(p) for p in personalities]
    
    # Assign all personalities to the category
    for personality_id in personality_ids:
        assignment = CategoryAssignment(
            personality=personality_id,
            category=category_name
        )
        store.category.create_assignment(assignment)
    
    # Get personalities for the category
    found_personality_ids = store.category.get_personalities_by_category(category_name)
    
    # Verify we got all the personalities
    assert set(found_personality_ids) == set(personality_ids)
