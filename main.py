import io
import base64
import os
import requests
import streamlit as st
from PIL import Image
from openai_client import ImageGenClient
from prompt_builder import build_marketing_prompt
from openai import OpenAI

# 1. Page Configuration
st.set_page_config(
    page_title="DrClearAligner Marketing Ad Generator", 
    page_icon="🦷", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Hide Header, Main Menu, Footer, and Sidebar
st.markdown(
    """
    <style>
    /* Hide top header bar, main menu, and footer */
    header {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    /* Hide sidebar and toggle buttons */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarExpandButton"] {
        display: none !important;
    }
    
    /* Adjust top container padding */
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Main Header Title
st.markdown(
    """
    <h1 style='white-space: nowrap; font-size: 2rem; margin-bottom: 0.5rem;'>
        Enterprise Marketing Image Generator
    </h1>
    """, 
    unsafe_allow_html=True
)
st.caption("Internal tool to generate & harmonize commercial ad visuals via OpenAI API.")

# 4. Helper Function: Generate Social Media Ad Copy via gpt-5.4-mini
def generate_marketing_copy(user_concept: str, ad_style: str) -> str:
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    system_prompt = """You are a high-converting conversion copywriter for DrClearAligners.
Based on the user's campaign theme, write 3 engaging Facebook/Instagram ad caption options.
Each caption must include:
1. Attention-grabbing Headline
2. Primary Selling Point / Key Benefit
3. Strong Call-To-Action (CTA) with relevant emojis.
Keep the tone modern, confident, clean, and appealing to young professionals."""

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Ad Style: {ad_style}\nCampaign Concept: {user_concept}"}
        ],
        temperature=0.7,
        max_completion_tokens=400
    )
    return response.choices[0].message.content.strip()

# 5. Global Configurations & Presets
with st.expander("⚙️ Image Generation Settings (Global Presets)", expanded=True):
    col_preset, col_res = st.columns(2)
    with col_preset:
        ad_style = st.selectbox(
            "Ad Style Preset",
            [
                "Commercial Studio Photography",
                "3D Render & Aesthetic Micro-Shot",
                "Minimalist Medical & Beauty Banner",
                "Cinematic Lifestyle & Smile Shot"
            ]
        )
        generate_ad_copy = st.checkbox("📝 Also generate social media Ad Copy (FB/IG)", value=True)
        
    with col_res:
        selected_sizes = st.multiselect(
            "Select required aspect ratios:",
            options=["1024x1024", "1024x1536", "1536x1024"],
            default=["1024x1024"],
            help="Generates only the checked resolutions to save API credits."
        )

st.markdown("---")

tab1, tab2 = st.tabs(["Text-to-Image", "Photo Harmonization"])

# 6. Helper Function: Render Multi-Format Export Section (HD PNG & Web JPG)
def render_download_and_export_section(img_source, size_label=""):
    """
    Helper function to render multiformat downloads and quick editor options.
    Supports HTTP URLs, Base64 data strings, and PIL Image objects safely.
    """
    st.markdown("---")
    st.subheader(f"📥 Export Options & Next Steps ({size_label})")
    
    try:
        if isinstance(img_source, str):
            if img_source.startswith("data:image"):
                base64_data = img_source.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                pil_img = Image.open(io.BytesIO(image_bytes))
            elif img_source.startswith("http"):
                response = requests.get(img_source)
                pil_img = Image.open(io.BytesIO(response.content))
            else:
                raise ValueError("Unsupported image string format.")
        else:
            pil_img = img_source

        col_png, col_jpg = st.columns(2)
        
        # PNG Download Buffer
        png_buf = io.BytesIO()
        pil_img.save(png_buf, format="PNG")
        with col_png:
            st.download_button(
                label=f"💾 Download HD PNG ({size_label})",
                data=png_buf.getvalue(),
                file_name=f"DrClearAligners_{size_label}.png",
                mime="image/png",
                use_container_width=True,
                key=f"png_{size_label}"
            )
            
        # JPG Download Buffer
        jpg_buf = io.BytesIO()
        rgb_img = pil_img.convert("RGB")
        rgb_img.save(jpg_buf, format="JPEG", quality=95)
        with col_jpg:
            st.download_button(
                label=f"💾 Download JPG ({size_label})",
                data=jpg_buf.getvalue(),
                file_name=f"DrClearAligners_{size_label}.jpg",
                mime="image/jpeg",
                use_container_width=True,
                key=f"jpg_{size_label}"
            )
            
    except Exception as e:
        st.error(f"Export Rendering Error: {str(e)}")

# --- Tab 1: Text-to-Image ---
with tab1:
    with st.form("text_gen_form"):
        raw_prompt = st.text_area(
            "Ad Description / Product Concept",
            placeholder="e.g., A pair of transparent aligners on a white marble table surrounded by light water droplets and clean morning light...",
            height=100
        )
        submit_btn1 = st.form_submit_button("Generate Ad Image", type="primary")

    if submit_btn1:
        if not raw_prompt.strip():
            st.warning("Please input a description for the image.")
        elif not selected_sizes:
            st.warning("Please select at least one resolution in Settings above.")
        else:
            enhanced_prompt = build_marketing_prompt(raw_prompt, ad_style)
            st.write("**Optimized Prompt sent to OpenAI:**")
            st.code(enhanced_prompt, language="text")
            
            client = ImageGenClient()
            
            # Loop through selected resolutions to generate images
            for img_size in selected_sizes:
                with st.spinner(f"Generating high-resolution image ({img_size})..."):
                    try:
                        img_url = client.generate_ad_image(
                            prompt=enhanced_prompt,
                            size=img_size
                        )
                        st.image(img_url, caption=f"Generated Ad Visual - {img_size}", use_container_width=True)
                        render_download_and_export_section(img_url, size_label=img_size)
                    except Exception as e:
                        st.error(f"Error for size {img_size}: {e}")

            # Generate matching marketing copy if enabled
            if generate_ad_copy:
                st.markdown("---")
                st.subheader("📝 Recommended Social Media Ad Captions (FB / IG)")
                with st.spinner("✍️ Crafting high-converting ad copy..."):
                    try:
                        copy_text = generate_marketing_copy(raw_prompt, ad_style)
                        st.info(copy_text)
                    except Exception as e:
                        st.warning(f"Could not generate ad copy: {str(e)}")

# --- Tab 2: Single Photo Upload & Redesign ---
with tab2:
    st.subheader("Upload 1 Photo & Transform Scene")
    st.caption("Upload a product or reference shot. AI will reimagine the background and studio lighting while keeping clean quality.")
    
    uploaded_file = st.file_uploader(
        "Upload Product Photo (PNG or JPG)",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        input_img = Image.open(uploaded_file).convert("RGBA")
        st.image(input_img, caption="Original Uploaded Photo", width=300)
        
        edit_instruction = st.text_area(
            "Redesign / Background Transformation Instruction",
            placeholder="e.g., Place the transparent aligner onto a smooth marble countertop with soft morning sunbeams and delicate water droplets. Clean commercial studio photography.",
            height=90
        )

        if st.button("Transform Photo with AI", type="primary"):
            if not edit_instruction.strip():
                st.warning("Please enter your design instruction.")
            elif not selected_sizes:
                st.warning("Please select at least one resolution in Settings above.")
            else:
                try:
                    enhanced_edit_prompt = build_marketing_prompt(edit_instruction, ad_style)
                    st.write("**Optimized Instruction sent to AI:**")
                    st.code(enhanced_edit_prompt, language="text")

                    client = ImageGenClient()
                    for img_size in selected_sizes:
                        with st.spinner(f"AI is harmonizing photo background and lighting ({img_size})..."):
                            img_url = client.edit_ad_image(
                                pil_image=input_img,
                                prompt=enhanced_edit_prompt,
                                size=img_size
                            )
                            st.image(img_url, caption=f"Final AI Harmonized Ad Visual - {img_size}", use_container_width=True)
                            render_download_and_export_section(img_url, size_label=img_size)

                    # Generate matching ad copy for Tab 2
                    if generate_ad_copy:
                        st.markdown("---")
                        st.subheader("📝 Recommended Social Media Ad Captions (FB / IG)")
                        with st.spinner("✍️ Crafting high-converting ad copy..."):
                            try:
                                copy_text = generate_marketing_copy(edit_instruction, ad_style)
                                st.info(copy_text)
                            except Exception as copy_err:
                                st.warning(f"Could not generate ad copy: {str(copy_err)}")

                except Exception as e:
                    st.error(f"Processing Error: {e}")
