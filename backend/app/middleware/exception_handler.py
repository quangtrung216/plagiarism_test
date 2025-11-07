from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException
from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback
import logging

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            logger.warning(f"HTTP Exception: {e.status_code} - {e.detail}")
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception as e:
            logger.error(f"Unhandled Exception: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )
