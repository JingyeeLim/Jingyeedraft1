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

# 选项卡：单图文生图 vs 多图/Logo 合成重构
tab1, tab2 = st.tabs(["✨ Text-to-Image", "🖼️ Multi-Image / Logo Composite"])

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

# ----------------- Tab 2: 多图上传 (主图 + Logo 合成) -----------------
with tab2:
    st.subheader("Composite Main Product Photo with Brand Logo")
    
    col1, col2 = st.columns(2)
    with col1:
        main_bg_file = st.file_uploader("1. Upload Main Product Photo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    with col2:
        logo_file = st.file_uploader("2. Upload Brand Logo (PNG Transparent)", type=["png", "jpg", "jpeg"])

    logo_position = st.selectbox(
        "Logo Overlay Position",
        ["Top Right (右上角)", "Bottom Right (右下角)", "Top Left (左上角)", "Bottom Left (左下角)"]
    )
    
    logo_size_ratio = st.slider("Logo Size Ratio", min_value=0.1, max_value=0.4, value=0.2, step=0.05)

    edit_instruction = st.text_area(
        "AI Harmonization Instruction",
        placeholder="e.g., Seamlessly blend the brand logo onto the image with natural lighting, soft shadow, and studio polish...",
        height=80
    )
    
    submit_btn2 = st.button("🚀 Composite & Redesign Image", type="primary")

    if submit_btn2:
        if not main_bg_file:
            st.warning("Please upload the main product photo first.")
        else:
            try:
                # 1. 打开主图并转为 RGBA 模式
                main_img = Image.open(main_bg_file).convert("RGBA")
                
                # 2. 如果上传了 Logo，自动进行像素级合成
                if logo_file:
                    logo_img = Image.open(logo_file).convert("RGBA")
                    
                    # 动态计算 Logo 尺寸
                    main_w, main_h = main_img.size
                    target_logo_w = int(main_w * logo_size_ratio)
                    aspect_ratio = logo_img.height / logo_img.width
                    target_logo_h = int(target_logo_w * aspect_ratio)
                    logo_resized = logo_img.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)
                    
                    # 计算定位坐标
                    padding = int(main_w * 0.03)
                    if "Top Right" in logo_position:
                        pos = (main_w - target_logo_w - padding, padding)
                    elif "Bottom Right" in logo_position:
                        pos = (main_w - target_logo_w - padding, main_h - target_logo_h - padding)
                    elif "Top Left" in logo_position:
                        pos = (padding, padding)
                    else:  # Bottom Left
                        pos = (padding, main_h - target_logo_h - padding)
                    
                    # 粘贴 Logo（保留透明通道）
                    main_img.paste(logo_resized, pos, logo_resized)
                
                # 展示预合成的原图预览
                st.image(main_img, caption="Pre-composited Reference Image", width=350)
                
                # 3. 构造强化 Prompt 送入 AI 进行自然融合重构
                prompt_text = edit_instruction if edit_instruction.strip() else "Seamlessly integrate the brand element onto the product photo with realistic studio lighting."
                enhanced_edit_prompt = build_marketing_prompt(prompt_text, ad_style)
                
                with st.spinner("AI is harmonizing and generating final high-res ad visual..."):
                    client = ImageGenClient()
                    img_url = client.edit_ad_image(
                        pil_image=main_img,
                        prompt=enhanced_edit_prompt,
                        size=img_size
                    )
                    st.image(img_url, caption="Final Branded Ad Visual", use_container_width=True)
                    st.markdown(f"[📥 Download Full High-Res Image]({img_url})")
                    
            except Exception as e:
                st.error(f"Processing Error: {e}")
