import csv
import sqlite3
from io import StringIO

import streamlit as st


@st.cache_resource
def get_db():
    conn = sqlite3.connect("annotations.db", check_same_thread=False)

    conn.execute("DROP TABLE annotations")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS annotations (
        id INTEGER,
        previous_id INTEGER,
        next_id INTEGER,
        team_member TEXT,
        round INTEGER,
        text TEXT,
        image TEXT,
        mimetype TEXT,
        date TEXT,
        account TEXT,
        rank INTEGER,
        image_type TEXT,
        humor TEXT,
        ai TEXT,
        PRIMARY KEY (id, team_member)
    )
    """)

    conn.commit()
    return conn


def save_metadata(
    conn,
    id,
    previous_id,
    team_member,
    round,
    text,
    image,
    mimetype,
    date,
    account,
    rank,
    image_type,
    ai,
    humor,
):
    conn.execute(
        """
    INSERT INTO annotations (id, previous_id, team_member, round, text, image, mimetype, date, account, rank, image_type, ai, humor)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING
    """,
        (
            id,
            previous_id,
            team_member,
            round,
            text,
            image,
            mimetype,
            date,
            account,
            rank,
            image_type,
            ai,
            humor,
        ),
    )

    conn.commit()


def save_single_field(conn, id, team_member, key, value):
    conn.execute(
        f"""
    INSERT INTO annotations (id, team_member, {key})
    VALUES (?, ?, ?)
    ON CONFLICT(id, team_member) DO UPDATE SET
        {key} = excluded.{key}
    """,
        (id, team_member, value),
    )

    conn.commit()


def fetch_annotations(conn, id, team_member):

    cursor = conn.execute(
        """
    SELECT image_type, humor, ai
    FROM annotations
    WHERE (id, team_member) = (?, ?)
        """,
        (id, team_member),
    )
    return cursor.fetchone()


def fetch_record(conn, id, team_member):
    cursor = conn.execute(
        """
    SELECT previous_id, next_id, text, image, date, account, rank
    FROM annotations
    WHERE (id, team_member) = (?, ?)
        """,
        (id, team_member),
    )
    previous_id, next_id, text, image, date, account, rank = cursor.fetchone()
    return {
        "previous_id": previous_id,
        "next_id": next_id,
        "b64_image": image,
        "text": text,
        "date": date,
        "account": account,
        "rank": rank,
    }


def extract_values(_conn, team_member, round):

    cursor = _conn.execute(
        """
    SELECT id, rank, image_type, humor, ai, team_member, round, account, date, text, mimetype, image
    FROM annotations
    WHERE (team_member, round) = (?, ?)
    """,
        (team_member, round),
    )

    buffer = StringIO()

    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "index",
            "image_type",
            "humor",
            "ai_generated",
            "team_member",
            "round",
            "post_owner.name",
            "creation_time",
            "text",
            "mimetype",
            "b64_image",
        ]
    )
    for elements in cursor.fetchall():
        writer.writerow(elements)

    return buffer.getvalue()
