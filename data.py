import csv
import sys
from io import StringIO

import casanova

from sqlite import fetch_annotations, save_metadata, save_single_field

csv.field_size_limit(sys.maxsize)


def parse_csv(data_file, conn):
    """Parse csv and store data in db"""
    reader = casanova.reader(StringIO(data_file.getvalue().decode("utf-8")))

    account_pos = reader.headers["post_owner.name"]
    date_pos = reader.headers.creation_time
    id_pos = reader.headers.id
    text_pos = reader.headers.text
    mimetype_pos = reader.headers.mimetype
    b64_image_pos = reader.headers.b64_image
    team_member_pos = reader.headers.team_member
    round_pos = reader.headers.round
    if "image_type" in reader.headers:
        image_type_pos = reader.headers.image_type
        ai_pos = reader.headers.ai_generated
        humor_pos = reader.headers.humor

    previous_id = None
    first_id = None
    last_annotated = None

    for enum, row in enumerate(reader):
        int_id = int(row[id_pos])

        image = row[b64_image_pos] if "image" in row[mimetype_pos] else None
        if "image_type" in reader.headers:
            image_type = row[image_type_pos]
            ai = row[ai_pos]
            humor = row[humor_pos]
        else:
            image_type = None
            ai = None
            humor = None
        save_metadata(
            conn,
            int_id,
            previous_id,
            row[team_member_pos],
            row[round_pos],
            row[text_pos],
            image,
            row[mimetype_pos],
            row[date_pos],
            row[account_pos],
            enum + 1,
            image_type,
            ai,
            humor,
        )

        if previous_id:
            save_single_field(
                conn, previous_id, row[team_member_pos], "next_id", int_id
            )
        else:
            first_id = int_id
        previous_id = int_id

        annotations = fetch_annotations(conn, int_id, row[team_member_pos])
        if annotations and annotations[0]:
            last_annotated = int_id

    if last_annotated is None:
        return first_id, row[team_member_pos], row[round_pos], enum + 1

    del data_file, reader

    return last_annotated, row[team_member_pos], row[round_pos], enum + 1
