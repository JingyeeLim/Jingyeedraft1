import io
import base64
import requests
import streamlit as st
from PIL import Image
from openai_client import ImageGenClient
from prompt_builder import build_marketing_prompt

st.set_page_config(page_title="Enterprise AI Ad Generator", page_icon="🎨", layout="centered")

st.markdown(
    """
    <h1 style='white-space: nowrap; font-size: 2rem; margin-bottom: 0.5rem;'>
        🎯 Enterprise Marketing Image Generator
    </h1>
    """, 
    unsafe_allow_html=True
)
st.caption("Internal tool to generate & harmonize commercial ad visuals via OpenAI API.")

with st.sidebar:
    st.header("⚙️ Image Settings")
    ad_style = st.selectbox(
        "Ad Style Preset",
        [
            "Commercial Studio Photography",
            "3D Render & Aesthetic Micro-Shot",
            "Minimalist Medical & Beauty Banner",
            "Cinematic Lifestyle & Smile Shot"
        ]
    )
    img_size = st.selectbox("Resolution", ["1024x1024", "1024x1792", "1792x1024"])
    
    st.markdown("---")
    st.info("💡 **Cost Control Active**: Chat API endpoint is locked out to conserve company API tokens.")

tab1, tab2 = st.tabs(["✨ Text-to-Image", "🖼️ Photo Harmonization (Single Photo Upload)"])

def render_download_and_export_section(img_source):
    """
    Helper function to render multiformat downloads and quick editor options.
    Supports HTTP URLs, Base64 data strings, and PIL Image objects.
    """
    st.markdown("---")
    st.subheader("📥 Export Options & Next Steps")
    
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
                label="💾 Download HD PNG (Lossless)",
                data=png_buf.getvalue(),
                file_name="DrClearAligners_Ad_Visual.png",
                mime="image/png",
                use_container_width=True
            )
            
        # JPG Download Buffer
        jpg_buf = io.BytesIO()
        rgb_img = pil_img.convert("RGB")
        rgb_img.save(jpg_buf, format="JPEG", quality=95)
        with col_jpg:
            st.download_button(
                label="💾 Download JPG (Web Compressed)",
                data=jpg_buf.getvalue(),
                file_name="DrClearAligners_Ad_Visual.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
            
        st.info(
            "🎨 **Next Step for Marketing Team:**\n"
            "- **Canva**: Open [Canva](https://www.canva.com/) -> Create Design -> Upload this rendered background to overlay DrClearAligners logo and Chinese typography.\n"
            "- **Photoshop**: Import into PS to add vector logos, brand typography, or adjust curves."
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
        submit_btn1 = st.form_submit_button("🚀 Generate Ad Image", type="primary")

    if submit_btn1:
        if not raw_prompt.strip():
            st.warning("Please input a description for the image.")
        else:
            enhanced_prompt = build_marketing_prompt(raw_prompt, ad_style)
            st.write("**Optimized Prompt sent to OpenAI:**")
            st.code(enhanced_prompt, language="text")
            
            with st.spinner("Generating high-resolution image..."):
                try:
                    client = ImageGenClient()
                    img_url = client.generate_ad_image(
                        prompt=enhanced_prompt,
                        size=img_size
                    )
                    st.image(img_url, caption="Generated Ad Visual", use_container_width=True)
                    render_download_and_export_section(img_url)
                except Exception as e:
                    st.error(f"Error: {e}")

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

        if st.button("🚀 Transform Photo with AI", type="primary"):
            if not edit_instruction.strip():
                st.warning("Please enter your design instruction.")
            else:
                try:
                    enhanced_edit_prompt = build_marketing_prompt(edit_instruction, ad_style)
                    st.write("**Optimized Instruction sent to AI:**")
                    st.code(enhanced_edit_prompt, language="text")

                    with st.spinner("AI is harmonizing photo background and lighting..."):
                        client = ImageGenClient()
                        img_url = client.edit_ad_image(
                            pil_image=input_img,
                            prompt=enhanced_edit_prompt,
                            size=img_size
                        )
                        st.image(img_url, caption="Final AI Harmonized Ad Visual", use_container_width=True)
                        render_download_and_export_section(img_url)

                except Exception as e:
                    st.error(f"Processing Error: {e}")
