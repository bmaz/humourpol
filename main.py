import streamlit as st

from data import parse_csv
from image import process_image

st.set_page_config(layout="wide", page_title="Interface d'annotation")
# st.logo("Facebook.png", size="large")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# UI Layout
# data_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])
left_col, center_col, right_col = st.columns([1, 3, 1])
_, bcol1, bcol2, _ = st.sidebar.columns([1, 1, 1, 1])


# Process the CSV
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if st.session_state.uploaded_file is None:
    uploaded_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.rerun()

else:
    db, first_id = parse_csv(st.session_state.uploaded_file)
    if "current_id" not in st.session_state:
        st.session_state.current_id = first_id
    if bcol1.button("", icon=":material/arrow_back_ios:", shortcut="Left"):
        previous_id = db[st.session_state.current_id]["previous_id"]
        if previous_id is not None:
            st.session_state.current_id = previous_id
    if bcol2.button("", icon=":material/arrow_forward_ios:", shortcut="Right"):
        next_id = db[st.session_state.current_id]["next_id"]
        if next_id is not None:
            st.session_state.current_id = next_id

    with center_col:
        record = db[st.session_state.current_id]
        image_path = record["image"]
        if image_path:
            image = process_image(image_path)
            if image:
                st.image(image)
        st.sidebar.write(f"**{record['account']}**")
        st.sidebar.caption(record["date"])
        st.sidebar.write(record["text"])
