import os
import shutil
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Response, HTTPException
from fastapi import Query, File
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from .utils import VideoProcessor

load_dotenv()
os.makedirs("videos", exist_ok=True)

# Loading MongoDB
MONGO_URI = os.environ.get("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["video_db"]
collection = db["metadata"]

# Loding Video Processor
processor = VideoProcessor()
# processor.load()

# Fast API
app = FastAPI()

# Configure CORS
origins = [
    "*",
]

# Adding Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/db/add")
async def create_upload_video(file: UploadFile = File(...)):
    
    # Saving the video
    video_path = f"videos/{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate caption for the uploaded video
    caption = processor.generate_caption_from_video(video_path)
    
    # Generate tags for the caption
    tag = processor.generate_tag_from_caption(caption)
    all_tags = []
    for key in tag:
        all_tags.extend(tag[key])
    
    document = await collection.insert_one({
        "video_id": file.filename,
        "caption": caption,
        "tags": all_tags,
        "organized_tags": tag
    })
    
    return {
        "video_id": file.filename,
        "caption": caption,
        "tags": all_tags
    }
    
    
@app.get("/db/video")
async def get_video(video_id: str):
    video = await collection.find_one({"video_id": video_id})
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video


@app.get("/tags")
async def get_tags(limit: int = 10):
    # Aggregation pipeline to unwind tags array and count occurrences
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    results = await collection.aggregate(pipeline).to_list(length=None)

    # Convert the results to a dictionary
    tag_counts = [f"{result['_id']}" for result in results]
    
    return tag_counts


def parse_tag_weights(tag_weights_str: str) -> Dict[str, float]:
    tag_weights = {}
    for item in tag_weights_str.split(','):
        tag, weight = item.split('=')
        tag_weights[tag] = float(weight)
    return tag_weights


def get_user_profile(user_id: str):
    # Dummy function to fetch user data
    return {"user_id": user_id, "favorite_tags": {"music": 10, "travel": 5}}

@app.get("/feed")
async def get_feed(tag_weights: str = Query(default=''), limit: int = 10):
    
    if tag_weights:
        tag_weights_dict = parse_tag_weights(tag_weights)
    else:
        # Fetch user profile and use favorite tags as weights
        user_profile = get_user_profile(10)
        tag_weights_dict = user_profile['favorite_tags']
        if not tag_weights_dict:
            raise HTTPException(status_code=404, detail="No tag preferences found for the user")

    # Create a projection for the aggregation pipeline to calculate the relevance score
    projection = {
        "video_id": 1,
        "tags": 1,
        "caption": 1,
        "relevance_score": {
            "$sum": [
                {"$cond": [{"$in": [tag, "$tags"]}, weight, 0]}
                for tag, weight in tag_weights_dict.items()
            ]
        }
    }
    
    # Aggregation pipeline to calculate relevance scores and sort by relevance
    pipeline = [
        {"$project": projection},
        {"$sort": {"relevance_score": -1}},
        {"$limit": limit}
    ]
    
    feed_cursor = await collection.aggregate(pipeline).to_list(length=None)
    
    # Convert the cursor to a list of video_ids
    feed_list = [
        {
            'video_id': doc['video_id'],
            'caption': doc['caption'],
            'tags': doc['tags'],
        } 
        for doc in feed_cursor
    ]
    
    return feed_list
