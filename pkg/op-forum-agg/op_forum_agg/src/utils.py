from forum_dl import ExtractorOptions, ForumDl, SessionOptions, WriterOptions, logging, extractors
from forum_dl.writers.common import Entry, Item, Board, Thread, Post, File, Writer
from forum_dl.extractors.common import Extractor
from forum_dl.version import __version__

from datetime import datetime, timezone
import sys

import httpx
import psycopg2
from psycopg2.extras import execute_values
from op_forum_agg.config import config

def fetch_info(url: str):
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()

def store_data_in_db(data, query):
    conn = psycopg2.connect(config["DATABASE_URL"])
    cur = conn.cursor()
    execute_values(cur, query, data)
    conn.commit()

    cur.close()
    conn.close()

class ReadWriter(Writer):
    def __init__(self, extractor: Extractor, options: WriterOptions):
        super().__init__(extractor, options)
        self.entries = []

    def write(self, url: str):
        self.read_metadata()

        base_node = self._extractor.node_from_url(url)

        if isinstance(base_node, Board):
            self.write_board(base_node)
        elif isinstance(base_node, Thread):
            self.write_thread(base_node)

        return self.get_entries()

    def read_metadata(self):
        pass  # TODO.

    def _write_board_object(self, board: Board):
        entry = self._make_entry(board)
        self.entries.append(self._serialize_entry(entry))

    def _write_thread_object(self, thread: Thread):
        entry = self._make_entry(thread)
        self.entries.append(self._serialize_entry(entry))

    def _write_post_object(self, thread: Thread, post: Post):
        entry = self._make_entry(post)
        self.entries.append(self._serialize_entry(entry))

    def _write_file_object(self, file: File):
        entry = self._make_entry(file)
        self.entries.append(self._serialize_entry(entry))

    def _make_entry(self, item: Item):
        match item:
            case Board():
                typ = "board"
            case Thread():
                typ = "thread"
            case Post():
                typ = "post"
            case File():
                typ = "file"
            case Item():
                raise ValueError

        return Entry(
            generator="forum-dl",
            version=__version__,
            extractor=self._extractor.__class__.__module__.split(".")[-1],
            download_time=datetime.now(timezone.utc).isoformat(),
            type=typ,
            item=item,
        )
    
    def _serialize_entry(self, entry: Entry) -> str:
        return entry.json()

    def get_entries(self):
        return self.entries
