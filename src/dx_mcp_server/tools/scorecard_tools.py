from os import environ
import requests

from dx_mcp_server.server import mcp

DX_API_HOST = environ.get("DX_API_HOST", "https://api.getdx.com")
WEB_API_TOKEN = environ.get("WEB_API_TOKEN", "")


@mcp.tool()
def listInitiatives(
    cursor: str = None,
    limit: int = 20,
    published: bool = None,
    priority: int = None,
    tags: str = None,
) -> dict:
    """
    Lists all initiatives with summary information.

    Args:
        cursor (str, optional): Cursor for pagination. Get from response_metadata.next_cursor in prior requests.
        limit (int, optional): Limit the number of initiatives per page. Maximum 100, defaults to 50.
        published (bool, optional): Filter by published status.
        priority (int, optional): Filter by priority (0-2, lower numbers are more urgent).
        tags (str, optional): Comma-separated tags to filter by.
    """
    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    params = {}
    if cursor:
        params["cursor"] = cursor
    if limit is not None:
        params["limit"] = limit
    if published is not None:
        params["published"] = str(published).lower()
    if priority is not None:
        params["priority"] = priority
    if tags:
        params["tags"] = tags

    url = f"{DX_API_HOST}/initiatives.list"
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

        initiatives = data.get("initiatives", [])
        return {
            "initiatives": initiatives,
            "next_cursor": data.get("response_metadata", {}).get("next_cursor", None),
        }
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool()
def getInitiativeDetails(
    id: str,
    entity_type_identifiers: str = None,
    limit: int = 20,
    cursor: str = None,
) -> dict:
    """
    Get initiative details including both the initiative info and its progress report.

    Note: This calls two endpoints:
    - initiatives.info
    - initiatives.progressReport

    Args:
        id (str): Initiative public ID.
        entity_type_identifiers (str, optional): Passed through to initiatives.progressReport.
        limit (int, optional): Passed through to initiatives.progressReport. Maximum 100, defaults to 50.
        cursor (str, optional): Passed through to initiatives.progressReport.
    """
    if not id:
        return {"error": "id is required"}

    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }

    result = {}

    # Get initiative info
    info_url = f"{DX_API_HOST}/initiatives.info"
    info_params = {"id": id}
    try:
        info_response = requests.get(info_url, params=info_params, headers=headers)
        info_response.raise_for_status()
        info_data = info_response.json()

        if not info_data.get("ok"):
            result["initiative_error"] = info_data.get("error", "Unknown error")
        else:
            result["initiative"] = info_data.get("initiative")
    except requests.RequestException as e:
        result["initiative_error"] = str(e)

    # Get progress report
    progress_url = f"{DX_API_HOST}/initiatives.progressReport"
    progress_params = {"id": id}
    if entity_type_identifiers:
        progress_params["entity_type_identifiers"] = entity_type_identifiers
    if limit is not None:
        progress_params["limit"] = limit
    if cursor:
        progress_params["cursor"] = cursor

    try:
        progress_response = requests.get(
            progress_url, params=progress_params, headers=headers
        )
        progress_response.raise_for_status()
        progress_data = progress_response.json()

        if not progress_data.get("ok"):
            result["progress_error"] = progress_data.get("error", "Unknown error")
        else:
            result["entities"] = progress_data.get("entities", [])
            result["next_cursor"] = progress_data.get("response_metadata", {}).get(
                "next_cursor", None
            )
    except requests.RequestException as e:
        result["progress_error"] = str(e)

    if not result:
        return {"error": "Request failed"}

    return result


@mcp.tool()
def listScorecards(cursor: str = None, limit: int = 20) -> dict:
    """
    List all active scorecards.
    Args:
        cursor (str, optional): Cursor for pagination. Get from response_metadata.next_cursor in prior requests.
        limit (int, optional): Limit the number of scorecards per page. Must be between 1 and 50.
    """
    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    params = {}
    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    url = f"{DX_API_HOST}/scorecards.list"
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

        scorecards = data.get("scorecards", [])

        return {
            "scorecards": scorecards,
            "next_cursor": data.get("response_metadata", {}).get("next_cursor", None),
        }
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool()
def getScorecardInfo(id: str) -> dict:
    """
    Retrieve details about a specific scorecard, including its defined levels and checks.
    Args:
        id (str): The unique ID of the scorecard.
    """
    if not id:
        return {"error": "id is required"}

    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    url = f"{DX_API_HOST}/scorecards.info"
    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }
    params = {"id": id}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            return {"error": f"API error: {error}"}

        return {"scorecard": data.get("scorecard")}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool()
def reviewTasks(
    entity_identifier: str,
    check_ids: str,
) -> str:
    """
    Review/resolve/complete outstanding DX tasks (failing checks).

    Args:
        entity_identifier (str): Entity identifier.
        check_ids (str): Comma-separated list of check IDs to focus on.
    """
    return f"""You are a DX task resolver. Your job is to find, understand, and resolve failing DX scorecard checks/tasks efficiently and safely.

### High-level rules
- Prefer using DX MCP tools to fetch ground truth before guessing.
- Ask at most 1-2 clarifying questions *only* if you are blocked; otherwise proceed with reasonable defaults and state your assumptions.
- If there is exactly **one** check and the fix is **small + safe** (fits in a single PR / minimal change), proceed to execute the fix. Otherwise, output a detailed plan.
- If you cannot fully resolve with available tools/code changes, explain what's missing and propose the next best actions.

### Step 1 — Identify the entity
- Call tool getEntityDetails(identifier={entity_identifier}).
- Determine the target checks from the provided check ids: {check_ids}.

### Step 2 — For each target check, build a compact "case file"
For each check/task, extract and write:
- Check/task id + name
- Current status (failing/blocked/etc.)
- Latest result payloads / error messages (quote the key parts)
- What you believe the check is asserting (in one sentence)
- What evidence supports that (link back to the payload/definition)

### Step 3 — Decide: execute vs plan vs blocked
- **Execute now** when:
  - Exactly one check is in scope, and
  - The resolution is straightforward, low-risk, and locally verifiable (code/config/doc change that fits in one PR).
- **Plan** when:
  - Multiple checks are in scope, or
  - The fix is non-trivial / risky / needs coordination.
- **Blocked** when:
  - Missing access/data/ownership, or
  - Requirements are unclear even after pulling scorecard + task details.

### Output format (strict)
Start with:
- Entity: <identifier>
- Checks in scope: <ids>
- Decision: EXECUTE | PLAN | BLOCKED

Then:
- If **EXECUTE**:
  - What you will change (1-3 bullets)
  - Execute the changes (edit code / run available actions)
- If **PLAN**:
  - A step-by-step plan with clear ordering, expected files/areas to touch, and verification for each step
  - Call out dependencies/risks and where human input is needed
- If **BLOCKED**:
  - What's missing
  - The smallest next step to unblock
  - Who/what to consult (team/initiative/owner), using listTeams/getTeamDetails if helpful
"""
