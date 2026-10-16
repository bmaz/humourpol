import csv
import sqlite3
from io import StringIO

import streamlit as st


@st.cache_resource
def get_db():
    conn = sqlite3.connect("annotations.db", check_same_thread=False)

    # conn.execute("DROP TABLE annotations")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS annotations (
        id INTEGER,
        user TEXT,
        text TEXT,
        content_type TEXT,
        humor TEXT,
        ai TEXT,
        rank INTEGER,
        PRIMARY KEY (id, user)
    )
    """)

    conn.commit()
    return conn


def save_value(conn, id, user, rank, key, value):
    conn.execute(
        f"""
    INSERT INTO annotations (id, user, rank, {key})
    VALUES (?, ?, ?, ?)
    ON CONFLICT(id, user) DO UPDATE SET
        {key} = excluded.{key}
    """,
        (
            id,
            user,
            rank,
            value,
        ),
    )

    conn.commit()


def fetch_annotations(conn, id, user):

    cursor = conn.execute(
        """
    SELECT content_type, humor, ai
    FROM annotations
    WHERE (id, user) = (?, ?)
        """,
        (id, user),
    )
    return cursor.fetchone()


def extract_values(_conn, user):

    cursor = _conn.execute(
        """
    SELECT id, rank, content_type, humor, ai, user, text
    FROM annotations
    WHERE user = ?
    """,
        (user,),
    )

    buffer = StringIO()

    writer = csv.writer(buffer)
    writer.writerow(
        ["id", "index", "content_type", "humor", "ai_generated", "team_member", "text"]
    )
    for elements in cursor.fetchall():
        writer.writerow(elements)

    return buffer.getvalue()
