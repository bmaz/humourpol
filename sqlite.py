import csv
import sqlite3
from io import StringIO

import streamlit as st


@st.cache_resource
def get_db():
    conn = sqlite3.connect("annotations.db", check_same_thread=False)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS annotations (
        id INTEGER,
        user TEXT,
        content_type TEXT,
        PRIMARY KEY (id, user)
    )
    """)

    conn.commit()
    return conn


def save_value(conn, id, user, content_type):
    conn.execute(
        """
    INSERT INTO annotations (id, user, content_type)
    VALUES (?, ?, ?)
    ON CONFLICT(id, user) DO UPDATE SET
        content_type = excluded.content_type
    """,
        (
            id,
            user,
            content_type,
        ),
    )

    conn.commit()


@st.cache_data
def extract_values(_conn, user):

    cursor = _conn.execute(
        """
    SELECT id, content_type, user
    FROM annotations
    WHERE user = ?
    """,
        (user,),
    )

    buffer = StringIO()

    writer = csv.writer(buffer)
    writer.writerow(["id", "content_type", "team_member"])
    for post_id, content_type, userid in cursor.fetchall():
        writer.writerow([post_id, content_type, userid])

    return buffer.getvalue()
