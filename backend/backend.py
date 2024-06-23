import av
import numpy as np
import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel
from fastapi import FastAPI, File, UploadFile
import pandas as pd
import shutil
import os
    
app = FastAPI()

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



@app.post("/uploadvideo/")
async def create_upload_video(file: UploadFile = File(...)):
    video_path = f"videos/{file.filename}"
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Generate caption for the uploaded video
    caption = generate_caption_from_video(video_path)
    
    csv_path = "captions.csv"
    if not os.path.exists(csv_path):
        pd.DataFrame(columns=["video_name", "caption"]).to_csv(csv_path, index=False)
    
    new_row = pd.DataFrame([[file.filename, caption]], columns=["video_name", "caption"])
    pd.concat([pd.read_csv(csv_path), new_row]).to_csv(csv_path, index=False)
    
    return {"filename": file.filename, "caption": caption}
