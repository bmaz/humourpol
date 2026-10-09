from datetime import datetime

import pytz
import streamlit as st

from data import parse_csv
from image import process_image
from sqlite import extract_values, get_db, save_value

st.set_page_config(layout="wide", page_title="Interface d'annotation")
# st.logo("Facebook.png", size="large")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# UI Layout
# data_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])
left_col, center_col, right_col = st.columns([1, 3, 1])
_, bcol1, bcol2, _ = st.sidebar.columns([1, 1, 1, 1])

conn = get_db()


def initialize_toggles():
    if f"visual_humor_{st.session_state.current_id}" not in st.session_state:
        st.session_state[f"visual_humor_{st.session_state.current_id}"] = False

    if f"textual_humor_{st.session_state.current_id}" not in st.session_state:
        st.session_state[f"textual_humor_{st.session_state.current_id}"] = False


if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if st.session_state.uploaded_file is None:
    uploaded_file = st.file_uploader("Sélectionner un fichier CSV", type=["csv"])

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.rerun()

else:
    if "db" not in st.session_state:
        st.session_state.db, st.session_state.current_id = parse_csv(
            st.session_state.uploaded_file
        )

    initialize_toggles()

    if bcol1.button("", icon=":material/arrow_back_ios:", shortcut="Up"):
        previous_id = st.session_state.db[st.session_state.current_id]["previous_id"]
        if previous_id is not None:
            st.session_state.current_id = previous_id
        initialize_toggles()

    if bcol2.button("", icon=":material/arrow_forward_ios:", shortcut="Down"):
        next_id = st.session_state.db[st.session_state.current_id]["next_id"]
        if next_id is not None:
            st.session_state.current_id = next_id
        initialize_toggles()

    record = st.session_state.db[st.session_state.current_id]

    b64_image = record["b64_image"]

    def content_type_selected():
        record["content_type"] = st.session_state[
            f"content_type_{st.session_state.current_id}"
        ]
        save_value(
            conn,
            st.session_state.current_id,
            record["team_member"],
            record["content_type"],
            record["text"],
        )
        # st.empty()

    def visual_humor_selected():
        record["visual_humor"] = st.session_state[
            f"visual_humor_{st.session_state.current_id}"
        ]
        # st.write("")

    def textual_humor_selected():
        record["textual_humor"] = st.session_state[
            f"textual_humor_{st.session_state.current_id}"
        ]
        # st.write("")

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
            st.write("L'image est-elle humoristique ?")
            visual_humor = st.toggle(
                "L'image est humoristique"
                if st.session_state[f"visual_humor_{st.session_state.current_id}"]
                else "L'image n'est pas humoristique",
                key=f"visual_humor_{st.session_state.current_id}",
                on_change=visual_humor_selected,
            )

            st.write("Le texte est-il humoristique ?")
            textual_humor = st.toggle(
                "Le texte est humoristique"
                if st.session_state[f"textual_humor_{st.session_state.current_id}"]
                else "Le texte n'est pas humoristique",
                key=f"textual_humor_{st.session_state.current_id}",
                on_change=textual_humor_selected,
            )

            content_type = st.pills(
                "Type de contenu",
                [
                    "Photo",
                    "Caricature",
                    "Mème",
                    "Infographie",
                    "Illustration",
                    "Montage photo",
                    "Capture d’écran d’un site d'information",
                    "Capture d’écran d’un sondage",
                    "Capture d’écran d'un tweet",
                    "Autre",
                    "Ne s'applique pas",
                ],
                selection_mode="single",
                key=f"content_type_{st.session_state.current_id}",
                on_change=content_type_selected,
            )

            if st.button("Sauvegarder la progression"):
                data = extract_values(conn, record["team_member"])
                st.download_button(
                    label="Export CSV",
                    data=data,
                    file_name=f"Annotation_{record['team_member']}_{datetime.now(tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%dT%H-%M-%S')}.csv",
                    mime="text/csv",
                    icon=":material/download:",
                )
