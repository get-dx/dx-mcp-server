from dx_mcp_server.server import mcp


@mcp.prompt()
def summarizeSnapshot(team: str = "") -> str:
    """
    Summarize the results of the latest completed DX snapshot.

    Args:
        team: Optional team name to scope the summary to one team.
    """
    scope = f" for the team named {team}" if team else ""
    return (
        f"Summarize the latest completed DX snapshot{scope}. "
        "Read the resource skill://snapshot-summary/SKILL.md and follow it exactly."
    )
