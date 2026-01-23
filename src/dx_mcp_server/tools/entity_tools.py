from os import environ
import requests

from dx_mcp_server.server import mcp

DX_API_HOST = environ.get("DX_API_HOST", "https://api.getdx.com")
WEB_API_TOKEN = environ.get("WEB_API_TOKEN", "")


@mcp.tool()
def listEntities(
    search_term: str = None,
    type: str = None,
    cursor: str = None,
    limit: int = 20,
) -> dict:
    """
    List entities from the DX software catalog.

    Args:
        search_term (str, optional): Search term to filter by.
        type (str, optional): Filter entities by type (e.g., 'service', 'team', etc.).
        cursor (str, optional): Cursor for pagination. Get from response_metadata.next_cursor in prior requests.
        limit (int, optional): Number of entities per page - if present, must be between 1 and 50.
    """
    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    params = {}
    if search_term:
        params["search_term"] = search_term
    if type:
        params["type"] = type
    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    url = f"{DX_API_HOST}/entities.list"
    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            return {"error": f"API error: {error}"}

        entities = data.get("entities", [])

        return {
            "entities": entities,
            "next_cursor": data.get("response_metadata", {}).get("next_cursor", None),
        }
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool()
def getEntityDetails(identifier: str) -> dict:
    """
    Get comprehensive details about a specific entity including its information, tasks, and scorecards - we can use this to check operational readiness/health of an entity.

    Args:
        identifier (str): The unique identifier for the entity (e.g., 'payment-processing').
    """
    if not identifier:
        return {"error": "identifier is required"}

    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }

    result = {}

    # Get entity info
    info_url = f"{DX_API_HOST}/entities.info"
    info_params = {"identifier": identifier}

    try:
        info_response = requests.get(info_url, params=info_params, headers=headers)
        info_response.raise_for_status()
        info_data = info_response.json()

        if not info_data.get("ok"):
            error = info_data.get("error", "Unknown error")
            result["entity_error"] = error
        else:
            result["entity"] = info_data.get("entity")
    except requests.RequestException as e:
        result["entity_error"] = str(e)

    # Get entity tasks
    tasks_url = f"{DX_API_HOST}/entities.tasks"
    tasks_params = {"identifier": identifier}
    try:
        tasks_response = requests.get(tasks_url, params=tasks_params, headers=headers)
        tasks_response.raise_for_status()
        tasks_data = tasks_response.json()
        if not tasks_data.get("ok"):
            error = tasks_data.get("error", "Unknown error")
            result["tasks_error"] = error
        else:
            result["tasks"] = tasks_data.get("tasks", [])
    except requests.RequestException as e:
        result["tasks_error"] = str(e)

    # Get entity scorecards
    scorecards_url = f"{DX_API_HOST}/entities.scorecards"
    scorecards_params = {"identifier": identifier}

    try:
        scorecards_response = requests.get(
            scorecards_url, params=scorecards_params, headers=headers
        )
        scorecards_response.raise_for_status()
        scorecards_data = scorecards_response.json()

        if not scorecards_data.get("ok"):
            error = scorecards_data.get("error", "Unknown error")
            result["scorecards_error"] = error
        else:
            result["scorecards"] = scorecards_data.get("scorecards", [])
    except requests.RequestException as e:
        result["scorecards_error"] = str(e)

    if not result:
        return {"error": f"Request failed: {str(e)}"}

    return result
