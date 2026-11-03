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
st.caption("Internal tool to generate, edit & combine ad visuals via OpenAI Image API (gpt-image-1.5).")

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

tab1, tab2 = st.tabs(["✨ Text-to-Image", "🖼️ Smart Image Studio (Edit & Composite)"])

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

# ----------------- Tab 2: 多功能图像工作站 (单图 Edit / 多图拼接融合) -----------------
with tab2:
    st.subheader("Upload & Transform Photos")
    st.caption("Upload 1 or multiple photo elements. The AI will seamlessly harmonize them based on your instructions.")
    
    # 允许上传最多 4 张图片
    uploaded_files = st.file_uploader(
        "Upload Photos (1-4 images: Product, Model, Background, or Overlay Elements)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"📸 **Uploaded ({len(uploaded_files)} images):**")
        cols = st.columns(min(len(uploaded_files), 4))
        images = []
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file).convert("RGBA")
            images.append(img)
            with cols[idx]:
                st.image(img, caption=f"Img #{idx+1}", use_container_width=True)

        # 拼接模式选择
        layout_mode = "Single Photo Edit"
        if len(images) > 1:
            layout_mode = st.radio(
                "Combination / Stitching Mode",
                [
                    "Side-by-Side (左右拼接对决/对比)", 
                    "Top-Bottom (上下拼接海报)", 
                    "Overlay Sub-Image onto Main Image (小图/画中画叠加)",
                    "2x2 Grid Collage (四格拼图)"
                ]
            )

        edit_instruction = st.text_area(
            "AI Editing & Harmonization Instruction",
            placeholder="e.g., Fuse these photos into a seamless premium commercial ad. Make the background realistic and apply warm natural daylight...",
            height=90
        )

        if st.button("🚀 Process & AI Harmonize", type="primary"):
            if not edit_instruction.strip():
                st.warning("Please enter an instruction describing how AI should transform or blend the photos.")
            else:
                try:
                    # 1. 根据拼接模式合并图片
                    if len(images) == 1 or layout_mode == "Single Photo Edit":
                        composite_img = images[0]
                    
                    elif "Side-by-Side" in layout_mode:
                        # 左右拼接
                        h = min(img.height for img in images)
                        resized = [img.resize((int(img.width * h / img.height), h)) for img in images]
                        total_w = sum(img.width for img in resized)
                        composite_img = Image.new("RGBA", (total_w, h))
                        x_off = 0
                        for img in resized:
                            composite_img.paste(img, (x_off, 0))
                            x_off += img.width
                            
                    elif "Top-Bottom" in layout_mode:
                        # 上下拼接
                        w = min(img.width for img in images)
                        resized = [img.resize((w, int(img.height * w / img.width))) for img in images]
                        total_h = sum(img.height for img in resized)
                        composite_img = Image.new("RGBA", (w, total_h))
                        y_off = 0
                        for img in resized:
                            composite_img.paste(img, (0, y_off))
                            y_off += img.height

                    elif "Overlay" in layout_mode:
                        # 叠加模式：第一张为主图，后面的缩小叠加在右下角/角落
                        main_img = images[0].copy()
                        main_w, main_h = main_img.size
                        sub_img = images[1]
                        sub_w = int(main_w * 0.3)
                        sub_h = int(sub_img.height * sub_w / sub_img.width)
                        sub_resized = sub_img.resize((sub_w, sub_h), Image.Resampling.LANCZOS)
                        main_img.paste(sub_resized, (main_w - sub_w - 20, main_h - sub_h - 20), sub_resized)
                        composite_img = main_img

                    elif "2x2 Grid" in layout_mode:
                        # 四格拼图
                        w, h = 500, 500
                        composite_img = Image.new("RGBA", (w * 2, h * 2))
                        positions = [(0,0), (w,0), (0,h), (w,h)]
                        for i, img in enumerate(images[:4]):
                            composite_img.paste(img.resize((w, h)), positions[i])

                    # 显示预合成草稿
                    st.image(composite_img, caption="Pre-processed Draft Layout", width=400)

                    # 2. 送入 OpenAI 进行 AI 风格统一与重构
                    enhanced_edit_prompt = build_marketing_prompt(edit_instruction, ad_style)
                    st.write("**Optimized Instruction sent to AI:**")
                    st.code(enhanced_edit_prompt, language="text")

                    with st.spinner("AI is harmonizing photo styles, lighting, and rendering final ad visual..."):
                        client = ImageGenClient()
                        img_url = client.edit_ad_image(
                            pil_image=composite_img,
                            prompt=enhanced_edit_prompt,
                            size=img_size
                        )
                        st.image(img_url, caption="Final AI Redesigned Ad Visual", use_container_width=True)
                        st.markdown(f"[📥 Download Full High-Res Image]({img_url})")

                except Exception as e:
                    st.error(f"Processing Error: {e}")
