import streamlit as st
from PIL import Image, ImageDraw
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

tab1, tab2 = st.tabs(["✨ Text-to-Image", "🖼️ Multi-Photo AI Studio"])

# --- Tab 1: Text-to-Image ---
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

# --- Tab 2: Multi-Photo AI Studio ---
with tab2:
    st.subheader("Upload Photos & Describe Design")
    st.caption("Upload 1-4 reference images. Use tags like **Image 1**, **Image 2** in your instruction to guide the AI.")
    
    uploaded_files = st.file_uploader(
        "Upload Reference Photos (1-4 images)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        raw_images = [Image.open(f).convert("RGBA") for f in uploaded_files[:4]]
        
        st.write("📸 **Uploaded Reference Images with IDs:**")
        cols = st.columns(len(raw_images))
        
        tagged_images = []
        for idx, img in enumerate(raw_images):
            tag_name = f"Image {idx+1}"
            with cols[idx]:
                st.image(img, caption=f"🏷️ {tag_name}", use_container_width=True)
            
            tagged_img = img.copy()
            draw = ImageDraw.Draw(tagged_img)
            draw.rectangle([(10, 10), (160, 50)], fill=(0, 0, 0, 180))
            draw.text((20, 15), tag_name, fill=(255, 255, 255, 255))
            tagged_images.append(tagged_img)

        edit_instruction = st.text_area(
            "Design Instruction (Use Image IDs freely)",
            placeholder="e.g., Take the aligner from Image 1 and place it onto the bathroom table in Image 2. Add the logo from Image 3 on top right corner.",
            height=100
        )

        if st.button("🚀 Process & Generate Visual", type="primary"):
            if not edit_instruction.strip():
                st.warning("Please enter your design instruction using the Image IDs.")
            else:
                try:
                    target_h = 400
                    resized_imgs = []
                    for img in tagged_images:
                        w_new = int(img.width * target_h / img.height)
                        resized_imgs.append(img.resize((w_new, target_h), Image.Resampling.LANCZOS))
                    
                    total_w = sum(img.width for img in resized_imgs)
                    composite_img = Image.new("RGBA", (total_w, target_h), (255, 255, 255, 255))
                    
                    x_off = 0
                    for img in resized_imgs:
                        composite_img.paste(img, (x_off, 0), img)
                        x_off += img.width

                    full_instruction = f"Based on reference grid ({', '.join([f'Image {i+1}' for i in range(len(raw_images))])}): {edit_instruction}"
                    enhanced_edit_prompt = build_marketing_prompt(full_instruction, ad_style)
                    
                    st.write("**Optimized Instruction sent to AI:**")
                    st.code(enhanced_edit_prompt, language="text")

                    with st.spinner("AI is processing image references and generating visual..."):
                        client = ImageGenClient()
                        img_url = client.edit_ad_image(
                            pil_image=composite_img,
                            prompt=enhanced_edit_prompt,
                            size=img_size
                        )
                        st.image(img_url, caption="Final AI Designed Visual", use_container_width=True)
                        st.markdown(f"[📥 Download Full High-Res Image]({img_url})")

                except Exception as e:
                    st.error(f"Processing Error: {e}")
