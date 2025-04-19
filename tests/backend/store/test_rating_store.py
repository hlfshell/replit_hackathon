import pytest
from uuid import uuid4

from app.backend.models.ad import Ad
from app.backend.models.personality import Personality
from app.backend.models.rating import Rating
from app.backend.store import Store


def test_rating_create(store: Store):
    """Test creating a rating record"""
    # First create a personality and an ad
    personality = Personality(name="Rating Test Person")
    personality_id = store.personality.create(personality)
    
    ad = Ad(image="https://example.com/rating-test.jpg", copy="Rating test ad")
    ad_id = store.ad.create(ad)
    
    # Create a test rating
    rating = Rating(
        personality=personality_id,
        ad=ad_id,
        thought="This ad makes me think about quality products",
        emotional_response="Positive",
        emotions="Happy, Satisfied",
        effectiveness="High"
    )
    
    # Save to database
    rating_id = store.rating.create(rating)
    
    # Verify ID was returned
    assert rating_id is not None
    
    # Verify we can retrieve it
    retrieved = store.rating.get(rating_id)
    assert retrieved is not None
    assert retrieved.personality == personality_id
    assert retrieved.ad == ad_id
    assert retrieved.thought == "This ad makes me think about quality products"
    assert retrieved.emotional_response == "Positive"
    assert retrieved.emotions == "Happy, Satisfied"
    assert retrieved.effectiveness == "High"


def test_rating_update(store: Store):
    """Test updating a rating record"""
    # First create a personality and an ad
    personality = Personality(name="Update Rating Test Person")
    personality_id = store.personality.create(personality)
    
    ad = Ad(image="https://example.com/update-rating-test.jpg", copy="Update rating test ad")
    ad_id = store.ad.create(ad)
    
    # Create a test rating
    rating = Rating(
        personality=personality_id,
        ad=ad_id,
        thought="Initial thought",
        emotional_response="Neutral",
        emotions="None",
        effectiveness="Low"
    )
    
    # Save to database
    rating_id = store.rating.create(rating)
    
    # Retrieve, modify, and update
    retrieved = store.rating.get(rating_id)
    retrieved.thought = "Updated thought"
    retrieved.emotional_response = "Positive"
    retrieved.emotions = "Happy"
    retrieved.effectiveness = "Medium"
    
    # Update in database
    success = store.rating.update(retrieved)
    assert success is True
    
    # Verify changes were saved
    updated = store.rating.get(rating_id)
    assert updated.thought == "Updated thought"
    assert updated.emotional_response == "Positive"
    assert updated.emotions == "Happy"
    assert updated.effectiveness == "Medium"


def test_rating_delete(store: Store):
    """Test deleting a rating record"""
    # First create a personality and an ad
    personality = Personality(name="Delete Rating Test Person")
    personality_id = store.personality.create(personality)
    
    ad = Ad(image="https://example.com/delete-rating-test.jpg", copy="Delete rating test ad")
    ad_id = store.ad.create(ad)
    
    # Create a test rating
    rating = Rating(
        personality=personality_id,
        ad=ad_id,
        thought="Delete test thought",
        emotional_response="Neutral",
        emotions="None",
        effectiveness="Low"
    )
    
    # Save to database
    rating_id = store.rating.create(rating)
    
    # Verify it exists
    assert store.rating.get(rating_id) is not None
    
    # Delete it
    success = store.rating.delete(rating_id)
    assert success is True
    
    # Verify it's gone
    assert store.rating.get(rating_id) is None


def test_rating_list_all(store: Store):
    """Test listing all ratings"""
    # First create a personality and an ad
    personality = Personality(name="List Ratings Test Person")
    personality_id = store.personality.create(personality)
    
    ad = Ad(image="https://example.com/list-ratings-test.jpg", copy="List ratings test ad")
    ad_id = store.ad.create(ad)
    
    # Create a unique identifier for this test
    test_id = str(uuid4())[:8]
    
    # Create multiple test ratings
    ratings = [
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} Rating thought 1",
            emotional_response="Positive",
            emotions="Happy",
            categories=["Test", "List1"]
        ),
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} Rating thought 2",
            emotional_response="Neutral",
            emotions="Calm",
            categories=["Test", "List2"]
        ),
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} Rating thought 3",
            emotional_response="Negative",
            emotions="Sad",
            categories=["Test", "List3"]
        )
    ]
    
    # Save all to database
    rating_ids = [store.rating.create(r) for r in ratings]
    
    # Get all ratings
    all_ratings = store.rating.list_all()
    
    # Verify all our test ratings are in the results
    test_thoughts = set([f"{test_id} Rating thought 1", f"{test_id} Rating thought 2", f"{test_id} Rating thought 3"])
    found_thoughts = set()
    
    for r in all_ratings:
        if r.thought in test_thoughts:
            found_thoughts.add(r.thought)
    
    assert found_thoughts == test_thoughts


def test_get_ratings_by_personality(store: Store):
    """Test getting ratings by personality"""
    # Create a personality
    personality = Personality(name="Personality Ratings Test")
    personality_id = store.personality.create(personality)
    
    # Create an ad
    ad = Ad(image="https://example.com/personality-ratings-test.jpg", copy="Personality ratings test ad")
    ad_id = store.ad.create(ad)
    
    # Create a unique identifier for this test
    test_id = str(uuid4())[:8]
    
    # Create multiple ratings for this personality
    ratings = [
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} Personality rating 1",
            emotional_response="Positive",
            emotions="Happy",
            categories=["Test"]
        ),
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} Personality rating 2",
            emotional_response="Neutral",
            emotions="Calm",
            categories=["Test"]
        )
    ]
    
    # Save all to database
    for r in ratings:
        store.rating.create(r)
    
    # Get ratings for the personality
    personality_ratings = store.rating.get_ratings_by_personality(personality_id)
    
    # Verify we got our test ratings
    test_thoughts = set([f"{test_id} Personality rating 1", f"{test_id} Personality rating 2"])
    found_thoughts = set()
    
    for r in personality_ratings:
        if r.thought in test_thoughts:
            found_thoughts.add(r.thought)
    
    assert found_thoughts == test_thoughts


def test_get_ratings_by_ad(store: Store):
    """Test getting ratings by ad"""
    # Create a unique identifier for this test
    test_id = str(uuid4())[:8]
    
    # Create multiple personalities
    personalities = [
        Personality(name=f"{test_id} Ad Rating Person 1"),
        Personality(name=f"{test_id} Ad Rating Person 2")
    ]
    personality_ids = [store.personality.create(p) for p in personalities]
    
    # Create an ad
    ad = Ad(image=f"https://example.com/{test_id}-ad-ratings.jpg", copy=f"{test_id} Ad ratings test")
    ad_id = store.ad.create(ad)
    
    # Create ratings from different personalities for this ad
    ratings = [
        Rating(
            personality=personality_ids[0],
            ad=ad_id,
            thought=f"{test_id} Ad rating 1",
            emotional_response="Positive",
            emotions="Happy",
            categories=["Test"]
        ),
        Rating(
            personality=personality_ids[1],
            ad=ad_id,
            thought=f"{test_id} Ad rating 2",
            emotional_response="Negative",
            emotions="Disappointed",
            categories=["Test"]
        )
    ]
    
    # Save all to database
    for r in ratings:
        store.rating.create(r)
    
    # Get ratings for the ad
    ad_ratings = store.rating.get_ratings_by_ad(ad_id)
    
    # Verify we got our test ratings
    test_thoughts = set([f"{test_id} Ad rating 1", f"{test_id} Ad rating 2"])
    found_thoughts = set()
    
    for r in ad_ratings:
        if r.thought in test_thoughts:
            found_thoughts.add(r.thought)
    
    assert found_thoughts == test_thoughts


def test_get_ratings_by_effectiveness(store: Store):
    """Test getting ratings by effectiveness"""
    # Create a unique identifier for this test
    test_id = str(uuid4())[:8]
    
    # Create a personality
    personality = Personality(name=f"{test_id} Effectiveness Ratings Test")
    personality_id = store.personality.create(personality)
    
    # Create an ad
    ad = Ad(image=f"https://example.com/{test_id}-effectiveness-ratings.jpg", copy=f"{test_id} Effectiveness ratings test")
    ad_id = store.ad.create(ad)
    
    # Create a unique effectiveness value for this test
    test_effectiveness = f"High{test_id}"
    
    # Create ratings with different effectiveness values
    ratings = [
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} High effectiveness",
            emotional_response="Positive",
            emotions="Happy",
            effectiveness=test_effectiveness
        ),
        Rating(
            personality=personality_id,
            ad=ad_id,
            thought=f"{test_id} Low effectiveness",
            emotional_response="Neutral",
            emotions="Calm",
            effectiveness="Low"
        )
    ]
    
    # Save all to database
    for r in ratings:
        store.rating.create(r)
    
    # Get ratings for the effectiveness value
    effectiveness_ratings = store.rating.get_ratings_by_effectiveness(test_effectiveness)
    
    # Verify we got only the rating with our test effectiveness value
    assert len(effectiveness_ratings) >= 1
    assert any(r.thought == f"{test_id} High effectiveness" for r in effectiveness_ratings)
    assert not any(r.thought == f"{test_id} Low effectiveness" for r in effectiveness_ratings)
