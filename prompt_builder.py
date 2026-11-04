import os
import streamlit as st
from openai import OpenAI

def build_marketing_prompt(user_input: str, ad_style: str) -> str:
    """
    使用 GPT-4o 充当 AI 视觉总监，把用户的简单想法扩写为极致的商业摄影 Prompt
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        # 如果没有 key 则退回到基础规则
        return f"{ad_style}: {user_input}, commercial studio quality, high resolution, 8k."

    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    You are an expert commercial advertising photographer and AI prompt architect for DrClearAligners (a clear aligner dental brand).
    Your job is to transform brief marketing requests into highly detailed, high-resolution image prompts for an AI image generator.
    
    Requirements for output prompt:
    1. Focus on photorealism, precise lighting, optical refractions, texture of clear aligners, and aesthetic environment.
    2. Incorporate specific camera terms (e.g., 85mm f/1.8 lens, macro shot, soft studio rim lighting).
    3. Ensure clean, luxury, medical-grade or natural lifestyle look.
    4. Return ONLY the enhanced final English prompt text. No introductory or extra chatter.
    """
    
    user_prompt = f"""
    Ad Style Selected: {ad_style}
    User Request: {user_input}
    
    Please refine and expand this into a single professional image generation prompt.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # 兜底机制：若 GPT-4o 调用失败，退回普通模板
        return f"{ad_style}: {user_input}, ultra-clean commercial photography, 8k resolution, elegant light refractions."
