import os
import streamlit as st
from openai import OpenAI

def build_marketing_prompt(user_input: str, ad_style: str) -> str:
    """
    Dynamically refines user input using gpt-5.4-mini into a professional commercial ad prompt.
    Enforces visible glossy clear aligner material extending to the gumline.
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return (
            f"Commercial photography for DrClearAligners, {ad_style} style: {user_input}. "
            f"Model wearing glossy transparent clear aligners with subtle light reflections along the edges and full gumline coverage, 8k resolution."
        )

    client = OpenAI(api_key=api_key)
    
    system_prompt = """You are an expert commercial advertising visual director for DrClearAligners.
Your primary job is to write image generation prompts that ensure clear aligners are VISIBLE, REALISTIC, and ENTIRELY ENCASE TEETH UP TO THE GUMLINE.

CRITICAL VISIBILITY & FIT RULES:
1. VISIBLE PLASTIC MATERIAL & REFLECTIONS: The clear aligner MUST be visually distinguishable. Describe it with glossy plastic sheen, subtle specular highlights along tooth contours, and clear transparent tray outlines. Do not render bare teeth.
2. FULL GUM-TO-TOOTH ENCLOSURE: The clear aligner tray must extend continuously from the tooth edge straight up into the pink gumline (gingival margin) without stopping halfway.
3. NO METAL: Zero metal wires, brackets, or dark gaps.

PROMPT CONSTRUCTION INSTRUCTION:
- Always include terms like: "visible glossy clear aligner tray with natural light reflections", "crystal-clear thermoplastic shell with smooth glossy edge tracing the gumline", "subtle highlight reflections on transparent aligner surface".

OUTPUT FORMAT:
- Output ONLY the final enhanced English prompt. No explanations, no markdown intro, no quotes."""

    user_prompt = f"""Brand Context: DrClearAligners
Ad Style Preset: {ad_style}
User Concept: {user_input}

Write an expanded prompt ensuring the clear aligners are VISIBLY PRESENT with glossy plastic light reflections, while fully encasing the upper and lower teeth completely up to the gumline."""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_completion_tokens=350
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
            enhanced_prompt = enhanced_prompt[1:-1]
            
        return enhanced_prompt if enhanced_prompt else user_input

    except Exception as e:
        return (
            f"Commercial portrait shot for DrClearAligners, {ad_style} style: {user_input}. "
            f"Model wearing visible glossy transparent aligners with subtle specular light reflections and clear tray outlines covering all teeth up to the pink gumline, 8k resolution."
        )
