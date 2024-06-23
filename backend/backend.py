import av
import numpy as np
import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel
from fastapi import FastAPI, File, UploadFile
import pandas as pd
import shutil
import os
from openai import OpenAI
import json
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

import os


app = FastAPI()

client = OpenAI(
  organization='org-FwPkHfz2zBsZt1qHLGhe0dZn',
  project='Ucb-Ai-Hackathon-June2024 200',
)

MONGO_URI = os.environ.get("MONGO_URI")
uri = MONGO_URI

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["video_db"]
collection = db["metadata"]

    
device = "cuda" if torch.cuda.is_available() else "cpu"

# load pretrained processor, tokenizer, and model
image_processor = AutoImageProcessor.from_pretrained("MCG-NJU/videomae-base")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = VisionEncoderDecoderModel.from_pretrained("Neleac/timesformer-gpt2-video-captioning").to(device)


os.makedirs("videos", exist_ok=True)

def generate_caption_from_video(video_path):
    container = av.open(video_path)

    # extract evenly spaced frames from video
    seg_len = container.streams.video[0].frames
    clip_len = model.config.encoder.num_frames
    indices = set(np.linspace(0, seg_len, num=clip_len, endpoint=False).astype(np.int64))
    frames = []
    container.seek(0)
    for i, frame in enumerate(container.decode(video=0)):
        if i in indices:
            frames.append(frame.to_ndarray(format="rgb24"))

    # generate caption
    gen_kwargs = {
        "min_length": 10, 
        "max_length": 20, 
        "num_beams": 8,
    }
    pixel_values = image_processor(frames, return_tensors="pt").pixel_values.to(device)
    tokens = model.generate(pixel_values, **gen_kwargs)
    caption = tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
    #print(caption)
    return caption

def generate_tag_from_caption(caption):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


    completion = client.chat.completions.create(
    model="gpt-4o",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": '''You are an expert tagging system for social media content. 
        Your task is to generate list of relevant tags for the following video captions in following JSON format.
        It should contain multiple tags for sentiment, multiple tags for targeted audience, and multiple tags for category if applicable. 
        
        {
            "other_tags" : [All the tags generated for the video caption], 
            "sentiment_tag" : "[Positive, Negative, Neutral, multiple of these]", 
            "targeted_audience_tag" : "[Children, Adults, Teenagers, General, multiple of these]",
            "category_tag" : "[Entertainment, News, Technology, Business, Science, Lifestyle, Health, Sports, Travel, Politics, Art, Culture, History, Other, multiple of these]"
        }
        '''},
        {"role": "user", "content": caption}
    ]
    )
    
    return json.loads(completion.choices[0].message.content)

@app.post("/uploadvideo/")
async def create_upload_video(file: UploadFile = File(...)):
    video_path = f"videos/{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate caption for the uploaded video
    caption = generate_caption_from_video(video_path)
    
    tag = generate_tag_from_caption(caption)
    
    collection.insert_one({
        "video_id": file.filename,
        "caption": caption,
        "tag": tag
    })
    print("Inserted into database!")
    
    return {"filename": file.filename, "caption": caption, "tag": tag}
    
