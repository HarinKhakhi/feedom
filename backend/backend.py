import os
import shutil

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

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
processor.load()

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
    
    video_path = os.path.join(os.environ.get('VIDEO_DB'), video['video_id'])
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return Response(content=open(video_path, "rb").read(), media_type="video/avi")    


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
    tag_counts = [f"{result['_id']}: {result['count']}" for result in results]
    
    return tag_counts


@app.get("/feed")
async def get_feed(limit: int = 10):
    feed_cursor = await collection.find({}, {"video_id": 1}).limit(limit).to_list(length=None)
    
    # Convert the cursor to a list of video_ids
    feed_list = [
        doc['video_id'] 
    for doc in feed_cursor ]
    
    return feed_list