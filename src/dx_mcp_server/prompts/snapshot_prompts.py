from dx_mcp_server.server import mcp


@mcp.prompt()
def summarizeSnapshot() -> str:
    """
    Summarize the results of the latest completed DX snapshot.
    """
    return (
        "Summarize the latest completed DX snapshot. "
        "Read the resource skill://snapshot-summary/SKILL.md and follow it exactly."
    )
