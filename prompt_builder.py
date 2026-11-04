import os
import streamlit as st
from openai import OpenAI

def build_marketing_prompt(user_input: str, ad_style: str) -> str:
    """
    Dynamically refines user input using GPT-4o into a professional commercial ad prompt.
    Supports both standard clear aligner ads and comparison ads (metal braces vs clear aligners).
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return (
            f"Commercial photography for DrClearAligners, {ad_style} style: {user_input}. "
            f"100% crystal-clear transparent plastic aligner tray, zero metal wires, zero brackets, "
            f"ultra-clean aesthetics, 8k resolution."
        )

    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    You are an expert commercial advertising visual director for DrClearAligners.
    Your task is to convert brief marketing requests into high-impact English image generation prompts.

    INTENT-BASED PRODUCT LOGIC:

    1. CASE A: COMPARISON ADS (Triggered if user mentions "comparison", "vs", "before and after", "traditional braces", or "versus")
       - Explicitly describe a split-screen or side-by-side comparison layout.
       - SIDE 1 (Traditional Braces): Show metal braces with visible silver brackets, metal dots, and archwires.
       - SIDE 2 (DrClearAligners): Show a sleek, 100% crystal-clear transparent thermoplastic aligner tray with zero metal.
       - Ensure clear visual contrast highlighting the aesthetic advantage of DrClearAligners.

    2. CASE B: STANDARD PRODUCT & LIFESTYLE ADS (Default mode for all other requests)
       - ABSOLUTELY NO METAL BRACES, NO METAL WIRES, NO SILVER BRACKETS, NO METAL DOTS ON TEETH.
       - DO NOT use the word "braces". Use "transparent clear aligner", "invisible thermoplastic tray", or "seamless clear aligner".
       - The product MUST be explicitly described as an ultra-thin, smooth, 100% crystal-clear transparent plastic tray resting invisibly over teeth.

    GENERAL COMMERCIAL ADVERTISING RULES:
    - Human Models: Natural skin textures with warmth, authentic smiles, anatomically correct dental structure. Avoid plastic AI looks.
    - Lighting & Camera: 85mm f/1.8 studio lens, soft lighting, commercial editorial quality.
    - Branding Space: DO NOT render any logos, text, or letters inside the image. Keep clean negative space at top or bottom for official logo overlay.

    OUTPUT FORMAT:
    - Output ONLY the final enhanced English prompt. No explanations, no markdown intro, no quotes.
    """

    user_prompt = f"""
    Brand Context: DrClearAligners
    Ad Style Preset: {ad_style}
    User Concept: {user_input}

    Analyze the user concept. If it is a comparison request, generate a side-by-side comparison prompt. Otherwise, generate a 100% clear aligner prompt without any metal components.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
            enhanced_prompt = enhanced_prompt[1:-1]
            
        return enhanced_prompt

    except Exception as e:
        return (
            f"Commercial advertising shot for DrClearAligners, {ad_style} style: {user_input}. "
            f"Featuring 100% crystal-clear transparent plastic aligners, zero metal brackets, "
            f"ultra-clean aesthetics, soft studio lighting, 8k resolution."
        )
