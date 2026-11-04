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
        You are a high-end commercial ad visual director for DrClearAligners.
        When expanding prompts for human models or product shots, strictly enforce these advertising standards:
        
        1. NATURAL HUMAN FEATURES:
           - Authentic, warm, and natural expressions (avoid fake 'AI-stare' or uncanny uncanny valley teeth).
           - Real skin textures with natural pores and subtle warmth, NOT plastic or overly airbrushed skin.
           - Natural jawline and normal, anatomically correct dental structure.
        
        2. PRODUCT ACCURACY:
           - Clear aligners must look like ultra-thin, medical-grade, transparent thermoplastic.
           - Micro-refractions of ambient light, non-bulky, perfect fit to teeth.
        
        3. COMMERCIAL LIGHTING:
           - Use soft studio window lighting, gentle depth of field (f/2.8), and clean background blur.
           - No weird floating artifacts, no warped background lines.
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
