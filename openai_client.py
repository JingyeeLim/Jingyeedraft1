import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenClient:
    def __init__(self):
        # 优先读取 Streamlit 云端 Secrets，若没有则读取本地环境变量 os.getenv
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in Secrets or Environment Variables.")
        self.client = OpenAI(api_key=api_key)

    def generate_ad_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid"):
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"OpenAI Image API Error: {str(e)}")
