import os
import av
import json
import numpy as np
import pandas as pd

import torch
from transformers import AutoImageProcessor, AutoTokenizer, VisionEncoderDecoderModel
from openai import OpenAI

class VideoProcessor:
    def load(self):
        # Loading OpenAI
        OPENAI_ORG = os.environ.get("OPENAI_ORG")
        OPENAI_PROJECT = os.environ.get("OPENAI_PROJECT")
        self.openai = OpenAI(
            # organization=OPENAI_ORG,
            # project=OPENAI_PROJECT
        )
        
        
        # Loading pretrained processor, tokenizer, and model/
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.image_processor = AutoImageProcessor.from_pretrained("MCG-NJU/videomae-base")
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.model = VisionEncoderDecoderModel.from_pretrained("Neleac/timesformer-gpt2-video-captioning").to(device)
        
    
    def generate_caption_from_video(self, video_path):
        container = av.open(video_path)

        # extract evenly spaced frames from video
        seg_len = container.streams.video[0].frames
        clip_len = self.model.config.encoder.num_frames
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
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pixel_values = self.image_processor(frames, return_tensors="pt").pixel_values.to(device)
        tokens = self.model.generate(pixel_values, **gen_kwargs)
        caption = self.tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
        
        return caption

    def generate_tag_from_caption(self, caption):
        completion = self.openai.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": '''You are an expert tagging system for social media content. 
                Your task is to generate list of relevant tags for the following video captions in following JSON format.
                It should contain multiple tags for sentiment, multiple tags for targeted audience, and multiple tags for category if applicable. 
                Note that all values of the keys are list of strings.
                {
                    "other_tags" : [All the tags generated for the video caption], 
                    "sentiment_tags" : "[Positive, Negative, Neutral]", 
                    "targeted_audience_tags" : "[Children, Adults, Teenagers, General]",
                    "category_tags" : "[Entertainment, News, Technology, Business, Science, Lifestyle, Health, Sports, Travel, Politics, Art, Culture, History]"
                }
                '''},
                {"role": "user", "content": caption}
            ]
        )
        
        return json.loads(completion.choices[0].message.content)