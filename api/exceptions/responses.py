import typing

from fastapi.exceptions import HTTPException as FastapiHTTPException
from starlette.responses import JSONResponse


class ErrorResponse(JSONResponse):
    def render(self, content: typing.Any) -> bytes:
        if not isinstance(content, dict):
            if isinstance(content, bytes):
                content = {"error": str(content)}
            else:
                content = {"error": content}
        return super().render(content)


class HTTPException(FastapiHTTPException):
    def __init__(self, url, response='', message='', status=400):
        super().__init__(status_code=status,
                         detail={
                             "url": url,
                             "response": response,
                             "message": message,
                             "status": status
                         })
