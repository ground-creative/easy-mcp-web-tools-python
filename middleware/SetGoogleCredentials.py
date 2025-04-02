from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.utils.logger import logger
from core.utils.state import global_state


class SetGoogleCredentials(BaseHTTPMiddleware):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):

        if not global_state.get("middleware.CheckAccessMiddleware.has_access", False):
            # Proceed with the request
            response = await call_next(request)
            return response

        content_type = request.headers.get("content-type", "")
    
        if content_type == "application/json":
            data = await request.json()
            method = data.get("method", "")
            params = data.get("params", {})

            if (
                method == "tools/call"
                and "name" in params
                and params["name"] == "search_google_tool"
            ):

                google_api_key = request.headers.get("x-google-api-key")

                if not google_api_key:
                    logger.error("Google API key missing in request headers.")
                else:
                    global_state.set("google_api_key", google_api_key, True)

                google_cse_id = request.headers.get("x-google-csi-id")

                if not google_cse_id:
                    logger.error("Google CSI ID missing in request headers.")
                else:
                    global_state.set("google_cse_id", google_cse_id, True)

        # Proceed with the request
        response = await call_next(request)
        return response
