import streamlit as st
from openai_client import ImageGenClient
from prompt_builder import build_marketing_prompt

st.set_page_config(page_title="Enterprise AI Ad Generator", page_icon="🎨", layout="centered")

# 使用自定义 CSS 强制标题在一行内显示 (nowrap) 并微调字号
st.markdown(
    """
    <h1 style='white-space: nowrap; font-size: 2rem; margin-bottom: 0.5rem;'>
        🎯 Enterprise Marketing Image Generator
    </h1>
    """, 
    unsafe_allow_html=True
)
st.caption("Internal tool to generate high-converting ad visuals via OpenAI Image API (gpt-image-1.5).")

# Sidebar Configuration
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
    img_quality = st.selectbox("Quality", ["standard", "hd"])
    
    st.markdown("---")
    st.info("💡 **Cost Control Active**: Chat API endpoint is locked out to conserve company API tokens.")

# Main Form Interface
with st.form("ad_gen_form"):
    raw_prompt = st.text_area(
        "Ad Description / Product Concept",
        placeholder="e.g., Ultra-clear invisible aligners placed on a pristine marble vanity table next to a glass of sparkling water...",
        height=100
    )
    submit_btn = st.form_submit_button("🚀 Generate Ad Image", type="primary")

if submit_btn:
    if not raw_prompt.strip():
        st.warning("Please input a description for the image.")
    else:
        enhanced_prompt = build_marketing_prompt(raw_prompt, ad_style)
        st.write("**Optimized Prompt sent to OpenAI API:**")
        st.code(enhanced_prompt, language="text")
        
        with st.spinner("Generating high-resolution image..."):
            try:
                client = ImageGenClient()
                img_url = client.generate_ad_image(
                    prompt=enhanced_prompt,
                    size=img_size,
                    quality=img_quality
                )
                st.image(img_url, caption="Generated Ad Visual", use_container_width=True)
                st.markdown(f"[📥 Download Full High-Res Image]({img_url})")
            except Exception as e:
                st.error(f"Error: {e}")
