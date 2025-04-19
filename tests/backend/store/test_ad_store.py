import pytest
from uuid import uuid4

from app.backend.models.ad import Ad
from app.backend.store import Store


def test_ad_create(store: Store):
    """Test creating an ad record"""
    # Create a test ad
    ad = Ad(
        image="https://example.com/image.jpg",
        copy="This is a test advertisement copy"
    )
    
    # Save to database
    ad_id = store.ad.create(ad)
    
    # Verify ID was returned
    assert ad_id is not None
    
    # Verify we can retrieve it
    retrieved = store.ad.get(ad_id)
    assert retrieved is not None
    assert retrieved.image == "https://example.com/image.jpg"
    assert retrieved.copy == "This is a test advertisement copy"


def test_ad_update(store: Store):
    """Test updating an ad record"""
    # Create a test ad
    ad = Ad(
        image="https://example.com/old-image.jpg",
        copy="Old advertisement copy"
    )
    
    # Save to database
    ad_id = store.ad.create(ad)
    
    # Retrieve, modify, and update
    retrieved = store.ad.get(ad_id)
    retrieved.image = "https://example.com/new-image.jpg"
    retrieved.copy = "Updated advertisement copy"
    
    # Update in database
    success = store.ad.update(retrieved)
    assert success is True
    
    # Verify changes were saved
    updated = store.ad.get(ad_id)
    assert updated.image == "https://example.com/new-image.jpg"
    assert updated.copy == "Updated advertisement copy"


def test_ad_delete(store: Store):
    """Test deleting an ad record"""
    # Create a test ad
    ad = Ad(
        image="https://example.com/delete-test.jpg",
        copy="Delete test advertisement"
    )
    
    # Save to database
    ad_id = store.ad.create(ad)
    
    # Verify it exists
    assert store.ad.get(ad_id) is not None
    
    # Delete it
    success = store.ad.delete(ad_id)
    assert success is True
    
    # Verify it's gone
    assert store.ad.get(ad_id) is None


def test_ad_list_all(store: Store):
    """Test listing all ads"""
    # Create multiple test ads
    ads = [
        Ad(image="https://example.com/image1.jpg", copy="Ad copy 1"),
        Ad(image="https://example.com/image2.jpg", copy="Ad copy 2"),
        Ad(image="https://example.com/image3.jpg", copy="Ad copy 3")
    ]
    
    # Save all to database
    ad_ids = [store.ad.create(ad) for ad in ads]
    
    # Get all ads
    all_ads = store.ad.list_all()
    
    # Verify all our test ads are in the results
    test_copies = set(["Ad copy 1", "Ad copy 2", "Ad copy 3"])
    found_copies = set()
    
    for ad in all_ads:
        if ad.copy in test_copies:
            found_copies.add(ad.copy)
    
    assert found_copies == test_copies


def test_ad_find_by_criteria(store: Store):
    """Test finding ads by criteria"""
    # Create unique identifier to ensure test isolation
    test_id = str(uuid4())[:8]
    
    # Create test ads with different attributes but identifiable
    ads = [
        Ad(
            image=f"https://example.com/{test_id}-image1.jpg", 
            copy=f"{test_id} Find criteria test 1"
        ),
        Ad(
            image=f"https://example.com/{test_id}-image2.jpg", 
            copy=f"{test_id} Find criteria test 2"
        ),
        Ad(
            image=f"https://example.com/{test_id}-image3.jpg", 
            copy=f"{test_id} Find criteria test 3"
        )
    ]
    
    # Save all to database
    for ad in ads:
        store.ad.create(ad)
    
    # Find by partial image URL
    results = store.ad.find_by_criteria({
        "image": f"https://example.com/{test_id}-image2.jpg"
    })
    
    assert len(results) >= 1
    assert any(ad.copy == f"{test_id} Find criteria test 2" for ad in results)
    
    # Find by copy
    results = store.ad.find_by_criteria({
        "copy": f"{test_id} Find criteria test 3"
    })
    
    assert len(results) >= 1
    assert any(ad.image == f"https://example.com/{test_id}-image3.jpg" for ad in results)
