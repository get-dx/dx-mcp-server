from os import environ
from fastmcp import FastMCP

mcp = FastMCP(name="dx-mcp")

# Tools
from dx_mcp_server.tools import entity_tools
from dx_mcp_server.tools import data_tools
from dx_mcp_server.tools import scorecard_tools
from dx_mcp_server.tools import team_tools

# Prompts
from dx_mcp_server.prompts import scorecard_prompts

# Resources
