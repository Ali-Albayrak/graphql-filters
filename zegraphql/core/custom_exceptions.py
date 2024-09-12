from fastapi.exceptions import HTTPException
from starlette import status
from .logger import log

class TriggerException(HTTPException):
    """
    Custom exception class for triggering exceptions with additional properties.

    Attributes:
        status_code (int): The status code of the HTTP response.
        detail (str): A human-readable detail message about the exception.
        trigger_name (str): A name associated with the trigger.
        debug_details (str): Additional debug details for troubleshooting.
    """
    def __init__(self, status_code: int, detail: dict = {}):
        super().__init__(status_code=status_code, detail=detail)

class AuthorizationError(Exception):
    pass

