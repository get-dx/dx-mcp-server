# DX MCP Server

<h4>Use natural language to write and execute queries on your organizational data in DX Data Cloud!</h4>


## About

The DX MCP Server is a Python-based tool that lets you interact with your Data Cloud database through MCP clients, such as [Claude for Desktop](https://claude.ai/download) and [Cursor](https://www.cursor.com/). The server runs locally and establishes a connection to the inputted Postgres database. A query tool is exposed, allowing the AI to formulate and execute queries on the database.


## Installation

You can use the DX MCP Server in two ways:

### Option 1: Install from PyPI

Install directly using pip:

```bash
pip install dx-mcp-server
```

### Option 2: Use from Source

Simply clone this repository:

```bash
git clone https://github.com/get-dx/dx-mcp-server
```

## Set up the MCP client

Both Claude for Desktop and Cursor use JSON configuration files to set up MCP servers. The configuration process is similar for both:

### 1. Access the configuration file

- **Claude for Desktop**: Click **Claude > Settings > Developer > Edit Config**
  - Config location: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- **Cursor**: Click **Cursor > Settings > Cursor Settings > MCP > Add new global MCP Server**
  - This directly opens the JSON editor

### 2. Add the MCP server configuration

Add the following configuration to the JSON file, adjusting based on your installation method:

#### If you installed via pip:

```json
{
  "mcpServers": {
    "DX Data": {
      "command": "dx-mcp-server",
      "env": {
        "DB_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

#### If you're using from source:

```json
{
  "mcpServers": {
    "DX Data": {
      "command": "python", # MacOS users may need to instead use the path to the Python executable
      "args": ["-m", "dx_mcp_server"],
      "cwd": "/path/to/dx-mcp-server",  # Replace with the path to your cloned repository
      "env": {
        "DB_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```


### 3. Restart and use

After saving the configuration, restart your MCP client. You should see "DX Data" in the available tools. When you use the database query tool, the client will ask for your approval before proceeding.
