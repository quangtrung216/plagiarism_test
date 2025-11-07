from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging
import time

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url}")

        # Process request
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.4f}s")

        return response
