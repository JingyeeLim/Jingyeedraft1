import os
import streamlit as st
from openai import OpenAI
from prompt_builder import build_marketing_prompt

# 1. Page Configuration
st.set_page_config(
    page_title="DrClearAligners - AI Ad Image Generator",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Hide Streamlit Header, GitHub / Deploy Icon, Main Menu & Footer via Custom CSS
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppHeader {display: none;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. Main Header & Title
st.title("🦷 DrClearAligners Enterprise Visual Portal")
st.markdown(
    "Generate realistic, high-converting commercial advertising images and matching ad copy for DrClearAligners."
)

st.markdown("---")

# 4. Form & Campaign Controls in Single Page Layout
with st.form("ad_generation_form"):
    st.subheader("📋 Campaign Configuration")
    
    col_preset, col_sizes = st.columns([1, 1])
    
    with col_preset:
        ad_style_preset = st.selectbox(
            "Select Advertising Style Preset:",
            options=[
                "Commercial Studio Photography",
                "Cinematic Lifestyle & Smile Shot",
                "Minimalist Medical & Beauty Banner",
                "3D Render & Aesthetic Micro-Shot",
                "Before and After Comparison"
            ],
            index=0
        )
        
        generate_ad_copy = st.checkbox("📝 Also generate social media Ad Copy (FB/IG)", value=True)

    with col_sizes:
        selected_sizes = st.multiselect(
            "Select required aspect ratios (Generates only selected sizes):",
            options=["1:1 Square (1024x1024)", "9:16 Story/Reels (1024x1792)", "16:9 Landscape (1792x1024)"],
            default=["1:1 Square (1024x1024)"],
            help="Select only the dimensions you need for your campaign to save API credits."
        )

    st.markdown("---")
    st.subheader("💡 Image Concept Description")
    
    user_input = st.text_area(
        "Enter your image description or concept:",
        value="A confident young woman smiling naturally with transparent clear aligners in a bright minimalist living room.",
        height=100,
        placeholder="e.g., A macro close-up of crystal-clear aligner resting on white marble with morning sunlight."
    )
    
    submit_button = st.form_submit_button("🚀 Generate Ad Visuals", use_container_width=True)

# Size Mapping Table for API
SIZE_MAPPING = {
    "1:1 Square (1024x1024)": "1024x1024",
    "9:16 Story/Reels (1024x1792)": "1024x1792",
    "16:9 Landscape (1792x1024)": "1792x1024"
}

# Helper function to generate Ad Copy via gpt-5.4-mini
def generate_marketing_copy(user_concept: str, ad_style: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    system_prompt = """
    You are a high-converting conversion copywriter for DrClearAligners.
    Based on the user's campaign theme, write 3 engaging Facebook/Instagram ad caption options.
    Each caption must include:
    1. Attention-grabbing Headline
    2. Primary Selling Point / Key Benefit
    3. Strong Call-To-Action (CTA) with relevant emojis.
    Keep the tone modern, confident, clean, and appealing to young professionals.
    """
    
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Ad Style: {ad_style}\nCampaign Concept: {user_concept}"}
        ],
        temperature=0.7,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

# 5. Generation Process Flow
if submit_button:
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.error("❌ OpenAI API Key not found! Please configure OPENAI_API_KEY in Streamlit Secrets or Environment Variables.")
    elif not selected_sizes:
        st.warning("⚠️ Please select at least one image dimension before generating.")
    elif not user_input.strip():
        st.warning("⚠️ Please enter an image concept description.")
    else:
        # Step A: Refine Prompt using gpt-5.4-mini
        with st.spinner("🧠 Visual Director (gpt-5.4-mini) is refining the master prompt..."):
            master_prompt = build_marketing_prompt(user_input, ad_style_preset)
            
        st.success("✨ Master Prompt Ready!")
        with st.expander("🔍 View Final Technical Prompt sent to OpenAI API"):
            st.code(master_prompt, language="text")

        # Step B: Render Images using gpt-image-2 Model
        st.markdown("---")
        st.subheader("🖼️ Generated Commercial Visuals")
        
        client = OpenAI(api_key=api_key)
        cols = st.columns(len(selected_sizes))
        
        for idx, size_name in enumerate(selected_sizes):
            target_size = SIZE_MAPPING[size_name]
            with cols[idx]:
                st.markdown(f"**{size_name}**")
                with st.spinner(f"Rendering {size_name}..."):
                     try:
                        res = client.images.generate(
                            model="gpt-image-2",
                            prompt=master_prompt,
                            size=target_size,
                            n=1
                        )
                        image_url = res.data[0].url
                        st.image(image_url, caption=f"DrClearAligners - {size_name}", use_column_width=True)
                    except Exception as e:
                        st.error(f"Failed to generate {size_name}: {str(e)}")

        # Step C: Generate Social Media Ad Copy via gpt-5.4-mini
        if generate_ad_copy:
            st.markdown("---")
            st.subheader("📝 Recommended Social Media Ad Captions (FB / IG)")
            with st.spinner("✍️ gpt-5.4-mini is crafting high-converting ad copy..."):
                try:
                    copy_text = generate_marketing_copy(user_input, ad_style_preset, api_key)
                    st.info(copy_text)
                except Exception as e:
                        st.warning(f"Could not generate ad copy: {str(e)}")
