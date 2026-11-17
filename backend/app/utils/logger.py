import logging
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from pathlib import Path
from app.config import STORAGE_DIR

LOGS_DIR = STORAGE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "app.log"

job_id_var: ContextVar[str] = ContextVar("job_id", default="-")

class JobIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        current_job_id = job_id_var.get()
        extra = kwargs.get("extra", {})
        extra["job_id"] = current_job_id
        kwargs["extra"] = extra
        return msg, kwargs

class JobIdFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "job_id"):
            record.job_id = job_id_var.get()
        return super().format(record)

def get_logger(name: str) -> JobIdAdapter:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        formatter = JobIdFormatter("%(asctime)s | %(levelname)s | %(name)s | job=%(job_id)s | %(message)s")

        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return JobIdAdapter(logger, {})
