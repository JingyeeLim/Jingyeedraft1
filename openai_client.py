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
        """
        调用 gpt-image-1.5 模型生成广告图片，兼容 URL 和 Base64 两种返回格式
        """
        try:
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size=size,
                n=1,
            )
            
            image_data = response.data[0]
            
            # 兼容处理：优先使用 url，若 url 为空则自动兼容 b64_json
            if hasattr(image_data, 'url') and image_data.url:
                return image_data.url
            elif hasattr(image_data, 'b64_json') and image_data.b64_json:
                return f"data:image/png;base64,{image_data.b64_json}"
            else:
                raise Exception("API returned no valid image URL or base64 data.")
                
        except Exception as e:
            raise Exception(f"OpenAI Image API Error: {str(e)}")
