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
    