import csv
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
from datetime import datetime


class StructuredLogger:
    def __init__(self, log_file: str = "logs.csv", app_log_file: str = "app.log"):
        self.log_file = log_file
        self.setup_file_logger(app_log_file)
        self.setup_csv_logger()

    def setup_file_logger(self, app_log_file: str):
        self.logger = logging.getLogger("OpChatBrainsLogger")
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def setup_csv_logger(self):
        self.csv_file = open(self.log_file, "a", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        if self.csv_file.tell() == 0:
            self.csv_writer.writerow(["timestamp", "question", "answer", "context"])

    def log_query(self, question: str, output: Dict[str, Any]):
        self.logger.info(f"Question: {question}")
        self.logger.info(f"Answer: {output['answer']}")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.csv_writer.writerow(
            [timestamp, question, output["answer"], output["context"]]
        )
        self.csv_file.flush()  # Ensure the data is written immediately

    def close(self):
        self.csv_file.close()
