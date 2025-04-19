import os
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional

from app.backend.models.ad import Ad
from app.backend.models.category_assignment import CategoryAssignment
from app.backend.models.personality import Personality
from app.backend.models.rating import Rating
from app.backend.store.db import Pool
from app.backend.store.ad_store import AdStore
from app.backend.store.category_store import CategoryStore
from app.backend.store.personality_store import PersonalityStore
from app.backend.store.rating_store import RatingStore
from app.backend.store.migration import Migration
from app.backend.agents.rate import RateAgent
from app.backend.llm import MultiModalLLM
from arkaine.flow import ParallelList
from app.backend.store import Store

# Configuration for image uploads
IMAGE_UPLOAD_DIR = Path("uploads/images")

# Create the upload directory if it doesn't exist
os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the uploads directory to serve images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Get database configuration from environment variables or use defaults
db_host = os.environ.get("POSTGRES_HOST", "localhost")
db_port = int(os.environ.get("POSTGRES_PORT", "5432"))
db_name = os.environ.get("POSTGRES_DB", "app")
db_user = os.environ.get("POSTGRES_USER", "postgres")
db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")

db_pool = Pool(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password,
)
Migration(db_pool).run_migrations()
store = Store(db_pool)
ad_store = AdStore(db_pool)
category_store = CategoryStore(db_pool)
personality_store = PersonalityStore(db_pool)
rating_store = RatingStore(db_pool)

llm = MultiModalLLM(model="gemini-2.5-flash-preview-04-17")
RateAgent(llm=llm, store=store)
RatingSwarm = ParallelList(RateAgent)

# --- Ad Endpoints ---
@app.post("/ads", response_model=str)
async def create_ad(image: Optional[UploadFile] = File(None), copy: Optional[str] = Form(None)):
    """
    Create a new ad with multipart form data.
    Example input (multipart form):
    - image: file upload
    - copy: "Buy now!"
    Example output (ad_id):
    "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc"
    """
    # Validate that at least one of image or copy is provided
    if not image and not copy:
        raise HTTPException(status_code=400, detail="At least one of image or copy must be provided")
    
    # Process image if provided
    image_path = None
    if image:
        # Generate a unique filename with UUID
        file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = IMAGE_UPLOAD_DIR / unique_filename
        
        # Save the uploaded file
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Store the relative path to be served via the /uploads endpoint
        image_path = f"/uploads/images/{unique_filename}"
    
    # Create the ad object
    ad_data = {"image": image_path, "copy": copy}
    ad_obj = Ad.from_dict(ad_data)
    
    # Store in database
    ad_id = ad_store.create(ad_obj)
    if not ad_id:
        raise HTTPException(status_code=400, detail="Ad creation failed")
    
    return ad_id

@app.post("/rate", response_model=Dict[str, Any])
async def rate_ad(image: UploadFile = File(...), personality_ids: str = Form(...)):
    """
    Rate an ad for multiple personalities.
    
    Example input (multipart form):
    - image: file upload
    - personality_ids: comma-separated list of personality IDs
    
    Example output:
    {
        "ad_id": "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc",
        "ratings": [
            {
                "id": "c9e8d7f6-5a4b-3c2d-1e0f-123456789abc",
                "personality": "personality_id_1",
                "ad": "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc",
                "thought": "This ad would appeal to...",
                "emotional_response": "The person would feel...",
                "emotions": ["Happy", "Excited"],
                "effectiveness": "Good Fit"
            },
            ...
        ]
    }
    """
    # Validate personality_ids
    try:
        personality_id_list = [pid.strip() for pid in personality_ids.split(',')]
        if not personality_id_list:
            raise ValueError("No personality IDs provided")
        
        # Verify all personalities exist
        for pid in personality_id_list:
            personality = personality_store.get(pid)
            if not personality:
                raise HTTPException(status_code=404, detail=f"Personality with ID {pid} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid personality_ids format: {str(e)}")
    
    # Process and save the image
    if not image:
        raise HTTPException(status_code=400, detail="Image is required")
    
    # Generate a unique filename with UUID
    file_extension = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = IMAGE_UPLOAD_DIR / unique_filename
    
    # Save the uploaded file
    contents = await image.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Store the relative path to be served via the /uploads endpoint
    image_path = f"/uploads/images/{unique_filename}"
    
    # Create the ad object with just the image (no copy)
    ad_data = {"image": image_path, "copy": None}
    ad_obj = Ad.from_dict(ad_data)
    
    # Store in database
    ad_id = ad_store.create(ad_obj)
    if not ad_id:
        raise HTTPException(status_code=400, detail="Ad creation failed")
    
    # Use RatingSwarm to generate ratings for all personalities
    try:
        # Create a list of arguments for each personality
        swarm_args = [{
            "personality": pid,
            "ad": ad_id
        } for pid in personality_id_list]
        
        # Run the rating swarm in parallel
        ratings = RatingSwarm(swarm_args)
        
        # Save the ratings to the database
        rating_ids = []
        for rating in ratings:
            rating_id = rating_store.create(rating)
            if rating_id:
                rating_ids.append(rating_id)
        
        # Retrieve the full rating objects to return
        rating_objects = []
        for rating_id in rating_ids:
            rating = rating_store.get(rating_id)
            if rating:
                rating_objects.append(rating.to_dict())
        
        return {
            "ad_id": ad_id,
            "ratings": rating_objects
        }
    except Exception as e:
        # If rating fails, still return the ad_id but with an error message
        return {
            "ad_id": ad_id,
            "error": f"Rating generation failed: {str(e)}",
            "ratings": []
        }

@app.get("/ads/{ad_id}")
def get_ad(ad_id: str):
    """
    Get an ad by ID.
    Example output:
    {
        "id": "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc",
        "image": "https://example.com/image.png",
        "copy": "Buy now!"
    }
    """
    ad = ad_store.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad.to_dict()

@app.put("/ads/{ad_id}")
def update_ad(ad_id: str, ad: Dict[str, Any]):
    """
    Update an ad by ID.
    Example input (JSON):
    {
        "image": "https://example.com/image2.png",
        "copy": "Updated copy"
    }
    Example output:
    {"success": true}
    """
    ad["id"] = ad_id
    ad_obj = Ad.from_dict(ad)
    success = ad_store.update(ad_obj)
    if not success:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True}

@app.delete("/ads/{ad_id}")
def delete_ad(ad_id: str):
    """
    Delete an ad by ID.
    Example output:
    {
        "success": true
    }
    """
    success = ad_store.delete(ad_id)
    if not success:
        raise HTTPException(status_code=404, detail="Delete failed")
    return {"success": True}

@app.get("/ads", response_model=List[Dict[str, Any]])
def list_ads():
    """
    List all ads.
    Example output:
    [
        {
            "id": "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc",
            "image": "https://example.com/image.png",
            "copy": "Buy now!"
        }
    ]
    """
    return [ad.to_dict() for ad in ad_store.list_all()]

# --- Personality Endpoints ---
@app.post("/personalities", response_model=str)
def create_personality(personality: Dict[str, Any]):
    """
    Create a new personality.
    Example input (JSON):
    {
        "name": "Alice",
        "age": 30,
        "gender": "female",
        "location": "NYC",
        "personality_traits": ["friendly", "curious"]
    }
    Example output (personality_id):
    "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456"
    """
    obj = Personality.from_dict(personality)
    pid = personality_store.create(obj)
    if not pid:
        raise HTTPException(status_code=400, detail="Creation failed")
    return pid

@app.get("/personalities/{personality_id}", response_model=Dict[str, Any])
def get_personality(personality_id: str):
    """
    Get a personality by ID.
    Example output:
    {
        "id": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
        "name": "Alice",
        "age": 30,
        ...
    }
    """
    obj = personality_store.get(personality_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj.to_dict()

@app.put("/personalities/{personality_id}")
def update_personality(personality_id: str, personality: Dict[str, Any]):
    """
    Update a personality by ID.
    Example input (JSON):
    {
        "name": "Alice Updated",
        ...
    }
    Example output:
    {"success": true}
    """
    personality["id"] = personality_id
    obj = Personality.from_dict(personality)
    success = personality_store.update(obj)
    if not success:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True}

@app.delete("/personalities/{personality_id}")
def delete_personality(personality_id: str):
    """
    Delete a personality by ID.
    Example output:
    {"success": true}
    """
    success = personality_store.delete(personality_id)
    if not success:
        raise HTTPException(status_code=404, detail="Delete failed")
    return {"success": True}

@app.get("/personalities", response_model=List[Dict[str, Any]])
def list_personalities():
    """
    List all personalities.
    Example output:
    [
        {
            "id": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
            "name": "Alice",
            "age": 30,
            ...
        },
        ...
    ]
    """
    return [obj.to_dict() for obj in personality_store.list_all()]
    return cid

@app.post("/categories", response_model=str)
def create_category(category: Dict[str, Any]):
    """
    Create a new category.
    Example input (JSON):
    {
        "name": "Tech",
        "description": "Technology related ads"
    }
    Example output (category_id):
    "c8e7c2e4-2b8f-4f9c-8a7e-abcdef654321"
    """
    cat = category_store.get_category(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    return cat

@app.get("/categories/{category_id}", response_model=Dict[str, Any])
def get_category(category_id: str):
    """
    Get a category by ID.
    Example output:
    {
        "id": "c8e7c2e4-2b8f-4f9c-8a7e-abcdef654321",
        "name": "Tech",
        "description": "Technology related ads"
    }
    """
    name = category["name"]
    description = category.get("description")
    success = category_store.update_category(category_id, name, description)
    if not success:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True}

@app.put("/categories/{category_id}")
def update_category(category_id: str, category: Dict[str, Any]):
    """
    Update a category by ID.
    Example input (JSON):
    {
        "name": "Tech Updated",
        "description": "Updated description"
    }
    Example output:
    {"success": true}
    """
    success = category_store.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Delete failed")
    return {"success": True}

@app.delete("/categories/{category_id}")
def delete_category(category_id: str):
    """
    Delete a category by ID.
    Example output:
    {"success": true}
    """
    return category_store.list_all_categories()

# --- Category Assignment Endpoints ---
@app.get("/categories", response_model=List[Dict[str, Any]])
def list_categories():
    """
    List all categories.
    Example output:
    [
        {
            "id": "c8e7c2e4-2b8f-4f9c-8a7e-abcdef654321",
            "name": "Tech",
            "description": "Technology related ads"
        },
        ...
    ]
    """
    obj = CategoryAssignment.from_dict(assignment)
    aid = category_store.create_assignment(obj)
    if not aid:
        raise HTTPException(status_code=400, detail="Creation failed")
    return aid

@app.post("/assignments", response_model=str)
def create_assignment(assignment: Dict[str, Any]):
    """
    Create a new category assignment.
    Example input (JSON):
    {
        "personality": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
        "category": "c8e7c2e4-2b8f-4f9c-8a7e-abcdef654321"
    }
    Example output (assignment_id):
    "a1b2c3d4-5678-90ab-cdef-1234567890ab"
    """
    obj = category_store.get_assignment(assignment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj.to_dict()

@app.get("/assignments/{assignment_id}", response_model=Dict[str, Any])
def get_assignment(assignment_id: str):
    """
    Get a category assignment by ID.
    Example output:
    {
        "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
        "personality": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
        "category": "c8e7c2e4-2b8f-4f9c-8a7e-abcdef654321"
    }
    """
    success = category_store.delete_assignment(assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Delete failed")
    return {"success": True}

@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: str):
    """
    Delete a category assignment by ID.
    Example output:
    {"success": true}
    """
    return [a.to_dict() for a in category_store.get_assignments_by_personality(personality_id)]

@app.get("/assignments/by_personality/{personality_id}", response_model=List[Dict[str, Any]])
def get_assignments_by_personality(personality_id: str):
    """
    Get all category assignments for a personality.
    Example output:
    [
        {
            "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
            "personality": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
            "category": "c8e7c2e4-2b8f-4f9c-8a7e-abcdef654321"
        },
        ...
    ]
    """
    return category_store.get_personalities_by_category(category_name)

# --- Rating Endpoints ---
@app.get("/assignments/by_category/{category_name}", response_model=List[str])
def get_personalities_by_category(category_name: str):
    """
    Get all personality IDs assigned to a category.
    Example output:
    [
        "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
        ...
    ]
    """
    obj = Rating.from_dict(rating)
    rid = rating_store.create(obj)
    if not rid:
        raise HTTPException(status_code=400, detail="Creation failed")
    return rid

@app.post("/ratings", response_model=str)
def create_rating(rating: Dict[str, Any]):
    """
    Create a new rating.
    Example input (JSON):
    {
        "personality": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
        "ad": "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc",
        "thought": "Interesting ad",
        "emotional_response": "Happy",
        "emotions": "joy",
        "categories": ["Tech"]
    }
    Example output (rating_id):
    "r1b2c3d4-5678-90ab-cdef-1234567890ab"
    """
    obj = rating_store.get(rating_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj.to_dict()

@app.get("/ratings/{rating_id}", response_model=Dict[str, Any])
def get_rating(rating_id: str):
    """
    Get a rating by ID.
    Example output:
    {
        "id": "r1b2c3d4-5678-90ab-cdef-1234567890ab",
        "personality": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
        "ad": "b8f7c2e4-2b8f-4f9c-8a7e-123456789abc",
        "thought": "Interesting ad",
        "emotional_response": "Happy",
        "emotions": "joy",
        "categories": ["Tech"]
    }
    """
    rating["id"] = rating_id
    obj = Rating.from_dict(rating)
    success = rating_store.update(obj)
    if not success:
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True}

@app.put("/ratings/{rating_id}")
def update_rating(rating_id: str, rating: Dict[str, Any]):
    """
    Update a rating by ID.
    Example input (JSON):
    {
        "thought": "Changed my mind",
        ...
    }
    Example output:
    {"success": true}
    """
    success = rating_store.delete(rating_id)
    if not success:
        raise HTTPException(status_code=404, detail="Delete failed")
    return {"success": True}

@app.delete("/ratings/{rating_id}")
def delete_rating(rating_id: str):
    """
    Delete a rating by ID.
    Example output:
    {"success": true}
    """
    return [obj.to_dict() for obj in rating_store.list_all()]

@app.get("/ratings", response_model=List[Dict[str, Any]])
def list_ratings():
    """
    List all ratings.
    Example output:
    [
        {
            "id": "r1b2c3d4-5678-90ab-cdef-1234567890ab",
            "personality": "d8e7c2e4-2b8f-4f9c-8a7e-abcdef123456",
            ...
        },
        ...
    ]
    """
    return [r.to_dict() for r in rating_store.get_ratings_by_personality(personality_id)]

@app.get("/ratings/by_personality/{personality_id}", response_model=List[Dict[str, Any]])
def get_ratings_by_personality(personality_id: str):
    """
    Get all ratings for a personality.
    Example output:
    [
        {
            "id": "r1b2c3d4-5678-90ab-cdef-1234567890ab",
            ...
        },
        ...
    ]
    """
    return [r.to_dict() for r in rating_store.get_ratings_by_ad(ad_id)]

@app.get("/ratings/by_ad/{ad_id}", response_model=List[Dict[str, Any]])
def get_ratings_by_ad(ad_id: str):
    """
    Get all ratings for an ad.
    Example output:
    [
        {
            "id": "r1b2c3d4-5678-90ab-cdef-1234567890ab",
            "personality": "p1b2c3d4-5678-90ab-cdef-1234567890ab",
            "ad": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
            "thought": "This ad makes me think about...",
            "emotional_response": "I feel happy when I see this ad",
            "emotions": ["happy", "excited", "interested"]
        }
    ]
    """
    # Assuming this endpoint should return ratings by ad, not by category.
    # If you want ratings by category, ensure 'category' is a parameter.
    # For now, commenting this out as it causes the unterminated string error and is likely a copy-paste mistake.
    # return [r.to_dict() for r in rating_store.get_ratings_by_category(category)]
    pass


@app.get("/")
def root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.backend.server:app", host="0.0.0.0", port=8000, reload=True)
