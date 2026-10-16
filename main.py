import locale
from datetime import datetime

import pytz
import streamlit as st

from data import parse_csv
from form import humor_categories, image_type_categories
from image import process_image
from sqlite import (
    extract_values,
    fetch_annotations,
    fetch_record,
    get_db,
    save_single_field,
)

locale.setlocale(locale.LC_TIME, "fr_FR")

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
    if "current_id" not in st.session_state:
        (
            st.session_state.current_id,
            st.session_state.user,
            st.session_state.round,
            st.session_state.total,
        ) = parse_csv(st.session_state.uploaded_file, conn)

    record = fetch_record(conn, st.session_state.current_id, st.session_state.user)

    with st.bottom:
        progressbar = st.progress(record["rank"] / st.session_state.total)

    if (
        bcol1.button("", icon=":material/arrow_back_ios:", shortcut="Up")
        and record["previous_id"] is not None
    ):
        st.session_state.current_id = record["previous_id"]
        record = fetch_record(conn, st.session_state.current_id, st.session_state.user)

    if (
        bcol2.button("", icon=":material/arrow_forward_ios:", shortcut="Down")
        and record["next_id"] is not None
    ):
        st.session_state.current_id = record["next_id"]
        record = fetch_record(conn, st.session_state.current_id, st.session_state.user)

    progressbar.progress(
        record["rank"] / st.session_state.total,
        text=f"{record['rank']}/{st.session_state.total}",
    )

    b64_image = record["b64_image"]

    def image_type_selected():
        record["image_type"] = st.session_state[
            f"image_type_{st.session_state.current_id}"
        ]
        save_single_field(
            conn,
            st.session_state.current_id,
            st.session_state.user,
            "image_type",
            record["image_type"],
        )

    def humor_selected():
        record["humor"] = st.session_state[f"humor_{st.session_state.current_id}"]
        save_single_field(
            conn,
            st.session_state.current_id,
            st.session_state.user,
            "humor",
            record["humor"],
        )

    def ai_selected():
        record["generated_by_ai"] = st.session_state[
            f"ai_{st.session_state.current_id}"
        ]
        save_single_field(
            conn,
            st.session_state.current_id,
            st.session_state.user,
            "ai",
            st.session_state[f"ai_{st.session_state.current_id}"],
        )

    with center_col:
        if b64_image:
            image = process_image(b64_image)
            if image:
                st.image(image)

    st.sidebar.write(f"**{record['account']}**")
    st.sidebar.caption(
        datetime.strptime(record["date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%A %d %B %Y")
    )
    st.sidebar.write(record["text"])

    with right_col:
        margin, col_with_margin = st.columns([1, 9])
        with col_with_margin:
            annotations = fetch_annotations(
                conn, st.session_state.current_id, st.session_state.user
            )

            if annotations:
                image_type, humor, ai = annotations
            else:
                image_type, humor, ai = None, "Non", "Non"

            st.pills(
                "Présence de contenus humoristiques",
                humor_categories,
                selection_mode="single",
                key=f"humor_{st.session_state.current_id}",
                default=humor if humor else "Non",
                on_change=humor_selected,
            )

            st.pills(
                "Image générée par IA",
                ["Non", "Oui", "Ne sait pas"],
                selection_mode="single",
                key=f"ai_{st.session_state.current_id}",
                default=ai if ai else "Non",
                on_change=ai_selected,
            )

            try:
                st.pills(
                    "Type de contenu",
                    image_type_categories,
                    selection_mode="single",
                    key=f"image_type_{st.session_state.current_id}",
                    default=image_type,
                    on_change=image_type_selected,
                )
            except st.errors.StreamlitAPIException:
                st.pills(
                    "Type de contenu",
                    image_type_categories,
                    selection_mode="single",
                    key=f"image_type_{st.session_state.current_id}",
                    on_change=image_type_selected,
                )

            if st.button("Sauvegarde", icon=":material/backup:"):
                data = extract_values(
                    conn, st.session_state.user, st.session_state.round
                )
                st.download_button(
                    label="Export CSV",
                    data=data,
                    file_name=f"Annotation_{st.session_state.user}_round_{st.session_state.round}_{datetime.now(tz=pytz.timezone('America/Toronto')).strftime('%Y-%m-%dT%H-%M-%S')}.csv",
                    mime="text/csv",
                    icon=":material/download:",
                )
