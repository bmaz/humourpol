from datetime import datetime

import pytz
import streamlit as st

from data import parse_csv
from form import content_type_categories, humor_categories
from image import process_image
from sqlite import extract_values, fetch_annotations, get_db, save_value

st.set_page_config(layout="wide", page_title="Interface d'annotation")
# st.logo("Facebook.png", size="large")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# UI Layout
# data_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])
left_col, center_col, right_col = st.columns([2, 5, 2])
_, bcol1, bcol2, _ = st.sidebar.columns([1, 1, 1, 1])

conn = get_db()


if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if st.session_state.uploaded_file is None:
    uploaded_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.rerun()

else:
    if "db" not in st.session_state:
        st.session_state.db, st.session_state.current_id, st.session_state.total = (
            parse_csv(st.session_state.uploaded_file, conn)
        )

    with st.bottom:
        progressbar = st.progress(0)

    if bcol1.button("", icon=":material/arrow_back_ios:", shortcut="Up"):
        previous_id = st.session_state.db[st.session_state.current_id]["previous_id"]
        if previous_id is not None:
            st.session_state.current_id = previous_id

    if bcol2.button("", icon=":material/arrow_forward_ios:", shortcut="Down"):
        next_id = st.session_state.db[st.session_state.current_id]["next_id"]
        if next_id is not None:
            st.session_state.current_id = next_id

    record = st.session_state.db[st.session_state.current_id]

    progressbar.progress(
        record["progress"] / st.session_state.total,
        text=f"{record['progress']}/{st.session_state.total}",
    )

    b64_image = record["b64_image"]

    def content_type_selected():
        record["content_type"] = st.session_state[
            f"content_type_{st.session_state.current_id}"
        ]
        save_value(
            conn,
            st.session_state.current_id,
            record["team_member"],
            record["progress"],
            "content_type",
            record["content_type"],
        )

    def humor_selected():
        record["humor"] = st.session_state[f"humor_{st.session_state.current_id}"]
        save_value(
            conn,
            st.session_state.current_id,
            record["team_member"],
            record["progress"],
            "humor",
            record["humor"],
        )

    def radio_selected():
        record["generated_by_ai"] = st.session_state[
            f"IA_{st.session_state.current_id}"
        ]
        save_value(
            conn,
            st.session_state.current_id,
            record["team_member"],
            record["progress"],
            "ai",
            record["generated_by_ai"],
        )

    with center_col:
        if b64_image:
            image = process_image(b64_image)
            if image:
                st.image(image)

    st.sidebar.write(f"**{record['account']}**")
    st.sidebar.caption(record["date"])
    st.sidebar.write(record["text"])

    with right_col:
        margin, col_with_margin = st.columns([1, 9])
        with col_with_margin:
            annotations = fetch_annotations(
                conn, st.session_state.current_id, record["team_member"]
            )

            if annotations:
                content_type, humor, _ = annotations
            else:
                content_type, humor = None, "Non"

            st.pills(
                "Présence de contenus humoristiques",
                humor_categories,
                selection_mode="single",
                key=f"humor_{st.session_state.current_id}",
                default=humor if humor else "Non",
                on_change=humor_selected,
            )

            st.radio(
                "Image générée par IA",
                ["Non", "Oui", "Ne sait pas"],
                horizontal=True,
                key=f"IA_{st.session_state.current_id}",
                on_change=radio_selected,
            )

            try:
                st.pills(
                    "Type de contenu",
                    content_type_categories,
                    selection_mode="single",
                    key=f"content_type_{st.session_state.current_id}",
                    default=content_type,
                    on_change=content_type_selected,
                )
            except st.errors.StreamlitAPIException:
                st.pills(
                    "Type de contenu",
                    content_type_categories,
                    selection_mode="single",
                    key=f"content_type_{st.session_state.current_id}",
                    on_change=content_type_selected,
                )

            if st.button("Sauvegarde", icon=":material/backup:"):
                data = extract_values(conn, record["team_member"])
                st.download_button(
                    label="Export CSV",
                    data=data,
                    file_name=f"Annotation_{record['team_member']}_{datetime.now(tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%dT%H-%M-%S')}.csv",
                    mime="text/csv",
                    icon=":material/download:",
                )
