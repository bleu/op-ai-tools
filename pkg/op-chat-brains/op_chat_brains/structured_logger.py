import csv
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
from datetime import datetime


class StructuredLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StructuredLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.logger = logging.getLogger("OpChatBrainsLogger")
        self.logger.setLevel(logging.INFO)

        # File handler for app.log
        file_handler = RotatingFileHandler(
            "app.log", maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # CSV handler for logs.csv
        self.csv_handler = CSVHandler("logs.csv")
        self.logger.addHandler(self.csv_handler)

    def log_query(self, question: str, output: Dict[str, Any]):
        self.logger.info(f"Question: {question}")
        self.logger.info(f"Answer: {output['answer']}")
        self.logger.info(
            "CSV_LOG",
            extra={
                "question": question,
                "answer": output["answer"],
                "context": output["context"],
            },
        )


class CSVHandler(logging.Handler):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.csv_file = open(self.filename, "a", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        if self.csv_file.tell() == 0:
            self.csv_writer.writerow(["timestamp", "question", "answer", "context"])

    def emit(self, record):
        if record.msg == "CSV_LOG":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.csv_writer.writerow(
                [
                    timestamp,
                    record.__dict__.get("question", ""),
                    record.__dict__.get("answer", ""),
                    record.__dict__.get("context", ""),
                ]
            )
            self.csv_file.flush()

    def close(self):
        self.csv_file.close()
        super().close()
