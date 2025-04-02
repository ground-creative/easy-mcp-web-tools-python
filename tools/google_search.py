from core.utils.logger import logger
import requests
from core.utils.state import global_state
from pydantic import Field
from typing import Annotated, Dict
from app.middleware.CheckAccessMiddleware import is_authenticated
import json

SERVICE_URL = "https://www.googleapis.com/customsearch/v1"

def search_google_tool(
    query: Annotated[
        str,
        Field(
            description="Required, the search query. Convert the query into a concise 3-4 word Google search term. Ex: 'Hotels in New York'"
        ),
    ],
    num: Annotated[
        int,
        Field(
            default=10,
            description="Required, number of results to fetch (max 10 per request). Default is 10. If more results are required, perform multiple searches incrementing the `start` parameter by 10 for each.",
        ),
    ] = 10,
    start: Annotated[
        int,
        Field(
            default=1,
            description="Required, the starting index for retrieving results, typically increments by 10.",
        ),
    ] = 1,
    filter: Annotated[
        str,
        Field(
            default=None,
            description="Optional, a site filter, e.g., 'example.com'. Use to restrict results to a specific site.",
        ),
    ] = None,
) -> Dict:
    """
    Use this tool to search on Google using Custom Search API and returns status code and either search results or error string.
    The `num` parameter cannot be more than 10. If more results are required, perform multiple searches incrementing the `start` value by 10 for each.

    Request Body Parameters:
    - query (str): Required, this is the search query. Convert the query into a concise 3-4 word Google search term. Ex: "Hotels in New York"
    - num (int): Required, number of results to fetch (max 10 per request).
    - start (int): Required, the starting index for retrieving results, typically increments by 10.
    - filter (str): Optional, site filter (e.g., "example.com").

    Example Request Payload:
    {
        "query": "Hotels in New York",
        "num": 10,   # get 10 results
        "start": 1    # Get results from first page
    }

    Example Response (200 OK):
    {
        "data": {
            "results": [
                {
                    "title": "Example Title",
                    "link": "https://example.com",
                    "snippet": "Example snippet text."
                }
            ],
            "total_results": 1
        }
    }
    """
    logger.info(
        f"Starting google search with query `{query}` num `{num}` start `{start}`"
    )

    auth_response = is_authenticated(True)
    if auth_response:
        return auth_response

    params = {
        "q": query,
        "key": global_state.get("google_api_key"),
        "cx": global_state.get("google_cse_id"),
        "num": num,
        "start": start,
    }

    try:
        response = requests.get(SERVICE_URL, params=params)

        print("AAAAAAAAAAAAAAA")
        print(response)

        # If the request is successful (status code 200)
        if response.status_code == 200:
            results = response.json()

            if "items" in results:
                search_results = [
                    {
                        "title": item["title"],
                        "link": item["link"],
                        "snippet": item["snippet"],
                    }
                    for item in results["items"]
                ]

                # Apply site filter if provided
                if filter:
                    search_results = [
                        result for result in search_results if filter in result["link"]
                    ]

                return json.dumps({
                    "status_code": response.status_code,
                    "data": {
                        "results": search_results,
                        "total_results": len(search_results)
                    }
                })

            # If no items are found, return an empty list
            return json.dumps({
                "status_code": response.status_code,
                "data": {
                    "results": [],
                    "total_results": 0
                }
            })

        # If the request fails, return the error string with the status code
        return json.dumps({
            "status_code": response.status_code,
            "error": f"Search request failed: {response.text}"
        })

    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error with google search query `{query}` num `{num}` start `{start}`: {str(e)}"
        )
        # Handle any request exceptions
        return json.dumps({
            "status_code": 500,
            "error": f"Search request failed: {str(e)}"
        })