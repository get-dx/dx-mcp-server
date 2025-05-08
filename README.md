# DX MCP Server

<h4>Use natural language to write and execute queries on your organizational data in DX Data Cloud!</h4>


## About

The DX MCP Server is a Python-based tool that empowers AI applications, such as [Claude for Desktop](https://claude.ai/download) and [Cursor](https://www.cursor.com/), to interact with your Data Cloud database. The server runs locally and establishes a connection to the inputted Postgres database, which can be configured on DX's [DB Users settings page](https://app.getdx.com/datacloud/dbusers). A query tool is exposed to the MCP client application, allowing the AI to actively formulate and execute queries on the database. Click [here](https://modelcontextprotocol.io/introduction) to learn more about MCP.


## Demo

https://github.com/user-attachments/assets/c6ce12a5-4562-4b44-b235-2d04871c3142




## Installation

You can install the DX MCP Server in two ways:

### Option 1: Install from PyPI

Install directly using pip:

```bash
pip install dx-mcp-server
```

**NOTE**: For macOS users: if you encounter an "externally-managed-environment" error, use `pipx` instead to install the package.

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
  - This directly opens the `mcp.json` file

### 2. Add the MCP server configuration

Add the following configuration to the JSON file, adjusting based on your installation method:

#### If you installed via pip:

```json
{
  "mcpServers": {
    "DX Data": {
      "command": "dx-mcp-server", 
      "args": ["run"],
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
      "command": "python",
      "args": ["-m", "dx_mcp_server", "run"],
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


## Troubleshooting

### Path Resolution Issues 
The most common issue involves the MCP client not finding the `dx-mcp-server`/`python` command, as GUI applications don't inherit the same PATH environment variables as the terminal. The solution is to use the full path to the executable in the json config.

```bash
# Find the path on macOS/Linux
which dx-mcp-server

# Find the path on Windows (in Command Prompt)
where dx-mcp-server
```

```json
{
  "mcpServers": {
    "DX Data": {
      "command": "/full/path/to/dx-mcp-server",
      "args": ["run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

### Checking Logs
If you're still experiencing issues:

- **Claude Desktop**: Check logs at:
  - macOS: `~/Library/Logs/Claude/`
  - Windows: `%APPDATA%\Claude\logs\`

- **Cursor**: Check logs at:
  - macOS: `~/Library/Application Support/Cursor/logs/[SESSION_ID]`
  - Windows: `%APPDATA%\Cursor\logs\[SESSION_ID]`

The logs will show any errors that occur when trying to start the MCP server.
