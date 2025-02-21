

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from jwt.exceptions import PyJWTError
from typing import Union, Any
import traceback
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Any = None,
        code: str = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details
        self.code = code
        super().__init__(message)

class ErrorHandler:
    async def __call__(
        self,
        request: Request,
        call_next
    ) -> Union[JSONResponse, Any]:
        try:
            return await call_next(request)
        except APIError as e:
            return self._handle_api_error(e)
        except SQLAlchemyError as e:
            return self._handle_database_error(e)
        except RedisError as e:
            return self._handle_cache_error(e)
        except PyJWTError as e:
            return self._handle_auth_error(e)
        except Exception as e:
            return self._handle_unknown_error(e)

    def _handle_api_error(self, error: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={
                "success": False,
                "error": error.message,
                "code": error.code,
                "details": error.details
            }
        )

    def _handle_database_error(self, error: SQLAlchemyError) -> JSONResponse:
        logger.error(f"Database error: {str(error)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": "Database error occurred",
                "code": "DATABASE_ERROR"
            }
        )

    def _handle_cache_error(self, error: RedisError) -> JSONResponse:
        logger.error(f"Cache error: {str(error)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": "Cache service error occurred",
                "code": "CACHE_ERROR"
            }
        )

    def _handle_auth_error(self, error: PyJWTError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error": "Authentication failed",
                "code": "AUTH_ERROR"
            }
        )

    def _handle_unknown_error(self, error: Exception) -> JSONResponse:
        logger.error(f"Unknown error: {str(error)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

