import psycopg
from psycopg.rows import class_row
from op_forum_agg.config import config


def retrieve_data(query, classrow=None):
    conn = psycopg.connect(config["DATABASE_URL"])
    with conn.cursor() as cur:
        if classrow:
            cur.row_factory = class_row(classrow)
        cur.execute(query)
        data = cur.fetchall()
    conn.close()

    return data
