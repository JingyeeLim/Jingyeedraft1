import os
import streamlit as st
from openai import OpenAI

def build_marketing_prompt(user_input: str, ad_style: str) -> str:
    """
    Dynamically refines user input using gpt-5.4-mini into a professional commercial ad prompt.
    Enforces strict full-coverage clear aligner geometry extending completely to the gingival margin/gumline.
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return (
            f"Commercial photography for DrClearAligners, {ad_style} style: {user_input}. "
            f"100% seamless transparent clear aligner tray fully encasing each tooth from the cutting edge straight up into the gumline (gingival margin). "
            f"The aligner forms a smooth continuous transparent shell right up to the pink gums, zero gaps, zero half-coverage, zero metal wires, 8k resolution."
        )

    client = OpenAI(api_key=api_key)
    
    system_prompt = """You are an expert commercial advertising visual director for DrClearAligners.
Your primary job is to write ultra-precise image generation prompts that force the AI image generator to render anatomically correct, full-coverage clear aligners.

CRITICAL HARD-RULES FOR CLEAR ALIGNERS (MUST ENFORCE IN PROMPT):
1. FULL GUM-TO-TOOTH ENCLOSURE: The clear aligner MUST be described as a single continuous transparent thermoplastic shell that extends ALL THE WAY UP into the pink gumline (gingival margin). It must completely cover 100% of the tooth surface from top to bottom.
2. STRICT NEGATIVE INSTRUCTIONS: Explicitly forbid half-covered teeth, partial trays, lower-edge-only caps, metal brackets, wires, or visible dots/buttons on teeth.
3. VISUAL TEXTURE: Describe it as "crystal-clear, ultra-thin, smooth glossy transparent plastic shell hugging the entire upper and lower arches perfectly up to the pink gingival tissue boundary."

INTENT-BASED ADVERTISING LOGIC:
- If user requests lifestyle/portrait: Describe a warm, confident smile with realistic natural skin texture, soft commercial studio lighting, showing the full-coverage invisible aligners up to the gums clearly upon close inspection.
- If user requests product/macro: Close-up macro focusing on the continuous transparent edge overlapping the gumline seamlessly.

OUTPUT FORMAT:
- Output ONLY the final enhanced English prompt. No explanations, no markdown intro, no quotes."""

    user_prompt = f"""Brand Context: DrClearAligners
Ad Style Preset: {ad_style}
User Concept: {user_input}

Please write an expanded prompt. CRITICAL INSTRUCTION: Emphasize that the clear aligner is a full-coverage tray that extends ALL THE WAY UP TO AND TOUCHES THE PINK GUMLINE (gingival margin), leaving no exposed upper tooth surface."""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,  # 稍微降低随机性，增强指令遵从度
            max_completion_tokens=350
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
            enhanced_prompt = enhanced_prompt[1:-1]
            
        return enhanced_prompt if enhanced_prompt else user_input

    except Exception as e:
        return (
            f"Commercial advertising shot for DrClearAligners, {ad_style} style: {user_input}. "
            f"Ultra-detailed close-up of a smiling model wearing seamless, 100% full-coverage crystal-clear transparent aligner trays extending entirely up to the pink gumline (gingival margin), glossy smooth texture, studio lighting, 8k resolution."
        )
