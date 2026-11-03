import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageGenClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")
        self.client = OpenAI(api_key=api_key)

    def generate_ad_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard", style: str = "vivid"):
        """
        调用 DALL·E 3 生成广告图片 (严格禁止任何 Chat completions 接口调用，防止浪费 Token)
        """
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
