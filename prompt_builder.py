import os
import streamlit as st
from openai import OpenAI

def build_marketing_prompt(user_input: str, ad_style: str) -> str:
    """
    Dynamically refines user input using GPT-4o into a professional commercial ad prompt.
    Enforces full aligner coverage extending completely to the gumline.
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return (
            f"Commercial photography for DrClearAligners, {ad_style} style: {user_input}. "
            f"100% crystal-clear transparent plastic aligner tray fully covering all teeth up to the gumline, "
            f"zero metal wires, 8k resolution."
        )

    client = OpenAI(api_key=api_key)
    
    system_prompt = """
        You are an expert commercial advertising visual director for DrClearAligners.
        Your task is to convert brief marketing requests into high-impact English image generation prompts.

        CRITICAL ALIGNER FIT & GEOMETRY RULES (MUST FOLLOW):
        1. FULL TOOTH COVERAGE: The transparent aligner tray MUST fully encase and cover every tooth entirely, extending all the way up to the gumline (gingival margin).
        2. NO PARTIAL MASKING: Do NOT render aligners that only cover half of the tooth or just the bottom edges. It must be a complete, custom-molded thermoplastic shell over the full surface of upper and lower teeth.
        3. NO METAL COMPONENTS: Absolutely no metal braces, wires, or brackets (unless user explicitly requests a comparison ad).

        INTENT-BASED PRODUCT LOGIC:
        1. CASE A: COMPARISON ADS (Triggered if user mentions "comparison", "vs", "before and after", "traditional braces", or "versus")
        - Explicitly describe a split-screen or side-by-side layout.
        - LEFT (Before/Traditional): Misaligned teeth or traditional metal braces.
        - RIGHT (After/DrClearAligners): Straight white teeth fully encased in crystal-clear aligners extending completely to the gumline.

        2. CASE B: STANDARD PRODUCT & LIFESTYLE ADS (Default mode)
        - Sleek, 100% crystal-clear, ultra-thin transparent thermoplastic tray covering teeth fully from edge to gumline.

        GENERAL COMMERCIAL ADVERTISING RULES:
        - Human Models: Natural skin textures with warmth, authentic smiles, anatomically correct dental structure.
        - Lighting & Camera: 85mm f/1.8 studio lens, soft lighting, commercial editorial quality.
        - Branding Space: DO NOT render any logos, text, or letters inside the image. Keep clean negative space at top or bottom for official logo overlay.

        OUTPUT FORMAT:
        - Output ONLY the final enhanced English prompt. No explanations, no markdown intro, no quotes.
    """

    user_prompt = f"""
    Brand Context: DrClearAligners
    Ad Style Preset: {ad_style}
    User Concept: {user_input}

    Please build an expanded prompt ensuring the clear aligner fully covers the entire teeth up to the gumline with no partial coverage errors.
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
            f"Featuring 100% crystal-clear transparent plastic aligners fully covering all teeth up to the gumline, "
            f"ultra-clean aesthetics, soft studio lighting, 8k resolution."
            )
