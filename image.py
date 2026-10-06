import os
import traceback
from io import BytesIO

import streamlit as st
from PIL import Image

# Max dimensions for processing
MAX_IMAGE_SIZE = 2000  # pixels


# Resize image while maintaining aspect ratio
def resize_image(image, max_size=MAX_IMAGE_SIZE):
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image

    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))

    return image.resize((new_width, new_height), Image.LANCZOS)


@st.cache_data
def load_image(image_bytes):
    """Process image with caching to avoid redundant processing"""
    try:
        image = Image.open(BytesIO(image_bytes))
        resized = resize_image(image)
        return resized
    except Exception as e:
        st.error(f"Error processing image: {e!s}")
        return None


def process_image(image_path):
    try:
        if not os.path.exists(image_path):
            st.error(f"Image not found at path: {image_path}")
            return
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Process image (using cache if available)
        image = load_image(image_bytes)

        return image

        # Prepare download button
        # st.sidebar.markdown("\n")
        # st.sidebar.download_button(
        #     "Download fixed image", convert_image(fixed), "fixed.png", "image/png"
        # )

    except Exception as e:
        st.error(f"An error occurred: {e!s}")
        print(f"Error in fix_image: {traceback.format_exc()}")
