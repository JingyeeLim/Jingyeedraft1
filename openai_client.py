import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenClient:
    def __init__(self):
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key)

    def generate_ad_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard"):
        """
        调用 gpt-image-1.5 模型生成广告图片
        """
        try:
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size=size,
                n=1,
            )
            
            # 拿到第一张图片对象
            image_data = response.data[0]
            
            # 安全提取 URL
            url = None
            if hasattr(image_data, 'url') and image_data.url:
                url = image_data.url
            elif isinstance(image_data, dict) and image_data.get('url'):
                url = image_data['url']
                
            if url:
                return url

            # 安全提取 Base64
            b64_json = None
            if hasattr(image_data, 'b64_json') and image_data.b64_json:
                b64_json = image_data.b64_json
            elif isinstance(image_data, dict) and image_data.get('b64_json'):
                b64_json = image_data['b64_json']

            if b64_json:
                return f"data:image/png;base64,{b64_json}"

            # 如果都没有获取到，抛出完整数据结构以便排查
            raise Exception(f"API 返回数据无法解析，数据类型为: {type(image_data)}")
                
        except Exception as e:
            raise Exception(f"OpenAI Image API Error: {str(e)}")
