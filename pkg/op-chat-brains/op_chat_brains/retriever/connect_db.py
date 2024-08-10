import psycopg
from psycopg.rows import class_row
from psycopg import Connection, connect
from psycopg.rows import dict_row
from op_chat_brains.config import DATABASE_URL
from typing import List, Dict

def retrieve_data(query, classrow=None):
    conn = psycopg.connect(DATABASE_URL)
    with conn.cursor() as cur:
        if classrow:
            cur.row_factory = class_row(classrow)
        cur.execute(query)
        data = cur.fetchall()
    conn.close()

    return data


def update_data(query: str, data: List[Dict[str, str]]) -> bool:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.executemany(query, data)
        conn.commit()
    return True


def update_single_param(query: str, params: tuple) -> bool:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
    return True

UPSERT_SUMMARIES_QUERY = """
        INSERT INTO "RawSummary" ("url", "data", "lastGeneratedAt", "updatedAt")
        VALUES (%(url)s, %(data)s, %(lastGeneratedAt)s, NOW())
        ON CONFLICT ("url") DO UPDATE SET
            "data" = EXCLUDED."data",
            "lastGeneratedAt" = EXCLUDED."lastGeneratedAt",
            "updatedAt" = NOW()
    """

UPDATE_URLS_AS_SUMMARIZED = """
        UPDATE "RawForumPost"
        SET "needsSummarize" = FALSE
        WHERE "url" = ANY(%s)
    """