from os import environ
import requests

from dx_mcp_server.server import mcp

DX_API_HOST = environ.get("DX_API_HOST", "https://api.getdx.com")
WEB_API_TOKEN = environ.get("WEB_API_TOKEN", "")


@mcp.tool()
def listTeams() -> dict:
    """
    List all teams in DX.
    """
    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }

    try:
        url = f"{DX_API_HOST}/teams.list"
        response = requests.get(url, headers=headers)

        response.raise_for_status()
        data = response.json()

        if data.get("ok") is False:
            error = data.get("error", "Unknown error")
            return {"error": f"API error: {error}"}

        return {"teams": data.get("teams", [])}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


@mcp.tool()
def getTeamDetails(
    team_id: str = None,
    reference_id: str = None,
    team_emails: str = None,
) -> dict:
    """
    Retrieve details for an individual team. Note that searching by team_emails will return
    things like the team name and members, where the search by team_id/reference_id will
    return more detailed information about the team structure.

    Args:
        team_id (str, optional): The DX team ID.
        reference_id (str, optional): The team's internal reference ID in your organization.
        team_emails (str, optional): Comma separated list of team members' email addresses.
    """
    if not team_id and not reference_id and not team_emails:
        return {"error": "team_id or reference_id or team_emails is required"}

    if not WEB_API_TOKEN:
        return {"error": "WEB_API_TOKEN environment variable is not set"}

    headers = {
        "Authorization": f"Bearer {WEB_API_TOKEN}",
        "Accept": "application/json",
    }

    try:
        if team_emails:
            url = f"{DX_API_HOST}/teams.findByMembers"
            params = {"team_emails": team_emails}
        else:
            url = f"{DX_API_HOST}/teams.info"
            params = {"team_id": team_id} if team_id else {"reference_id": reference_id}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("ok") is False:
            error = data.get("error", "Unknown error")
            return {"error": f"API error: {error}"}

        return {"team": data.get("team")}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
