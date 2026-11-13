from os import environ
import requests

from dx_mcp_server.server import mcp

DX_API_HOST = environ.get("DX_API_HOST", "https://api.getdx.com")
WEB_API_TOKEN = environ.get("WEB_API_TOKEN", "")


def _dxi_item(r: dict) -> dict:
    """DXI results carry no item; synthesize one per scale so the two scales stay apart."""
    scale = "five" if r.get("is_five_point_scale") else "three"
    return {"id": f"dxi_{scale}_point", "name": f"DXI ({scale}-point scale)"}


def _rated_answers(r: dict) -> int:
    """Driver and CSAT respondents: count answers, leaving out "I don't know / N/A"."""
    return sum(
        v for k, v in (r.get("distribution") or {}).items() if k != "idk_na_count"
    )


def _impact_respondents(r: dict) -> int:
    """Impact respondents: the distribution is a list of options; N/A has a null value."""
    return sum(
        d.get("count") or 0
        for d in (r.get("distribution") or [])
        if d.get("value") is not None
    )


def _allocation_rows(results: list) -> list:
    """Allocation results are one row per question with nested items; flatten to one row per
    item so items can be matched by id across snapshots. The percentage becomes the score.
    """
    rows = []
    for q in results:
        for item in q.get("items") or []:
            rows.append(
                {
                    "item": {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "bucket": item.get("bucket"),
                        "unit": "%",
                    },
                    "score": item.get("percentage"),
                    "hidden": q.get("hidden"),
                    "total_respondents": q.get("total_respondents"),
                }
            )
    return rows


# Score types supported by the snapshots.*Scores and snapshots.*.breakdown web API methods.
# Each maps to the API method prefix and the name of the item id param its breakdown expects.
# Types that compareSnapshotScores supports also say how to read a result row: "item" returns
# the scored item (id, name, benchmark, ...) and "respondents" returns the respondent count.
# "rows", when present, reshapes the API results into one row per scored item first, and
# "directional": False marks types where a change is neither better nor worse.
SCORE_TYPES = {
    "driver": {
        "method": "driverScores",
        "item_param": "driver_id",
        "item": lambda r: r.get("driver") or {},
        "respondents": _rated_answers,
    },
    "workflow": {
        "method": "workflowScores",
        "item_param": "workflow_id",
        "item": lambda r: r.get("workflow") or {},
        "respondents": lambda r: r.get("total_respondents"),
    },
    "impact": {
        "method": "impactScores",
        "item_param": "impact_id",
        "item": lambda r: r.get("impact") or {},
        "respondents": _impact_respondents,
    },
    "csat": {
        "method": "csatScores",
        "item_param": "csat_id",
        "item": lambda r: r.get("csat") or {},
        "respondents": _rated_answers,
    },
    "dxi": {
        "method": "dxiScores",
        "item_param": None,
        "item": _dxi_item,
        "respondents": lambda r: r.get("total_respondents"),
    },
    "allocation": {
        "method": "allocationPercentages",
        "item_param": "question_id",
        "rows": _allocation_rows,
        "item": lambda r: r.get("item") or {},
        "respondents": lambda r: r.get("total_respondents"),
        "directional": False,
    },
}
COMPARABLE_SCORE_TYPES = [t for t, score in SCORE_TYPES.items() if "item" in score]


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
        response = requests.get(url, params=params, headers=headers, timeout=30)
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
    """
    Args:
        team_ids (str, optional): Comma-separated team IDs (from listTeams) to filter respondents by.
        snapshot_team_ids (str, optional): Comma-separated snapshot team IDs (from listSnapshotTeams)
            to filter respondents by. Snapshot teams are the org structure captured when the snapshot
            ran. Combined with team_ids as an intersection.
        group_ids (str, optional): Comma-separated frontline user group IDs to filter respondents by.
        attribute_ids (str, optional): Comma-separated attribute (tag) IDs to filter respondents by.
        branch_ids (str, optional): Comma-separated snapshot branch IDs (from listSnapshotBranches)
            to filter respondents by. DXI scores require the main branch to be included if any branches are given.
    """
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
            - "driver": Drivers of developer experience (snapshots.driverScores)
            - "workflow": Workflow/behavioral questions (snapshots.workflowScores)
            - "impact": Impact/outcome scores (snapshots.impactScores)
            - "csat": Internal tool satisfaction scores (snapshots.csatScores)
            - "dxi": Developer Experience Index and its drivers (snapshots.dxiScores)
            - "allocation": Time allocation percentages (snapshots.allocationPercentages)
        Optional filters (see _filter_params for details):
            - team_ids
            - snapshot_team_ids
            - group_ids
            - attribute_ids
            - branch_ids (DXI scores require the main branch to be included if any branches are given)
    """
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
        Optional filters (see _filter_params for details):
            - team_ids
            - snapshot_team_ids
            - group_ids
            - attribute_ids
            - branch_ids (DXI scores require the main branch to be included if any branches are given)
    """
    # validate score_type locally because it is used to build the method name
    if score_type not in SCORE_TYPES:
        return {"error": f"score_type must be one of {', '.join(SCORE_TYPES)}"}

    score = SCORE_TYPES[score_type]
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


@mcp.tool()
def getSnapshotComments(snapshot_id: str, limit: int = 100, cursor: str = None) -> dict:
    """
    Get driver comments left by respondents in a snapshot, newest first. The API applies the
    token's comment visibility rules. Commenter identities are removed. There are no driver
    or team filters, so group the results by driver_name yourself.

    Args:
        snapshot_id (str): Snapshot ID from listSnapshots.
        limit (int, optional): Comments per page, 1 to 100. Defaults to 100.
        cursor (str, optional): next_cursor from the previous page. Omit for the first page.
    """
    data = _get(
        "snapshots.driverComments.list",
        {"id": snapshot_id, "limit": max(1, min(limit, 100)), "cursor": cursor},
    )
    if "error" in data:
        return data
    # Allowlist fields so any identifying data the API adds later never reaches the caller.
    comments = [
        {k: comment.get(k) for k in ("driver_name", "text", "created_at")}
        for comment in data.get("comments", [])
    ]
    return {
        "comments": comments,
        "next_cursor": (data.get("response_metadata") or {}).get("next_cursor"),
    }


def _index_rows(results: list, score: dict) -> dict:
    """Index getSnapshotScores results by item id, in the shape compareSnapshotScores returns."""
    rows = {}
    for r in score.get("rows", lambda rs: rs)(results):
        item = score["item"](r)
        rows[item.get("id")] = {
            "id": item.get("id"),
            "name": item.get("name"),
            "score": r.get("score"),
            "hidden": bool(r.get("hidden")),
            "respondents": score["respondents"](r),
            "distribution": r.get("distribution"),
            "benchmark_p_50": (item.get("benchmark") or {}).get("p_50"),
            "unit": item.get("unit"),
            "lower_is_better": bool(item.get("lower_is_better")),
        }
    return rows


def _stub(row: dict) -> dict:
    return {"id": row["id"], "name": row["name"]}


@mcp.tool()
def compareSnapshotScores(
    snapshot_id: str,
    score_type: str,
    comparison_snapshot_id: str = None,
    team_ids: str = None,
    snapshot_team_ids: str = None,
    group_ids: str = None,
    attribute_ids: str = None,
    branch_ids: str = None,
) -> dict:
    """
    Normalize one score type for a snapshot and, if a comparison snapshot is given, compute the
    change from it. Arithmetic is done here so it does not have to be done by hand. Rows hidden in either
    snapshot, or with no score in the current one, are listed under hidden; rows present in
    only one snapshot are listed under only_in_current or only_in_comparison. Both are left
    out of results.

    Each result has: id, name, score, previous_score, change (score - previous_score), direction
    ("better", "worse" or "flat", taking lower_is_better into account), respondents (for drivers
    this excludes "I don't know / N/A" answers), distribution (the current snapshot's answer
    counts), benchmark_p_50, vs_p_50 (score - benchmark_p_50, or null if no benchmark), unit, and
    lower_is_better. Without a comparison snapshot, previous_score, change and direction are null.
    Results are sorted by change, largest increase first, or by name when there is no comparison.

    "dxi" returns one row per scale (dxi_five_point, dxi_three_point). "allocation" returns one
    row per allocation item, with the item's percentage as the score and unit "%"; its direction
    is null because a shift in time allocation is not better or worse on its own. "csat" and
    "allocation" have no benchmark, so vs_p_50 is null.

    Args:
        snapshot_id (str): The current snapshot ID from listSnapshots.
        score_type (str): One of "driver", "workflow", "impact", "csat", "dxi", "allocation".
        comparison_snapshot_id (str, optional): An earlier snapshot ID to compare against.
        Optional filters, applied to both snapshots (see _filter_params for details):
            - team_ids
            - snapshot_team_ids
            - group_ids
            - attribute_ids
            - branch_ids
    """
    if score_type not in COMPARABLE_SCORE_TYPES:
        return {
            "error": f"score_type must be one of {', '.join(COMPARABLE_SCORE_TYPES)}"
        }
    if snapshot_id == comparison_snapshot_id:
        return {"error": "snapshot_id and comparison_snapshot_id must be different"}

    filters = (team_ids, snapshot_team_ids, group_ids, attribute_ids, branch_ids)
    snapshots = {"current": snapshot_id, "comparison": comparison_snapshot_id}
    indexed = {}
    for label, sid in snapshots.items():
        if not sid:
            continue
        data = getSnapshotScores(sid, score_type, *filters)
        if "error" in data:
            data["error"] = f"{label} snapshot {sid}: {data['error']}"
            return data
        indexed[label] = _index_rows(data["results"], SCORE_TYPES[score_type])
    current, previous = indexed["current"], indexed.get("comparison", {})

    results, hidden, only_current = [], [], []

    for item_id, row in current.items():
        prev = previous.get(item_id)
        if comparison_snapshot_id and prev is None:
            only_current.append(_stub(row))
            continue
        if row["hidden"] or row["score"] is None or (prev and prev["hidden"]):
            hidden.append(_stub(row))
            continue

        change = direction = None
        if prev and prev["score"] is not None:
            change = round(row["score"] - prev["score"], 2)
            if not SCORE_TYPES[score_type].get("directional", True):
                direction = None
            elif change == 0:
                direction = "flat"
            elif (change < 0) == row["lower_is_better"]:
                direction = "better"
            else:
                direction = "worse"

        p50 = row["benchmark_p_50"]
        result = {
            **row,
            "previous_score": prev["score"] if prev else None,
            "change": change,
            "direction": direction,
            "vs_p_50": round(row["score"] - p50, 2) if p50 is not None else None,
        }
        del result["hidden"]
        results.append(result)

    only_previous = [_stub(row) for i, row in previous.items() if i not in current]

    if comparison_snapshot_id:
        results.sort(
            key=lambda r: r["change"] if r["change"] is not None else 0, reverse=True
        )
    else:
        results.sort(key=lambda r: r["name"] or "")

    return {
        "score_type": score_type,
        "snapshot_id": snapshot_id,
        "comparison_snapshot_id": comparison_snapshot_id,
        "results": results,
        "hidden": hidden,
        "only_in_current": only_current,
        "only_in_comparison": only_previous,
    }
