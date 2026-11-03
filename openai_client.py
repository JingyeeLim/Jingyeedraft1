import os
import io
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

    def generate_ad_image(self, prompt: str, size: str = "1024x1024"):
        try:
            response = self.client.images.generate(
                model="gpt-image-1.5",
                prompt=prompt,
                size=size,
                n=1,
            )
            img_item = response.data[0]
            url = getattr(img_item, 'url', None)
            if url:
                return url
            b64 = getattr(img_item, 'b64_json', None)
            if b64:
                return f"data:image/png;base64,{b64}"
            raise Exception("No valid image data returned.")
        except Exception as e:
            raise Exception(f"OpenAI Image API Error: {str(e)}")

    def edit_ad_image(self, pil_image, prompt: str, size: str = "1024x1024"):
        try:
            pil_image = pil_image.convert("RGBA")
            byte_stream = io.BytesIO()
            pil_image.save(byte_stream, format="PNG")
            byte_stream.seek(0)
            
            file_tuple = ("image.png", byte_stream, "image/png")
            response = self.client.images.edit(
                model="gpt-image-1.5",
                image=file_tuple,
                prompt=prompt,
                size=size,
                n=1,
            )
            img_item = response.data[0]
            url = getattr(img_item, 'url', None)
            if url:
                return url
            b64 = getattr(img_item, 'b64_json', None)
            if b64:
                return f"data:image/png;base64,{b64}"
            raise Exception("No valid image data returned from Edit API.")
        except Exception as e:
            raise Exception(f"OpenAI Image Edit Error: {str(e)}")
