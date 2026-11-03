import streamlit as st
from openai_client import ImageGenClient
from prompt_builder import build_marketing_prompt

st.set_page_config(page_title="Enterprise AI Ad Generator", page_icon="🎨", layout="centered")

st.title("🎯 Enterprise Marketing Image Generator")
st.caption("Internal tool to generate high-converting ad visuals via OpenAI DALL·E 3 (Chat access disabled).")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ Image Settings")
    ad_style = st.selectbox(
        "Ad Style Preset",
        ["Commercial Studio (商业摄影)", "3D Tech Render (3D 科技感)", "Minimalist Banner (极简海报)", "Cinematic Lifestyle (生活场景)"]
    )
    img_size = st.selectbox("Resolution", ["1024x1024", "1024x1792", "1792x1024"])
    img_quality = st.selectbox("Quality", ["standard", "hd"])
    
    st.markdown("---")
    st.info("💡 **Cost Control Active**: Chat API endpoint is locked out to conserve company API tokens.")

# 表单主体 (物理隔离 Chat 接口)
with st.form("ad_gen_form"):
    raw_prompt = st.text_area(
        "Ad Description / Product Concept",
        placeholder="e.g., A wireless noise-canceling headphone resting on a polished wooden desk with coffee cup...",
        height=100
    )
    submit_btn = st.form_submit_button("🚀 Generate Ad Image", type="primary")

if submit_btn:
    if not raw_prompt.strip():
        st.warning("Please input a description for the image.")
    else:
        enhanced_prompt = build_marketing_prompt(raw_prompt, ad_style)
        st.write("**Optimized Prompt sent to DALL·E 3:**")
        st.code(enhanced_prompt, language="text")
        
        with st.spinner("Generating high-resolution image..."):
            try:
                client = ImageGenClient()
                img_url = client.generate_ad_image(
                    prompt=enhanced_prompt,
                    size=img_size,
                    quality=img_quality
                )
                # 使用最新版 Streamlit 的 use_container_width 参数
                st.image(img_url, caption="Generated Ad Visual", use_container_width=True)
                st.markdown(f"[📥 Download Full High-Res Image]({img_url})")
            except Exception as e:
                st.error(f"Error: {e}")
