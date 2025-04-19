import pytest
from uuid import uuid4

from app.backend.models.personality import Personality
from app.backend.store import Store


def test_personality_create(store: Store):
    """Test creating a personality record"""
    # Create a test personality
    personality = Personality(
        name="Test Person",
        age=30,
        gender="Female",
        location="New York",
        occupation="Software Engineer",
        income=120000.0,
        personality_traits=["Analytical", "Creative"],
        interests=["Coding", "Reading"]
    )
    
    # Save to database
    personality_id = store.personality.create(personality)
    
    # Verify ID was returned
    assert personality_id is not None
    
    # Verify we can retrieve it
    retrieved = store.personality.get(personality_id)
    assert retrieved is not None
    assert retrieved.name == "Test Person"
    assert retrieved.age == 30
    assert retrieved.gender == "Female"
    assert retrieved.personality_traits == ["Analytical", "Creative"]
    assert retrieved.interests == ["Coding", "Reading"]


def test_personality_update(store: Store):
    """Test updating a personality record"""
    # Create a test personality
    personality = Personality(
        name="Update Test",
        age=25,
        gender="Male"
    )
    
    # Save to database
    personality_id = store.personality.create(personality)
    
    # Retrieve, modify, and update
    retrieved = store.personality.get(personality_id)
    retrieved.age = 26
    retrieved.location = "San Francisco"
    
    # Update in database
    success = store.personality.update(retrieved)
    assert success is True
    
    # Verify changes were saved
    updated = store.personality.get(personality_id)
    assert updated.age == 26
    assert updated.location == "San Francisco"
    assert updated.name == "Update Test"  # Unchanged field


def test_personality_delete(store: Store):
    """Test deleting a personality record"""
    # Create a test personality
    personality = Personality(
        name="Delete Test",
        age=40
    )
    
    # Save to database
    personality_id = store.personality.create(personality)
    
    # Verify it exists
    assert store.personality.get(personality_id) is not None
    
    # Delete it
    success = store.personality.delete(personality_id)
    assert success is True
    
    # Verify it's gone
    assert store.personality.get(personality_id) is None


def test_personality_list_all(store: Store):
    """Test listing all personalities"""
    # Create multiple test personalities
    personalities = [
        Personality(name="List Test 1", age=20),
        Personality(name="List Test 2", age=30),
        Personality(name="List Test 3", age=40)
    ]
    
    # Save all to database
    personality_ids = [store.personality.create(p) for p in personalities]
    
    # Get all personalities
    all_personalities = store.personality.list_all()
    
    # Verify all our test personalities are in the results
    test_names = set(["List Test 1", "List Test 2", "List Test 3"])
    found_names = set()
    
    for p in all_personalities:
        if p.name in test_names:
            found_names.add(p.name)
    
    assert found_names == test_names


def test_personality_find_by_criteria(store: Store):
    """Test finding personalities by criteria"""
    # Create test personalities with different attributes
    personalities = [
        Personality(
            name="Criteria Test 1", 
            age=25, 
            gender="Female",
            location="New York",
            occupation="Engineer"
        ),
        Personality(
            name="Criteria Test 2", 
            age=30, 
            gender="Male",
            location="New York",
            occupation="Designer"
        ),
        Personality(
            name="Criteria Test 3", 
            age=35, 
            gender="Female",
            location="San Francisco",
            occupation="Engineer"
        )
    ]
    
    # Save all to database
    for p in personalities:
        store.personality.create(p)
    
    # Test finding by single criterion
    results = store.personality.find_by_criteria({"gender": "Female"})
    assert len(results) >= 2  # At least our 2 female test personalities
    assert all(p.gender == "Female" for p in results)
    
    # Test finding by multiple criteria
    results = store.personality.find_by_criteria({
        "location": "New York",
        "occupation": "Engineer"
    })
    assert len(results) >= 1
    assert all(p.location == "New York" and p.occupation == "Engineer" for p in results)
    
    # Test finding by age
    results = store.personality.find_by_criteria({"age": 30})
    assert len(results) >= 1
    assert all(p.age == 30 for p in results)
