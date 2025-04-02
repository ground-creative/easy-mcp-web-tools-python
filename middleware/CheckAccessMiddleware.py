import os, json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.utils.logger import logger
from core.utils.state import global_state
from core.utils.config import config
from core.utils.env import EnvConfig


class CheckAccessMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, check_access_func, *args, **kwargs):
        super().__init__(app)
        self.check_access_func = check_access_func
        logger.info(
            f"Successfully loaded the function {check_access_func} for access key validation."
        )
      
    async def dispatch(self, request: Request, call_next):

        global_state.set("middleware.CheckAccessMiddleware.has_access", False, True)
        global_state.set("middleware.CheckAccessMiddleware.error_message", "", True)
        api_key = request.headers.get("x-access-key")

        # Log headers for debugging
        logger.debug("Request Headers: %s", request.headers)

        # Check if API key is present and valid
        if not api_key:
            logger.error("x-access-key missing in request headers.")
            global_state.set("middleware.CheckAccessMiddleware.has_access", False, True)
            global_state.set("middleware.CheckAccessMiddleware.error_message", "Invalid or missing x-access-key in request header, user has no access to this resource.", True)
            # Proceed with the request
            response = await call_next(request)
            return response

        # Verify if the provided API key exists in the valid keys list
        if not self.check_access_func()(api_key):
            logger.error("Invalid access key provided")
            global_state.set("middleware.CheckAccessMiddleware.has_access", False, True)
            global_state.set("middleware.CheckAccessMiddleware.error_message", "Invalid or missing x-access-key in request header, user has no access to this resource.", True)
            # Proceed with the request
            response = await call_next(request)
            return response

        global_state.set("middleware.CheckAccessMiddleware.has_access", True, True)
        global_state.set("middleware.CheckAccessMiddleware.api_key", api_key, True)
        logger.info("CheckAccessMiddleware Access granted")

        # Log the raw body in debug mode
        if EnvConfig.get("LOG_LEVEL", "INFO") == "DEBUG":
            body = await request.body()
            logger.debug("Raw Request Body: %s", body.decode())

        # Proceed with the request
        response = await call_next(request)
        return response

def check_access(api_key):
    """Load valid API keys from a JSON file."""
    valid_keys = []
    try:
        with open(config.get("ACCESS_KEYS_FILE_PATH"), "r") as f:
            valid_keys = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load access keys: %s", e)
        return False
    
    if api_key not in valid_keys:
        logger.debug(f"Invalid access key: {api_key}")
        return False
    
    return True

def is_authenticated(returnJsonOnError=False):

    if not global_state.get("middleware.CheckAccessMiddleware.has_access"):
        logger.error("User is not authenticated.")

        if returnJsonOnError:
            return json.dumps(
                {
                    "status": "error",
                    "error": global_state.get(
                        "error_message", "User is not authenticated."
                    ),
                }
            )

        return "User is not authenticated."

    return None  # Return None if authenticated
