import os
import shutil

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from .utils import VideoProcessor

# Setup
load_dotenv()
os.makedirs("videos", exist_ok=True)

# Loading MongoDB
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["video_db"]
collection = db["metadata"]

# Loding Video Processor
processor = VideoProcessor()
processor.load()

# Fast API
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
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
    
    # Inert into MongoDB
    document = collection.insert_one({
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
    

@app.get("/tags")
async def get_tags(limit: int = 10):
    # Aggregation pipeline to unwind tags array and count occurrences
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    # Execute the aggregation pipeline
    results = collection.aggregate(pipeline)
    
    # Convert the results to a dictionary
    tag_counts = [f"{result['_id']}: {result['count']}" for result in results]
    
    return tag_counts


@app.get("/feed")
async def get_feed(limit: int = 10):
    feed_cursor = collection.find({}, {"video_id": 1}).limit(limit)
    
    # Convert the cursor to a list of video_ids
    feed_list = [{
        'filename': doc['video_id'],
        'title': 'Placeholder' 
    } for doc in feed_cursor]
    
    return feed_list