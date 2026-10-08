import base64
import traceback
from io import BytesIO

import streamlit as st
from PIL import Image


@st.cache_data
def process_image(b64_image):
    try:
        buff = BytesIO(base64.b64decode(b64_image))
        image = Image.open(buff)

        return image

        # Prepare download button
        # st.sidebar.markdown("\n")
        # st.sidebar.download_button(
        #     "Download fixed image", convert_image(fixed), "fixed.png", "image/png"
        # )

    except Exception as e:
        st.error(f"An error occurred: {e!s}")
        print(f"Error in fix_image: {traceback.format_exc()}")
