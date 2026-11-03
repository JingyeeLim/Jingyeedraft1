import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenClient:
    def __init__(self):
        # 优先读取 Streamlit 云端 Secrets，若没有则读取环境变量
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key)

    def generate_ad_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard"):
        try:
            # 替换为公司账号拥有的最新图像生成模型
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size=size,
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            raise Exception(f"OpenAI Image API Error: {str(e)}")
