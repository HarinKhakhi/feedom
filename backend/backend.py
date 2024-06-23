import os
import shutil

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
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
async def get_tags(therehold: int = 10):
    # Aggregation pipeline to unwind tags array and count occurrences
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": therehold}
    ]
    
    # Execute the aggregation pipeline
    results = collection.aggregate(pipeline)
    
    # Convert the results to a dictionary
    tag_counts = {result['_id']: result['count'] for result in results}
    
    return tag_counts