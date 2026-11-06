from os import environ
import requests

from dx_mcp_server.server import mcp

DX_API_HOST = environ.get("DX_API_HOST", "https://api.getdx.com")
WEB_API_TOKEN = environ.get("WEB_API_TOKEN", "")

# Score types supported by the snapshots.*Scores and snapshots.*.breakdown web API methods.
# Each maps to the API method prefix and the name of the item id param its breakdown expects.
SCORE_TYPES = {
    "driver": {"method": "driverScores", "item_param": "driver_id"},
    "workflow": {"method": "workflowScores", "item_param": "workflow_id"},
    "impact": {"method": "impactScores", "item_param": "impact_id"},
    "csat": {"method": "csatScores", "item_param": "csat_id"},
    "dxi": {"method": "dxiScores", "item_param": None},
    "allocation": {"method": "allocationPercentages", "item_param": "question_id"},
}

DIMENSION_TYPES = ["snapshotTeam", "group", "branch", "attribute"]


def _get(method: str, params: dict = None) -> dict:
    """GET a snapshots.* web API method and normalize errors into {"error": ...}."""
    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    url = f"{DX_API_HOST}/{method}"
    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }
    params = {k: v for k, v in (params or {}).items() if v not in (None, "")}

    try:
        response = requests.get(url, params=params, headers=headers)
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return {"error": "API returned a non-JSON response"}

        if not data.get("ok"):
            error = data.get("error", f"HTTP {response.status_code}")
            result = {"error": f"API error: {error}"}
            if data.get("details"):
                result["details"] = data["details"]
            return result

        return data
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def _filter_params(
    snapshot_id, team_ids, snapshot_team_ids, group_ids, attribute_ids, branch_ids
) -> dict:
    return {
        "snapshot_id": snapshot_id,
        "team_ids": team_ids,
        "snapshot_team_ids": snapshot_team_ids,
        "group_ids": group_ids,
        "attribute_ids": attribute_ids,
        "branch_ids": branch_ids,
    }


@mcp.tool()
def listSnapshots(ordering: str = None) -> dict:
    """
    List completed DX snapshots (developer experience surveys) with participation counts.
    Use this first to find a snapshot_id for the other snapshot tools.

    Args:
        ordering (str, optional): Sort newest first by "scheduled_for" or "completed_at".
            Omit for API default ordering.
    """
    if ordering and ordering not in ("scheduled_for", "completed_at"):
        return {"error": "ordering must be 'scheduled_for' or 'completed_at'"}

    data = _get("snapshots.list", {"ordering": ordering})
    if "error" in data:
        return data
    return {"snapshots": data.get("snapshots", [])}


@mcp.tool()
def listSnapshotBranches() -> dict:
    """
    List snapshot branches for the account. Branches are survey variants targeted at
    different audiences (e.g. engineering vs product management). Use the IDs as branch_ids
    filters in the snapshot score tools.
    """
    data = _get("snapshots.branches.list")
    if "error" in data:
        return data
    return {"branches": data.get("branches", [])}


@mcp.tool()
def listSnapshotTeams(snapshot_id: str) -> dict:
    """
    List the teams captured in a snapshot, with manager and parent/child hierarchy fields.
    Use the IDs as snapshot_team_ids filters or as parent_snapshot_team_id in breakdowns.

    Args:
        snapshot_id (str): Snapshot ID from listSnapshots.
    """
    if not snapshot_id:
        return {"error": "snapshot_id is required"}

    data = _get("snapshots.snapshotTeams.list", {"snapshot_id": snapshot_id})
    if "error" in data:
        return data
    return {"snapshot_teams": data.get("snapshot_teams", [])}


@mcp.tool()
def getSnapshotScores(
    snapshot_id: str,
    score_type: str,
    team_ids: str = None,
    snapshot_team_ids: str = None,
    group_ids: str = None,
    attribute_ids: str = None,
    branch_ids: str = None,
) -> dict:
    """
    Get aggregate snapshot results for one score type, optionally filtered to a cohort of
    respondents. Returns one result per item (driver, workflow, impact, CSAT tool, allocation
    question, or DXI scale) with score, response distribution, benchmark, and a hidden flag that
    is true when the cohort is below the account's minimum response threshold.

    Args:
        snapshot_id (str): Snapshot ID from listSnapshots.
        score_type (str): One of:
            - "driver": developer experience driver scores (snapshots.driverScores)
            - "workflow": workflow/behavioral question scores (snapshots.workflowScores)
            - "impact": impact/outcome scores (snapshots.impactScores)
            - "csat": internal tool satisfaction scores (snapshots.csatScores)
            - "dxi": Developer Experience Index and its drivers (snapshots.dxiScores)
            - "allocation": time allocation percentages (snapshots.allocationPercentages)
        team_ids (str, optional): Comma-separated team IDs (from listTeams) to filter respondents by.
        snapshot_team_ids (str, optional): Comma-separated snapshot team IDs (from listSnapshotTeams).
            Snapshot teams are the org structure captured when the snapshot ran. Combined with team_ids
            as an intersection.
        group_ids (str, optional): Comma-separated frontline user group IDs.
        attribute_ids (str, optional): Comma-separated attribute (tag) IDs.
        branch_ids (str, optional): Comma-separated snapshot branch IDs (from listSnapshotBranches).
            DXI scores require the main branch to be included if any branches are given.
    """
    if not snapshot_id:
        return {"error": "snapshot_id is required"}
    if score_type not in SCORE_TYPES:
        return {"error": f"score_type must be one of {', '.join(SCORE_TYPES)}"}

    method = f"snapshots.{SCORE_TYPES[score_type]['method']}"
    params = _filter_params(
        snapshot_id, team_ids, snapshot_team_ids, group_ids, attribute_ids, branch_ids
    )

    data = _get(method, params)
    if "error" in data:
        return data
    return {
        "score_type": score_type,
        "filters": data.get("filters"),
        "results": data.get("results", []),
    }


@mcp.tool()
def getSnapshotScoresBreakdown(
    snapshot_id: str,
    score_type: str,
    dimension_type: str,
    item_id: str = None,
    attribute_group_id: str = None,
    parent_snapshot_team_id: str = None,
    team_ids: str = None,
    snapshot_team_ids: str = None,
    group_ids: str = None,
    attribute_ids: str = None,
    branch_ids: str = None,
) -> dict:
    """
    Break down a single snapshot score by a dimension: one row per snapshot team, group, branch,
    or attribute value. Use getSnapshotScores first to find the item_id to break down.

    Args:
        snapshot_id (str): Snapshot ID from listSnapshots.
        score_type (str): One of "driver", "workflow", "impact", "csat", "dxi", "allocation".
        dimension_type (str): One of "snapshotTeam", "group", "branch", "attribute".
            "dxi" does not support "branch".
        item_id (str, optional): ID of the item to break down. Required for every score_type except
            "dxi": the driver id, workflow id, impact id, csat id, or allocation question id as
            returned by getSnapshotScores.
        attribute_group_id (str, optional): Required when dimension_type is "attribute". The
            attribute group whose values become the rows.
        parent_snapshot_team_id (str, optional): When dimension_type is "snapshotTeam", only return
            the children of this snapshot team (from listSnapshotTeams).
        team_ids (str, optional): Comma-separated team IDs (from listTeams) to filter respondents by.
        snapshot_team_ids (str, optional): Comma-separated snapshot team IDs (from listSnapshotTeams).
            Snapshot teams are the org structure captured when the snapshot ran. Combined with team_ids
            as an intersection.
        group_ids (str, optional): Comma-separated frontline user group IDs.
        attribute_ids (str, optional): Comma-separated attribute (tag) IDs.
        branch_ids (str, optional): Comma-separated snapshot branch IDs (from listSnapshotBranches).
            DXI scores require the main branch to be included if any branches are given.
    """
    if not snapshot_id:
        return {"error": "snapshot_id is required"}
    if score_type not in SCORE_TYPES:
        return {"error": f"score_type must be one of {', '.join(SCORE_TYPES)}"}
    if dimension_type not in DIMENSION_TYPES:
        return {"error": f"dimension_type must be one of {', '.join(DIMENSION_TYPES)}"}

    score = SCORE_TYPES[score_type]
    if score["item_param"] and not item_id:
        return {"error": f"item_id is required for score_type '{score_type}'"}
    if dimension_type == "attribute" and not attribute_group_id:
        return {
            "error": "attribute_group_id is required when dimension_type is 'attribute'"
        }

    method = f"snapshots.{score['method']}.breakdown"
    params = _filter_params(
        snapshot_id, team_ids, snapshot_team_ids, group_ids, attribute_ids, branch_ids
    )
    params["dimension_type"] = dimension_type
    params["attribute_group_id"] = attribute_group_id
    params["parent_snapshot_team_id"] = parent_snapshot_team_id
    if score["item_param"]:
        params[score["item_param"]] = item_id

    data = _get(method, params)
    if "error" in data:
        return data
    return {
        "score_type": score_type,
        "filters": data.get("filters"),
        "results": data.get("results", []),
    }
