import streamlit as st
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
st.caption("Internal tool to generate & redesign ad visuals via OpenAI Image API (gpt-image-1.5).")

# 侧边栏配置
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

# 使用 Tabs 区分 "文字生图" 与 "上传图片二次设计"
tab1, tab2 = st.tabs(["✨ Text-to-Image (New Visual)", "🖼️ Image-to-Image (Redesign Concept)"])

# ----------------- Tab 1: 文生图 -----------------
with tab1:
    with st.form("text_gen_form"):
        raw_prompt = st.text_area(
            "Ad Description / Product Concept",
            placeholder="e.g., Ultra-clear invisible aligners placed on a pristine marble vanity table...",
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
                    st.markdown(f"[📥 Download Full High-Res Image]({img_url})")
                except Exception as e:
                    st.error(f"Error: {e}")

# ----------------- Tab 2: 上传图片二次设计 -----------------
with tab2:
    with st.form("img_edit_form"):
        uploaded_file = st.file_uploader(
            "Upload Reference Product Image (PNG/JPG)", 
            type=["png", "jpg", "jpeg"],
            help="Upload an existing photo of aligner or product to modify."
        )
        edit_instruction = st.text_area(
            "Design / Modification Instruction",
            placeholder="e.g., Change the background to a minimalist pastel dental clinic, add soft sunlight rays and a glass of water...",
            height=80
        )
        submit_btn2 = st.form_submit_button("🎨 Redesign Image", type="primary")

    if submit_btn2:
        if not uploaded_file:
            st.warning("Please upload a reference image first.")
        elif not edit_instruction.strip():
            st.warning("Please input modification instructions.")
        else:
            enhanced_edit_prompt = build_marketing_prompt(edit_instruction, ad_style)
            st.write("**Optimized Edit Instruction:**")
            st.code(enhanced_edit_prompt, language="text")
            
            # 展示原图 preview
            st.image(uploaded_file, caption="Original Reference Image", width=300)
            
            with st.spinner("Redesigning image based on reference..."):
                try:
                    client = ImageGenClient()
                    # 将上传的文件流转给 API
                    img_url = client.edit_ad_image(
                        image_file=uploaded_file,
                        prompt=enhanced_edit_prompt,
                        size=img_size
                    )
                    st.image(img_url, caption="Redesigned Ad Visual", use_container_width=True)
                    st.markdown(f"[📥 Download Redesigned High-Res Image]({img_url})")
                except Exception as e:
                    st.error(f"Error: {e}")
