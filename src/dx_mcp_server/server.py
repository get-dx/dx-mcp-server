from os import environ
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP(name="dx-mcp")

# Tools
from dx_mcp_server.tools import entity_tools
from dx_mcp_server.tools import data_tools
from dx_mcp_server.tools import scorecard_tools
from dx_mcp_server.tools import team_tools
from dx_mcp_server.tools import snapshot_tools

# Prompts
from dx_mcp_server.prompts import scorecard_prompts
from dx_mcp_server.prompts import snapshot_prompts

# Resources (skills served as skill:// resources)
mcp.add_provider(SkillsDirectoryProvider(Path(__file__).parent / "skills"))
