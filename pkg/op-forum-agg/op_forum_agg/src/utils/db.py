import psycopg
from psycopg.rows import class_row

from op_forum_agg.config import config

if config["DATABASE_URL"] is None:
    raise ValueError("DATABASE_URL is not set in the environment")


def store_data_in_db(data, query):
    conn = psycopg.connect(config["DATABASE_URL"])
    with conn.cursor() as cur:
        cur.executemany(query, data)
    conn.commit()
    conn.close()


def retrieve_data_from_db(query, classrow=None):
    conn = psycopg.connect(config["DATABASE_URL"])
    with conn.cursor() as cur:
        if classrow:
            cur.row_factory = class_row(classrow)
        cur.execute(query)
        data = cur.fetchall()
    conn.close()

    return data


def filter_data_from_db(query, data, classrow=None):
    conn = psycopg.connect(config["DATABASE_URL"])
    with conn.cursor() as cur:
        if classrow:
            cur.row_factory = class_row(classrow)
        cur.execute(query, data)
        result = cur.fetchall()
    conn.close()

    return result
