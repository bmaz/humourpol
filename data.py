from datetime import datetime
from io import StringIO

import casanova
import streamlit as st


@st.cache_data
def parse_csv(data_file):
    """Parse csv with caching to avoid redundant processing"""
    reader = casanova.reader(StringIO(data_file.getvalue().decode("utf-8")))
    db = {}

    account_pos = reader.headers["post_owner.name"]
    date_pos = reader.headers.creation_time
    id_pos = reader.headers.id
    text_pos = reader.headers.text
    mimetype_pos = reader.headers.mimetype
    image_pos = reader.headers.full_path

    previous_id = None
    first_id = None

    for row in reader:
        int_id = int(row[id_pos])
        db[int_id] = {
            "account": row[account_pos],
            "date": datetime.strptime(row[date_pos], "%Y-%m-%dT%H:%M:%S%z").strftime(
                "%A %d %B %Y"
            ),
            "text": row[text_pos],
            "previous_id": previous_id,
            "next_id": None,
            "image": row[image_pos] if "image" in row[mimetype_pos] else None,
        }

        if previous_id:
            db[previous_id]["next_id"] = int_id
        else:
            first_id = int_id
        previous_id = int_id

    return db, first_id
