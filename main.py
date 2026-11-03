import io
import base64
import requests
import streamlit as st
from PIL import Image

def render_download_and_export_section(img_source):
    """
    Helper function to render multiformat downloads and quick editor options.
    Supports HTTP URLs, Base64 data strings, and PIL Image objects.
    """
    st.markdown("---")
    st.subheader("📥 Export Options & Next Steps")
    
    # Process image source safely
    try:
        if isinstance(img_source, str):
            if img_source.startswith("data:image"):
                # Handle Base64 encoded image string
                base64_data = img_source.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                pil_img = Image.open(io.BytesIO(image_bytes))
            elif img_source.startswith("http"):
                # Handle standard HTTP URL
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
