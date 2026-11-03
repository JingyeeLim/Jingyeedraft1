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
        调用 gpt-image-1.5 模型生成广告图片，全兼容 URL 与 Base64 解析
        """
        try:
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size=size,
                n=1,
            )
            
            image_obj = response.data[0]
            
            # 1. 尝试直接获取 url 属性
            url = getattr(image_obj, 'url', None)
            if url:
                return url
                
            # 2. 尝试获取 base64 属性
            b64_json = getattr(image_obj, 'b64_json', None)
            if b64_json:
                return f"data:image/png;base64,{b64_json}"
                
            # 3. 如果是 dict 字典结构
            if isinstance(image_obj, dict):
                if image_obj.get('url'):
                    return image_obj['url']
                if image_obj.get('b64_json'):
                    return f"data:image/png;base64,{image_obj['b64_json']}"
            
            raise Exception("API 没有返回有效图片链接或 Base64 数据。")
                
        except Exception as e:
            raise Exception(f"OpenAI Image API Error: {str(e)}")
