import os
import streamlit as st
from openai import OpenAI

def build_marketing_prompt(user_input: str, ad_style: str) -> str:
    """
    使用 GPT-4o 充当顶级商业视觉总监，把用户的简单想法扩写为专业级商业广告 Prompt。
    内置了商业光影、材质折射、人像真实感约束以及抗 AI 畸变规则。
    """
    # 1. 尝试从 Streamlit Secrets 或环境变量读取 API Key
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    # 2. 兜底机制：若无 Key，退回到基础规则拼接
    if not api_key:
        return (
            f"Commercial photography for DrClearAligners, {ad_style} style: {user_input}. "
            f"Ultra-clean lighting, high-resolution medical thermoplastic clear aligners, "
            f"8k resolution, professional advertising aesthetic."
        )

    client = OpenAI(api_key=api_key)
    
    # 3. 核心 System Prompt：定义 GPT-4o 的 AI 视觉总监角色与限制
    system_prompt = """
    You are an award-winning Commercial Visual Director and Prompt Engineer for DrClearAligners (a premium clear aligners dental brand).
    Your task is to take a brief user request and transform it into a single, master-level text prompt for AI image generation.

    STRICT GUIDELINES FOR PROMPT CONSTRUCTION:

    1. PRODUCT REALISM (DRCLEARALIGNERS):
       - Clear aligners must look like medical-grade, crystal-clear, ultra-thin thermoplastic.
       - Highlight subtle light refractions, pristine optical clarity, smooth contours, and custom precision fit.

    2. HUMAN MODEL & AESTHETIC REALISM (If models are present):
       - Natural, warm, and authentic expressions (AVOID robotic or uncanny 'AI-stare').
       - Real human skin texture with subtle pores, natural warmth, and authentic teeth anatomy.
       - Natural jawlines and realistic smile dynamics.

    3. COMMERCIAL ADVERTISING & LIGHTING:
       - Incorporate specific commercial photography parameters: soft studio rim lighting, 85mm f/1.8 lens depth of field, subtle shadow falloff, high-end editorial look.
       - Focus on premium pastel, marble, bright daylight, or luxury aesthetic environments.

    4. COMPOSITION & LOGO OVERLAY PREPARATION:
       - Ensure clean negative space (top or bottom area) to allow marketing teams to overlay official brand logos and typography later.
       - DO NOT render text, letters, or fake company logos inside the image.

    5. OUTPUT FORMAT:
       - Output ONLY the final enhanced English prompt. No greetings, no explanations, no quotes.
    """

    # 4. User Prompt 构建：结合当前选择的 Style Preset
    user_prompt = f"""
    Target Brand: DrClearAligners
    Selected Ad Style Preset: {ad_style}
    User's Input Concept: {user_input}

    Please rewrite and expand this concept into a stunning, detailed commercial photography prompt.
    """

    try:
        # 调用 GPT-4o 进行智能扩写
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=300
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        
        # 移除可能误生成的包裹引号
        if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
            enhanced_prompt = enhanced_prompt[1:-1]
            
        return enhanced_prompt

    except Exception as e:
        # 如果 API 调用遇到限制或异常，自动降级为规则扩写，保证前端依然可出图
        return (
            f"Commercial advertising shot for DrClearAligners, {ad_style} style: {user_input}. "
            f"Featuring crystal-clear transparent aligners, soft studio window lighting, depth of field, "
            f"ultra-clean aesthetics, luxury commercial photography, 8k."
        )
