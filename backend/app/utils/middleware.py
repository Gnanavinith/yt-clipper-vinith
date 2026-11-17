import time
import sqlite3
from fastapi import Request
from app.utils.logger import get_logger, job_id_var

logger = get_logger("http")

async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - status={response.status_code} - duration={duration:.3f}s")
    return response
