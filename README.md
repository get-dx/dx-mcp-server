# DX MCP Server

<h4>Use natural language to write and execute queries on organizational data in your DX Datacloud!</h4>


## About

The DX MCP Server is a Python-based tool that lets you interact with your Datacloud database through MCP clients, such as Claude Desktop and Cursor. The server runs locally and establishes a connection to the inputted Postgres database. A query tool is exposed, allowing the AI to formulate and execute queries on the database.


## Installation

Currently, downloading from source is the only supported installation method. 

1. Install UV

```bash
brew install uv
```

2. Clone this repository

```bash
git clone https://github.com/get-dx/dx-mcp-server
```

3. Set up the MCP client

Setup instructions will vary depending on the MCP Client. Detailed instructions for Claude Desktop and Cursor are provided below.

### Claude Desktop

1. From the top of Claude Desktop, click **Claude > Settings > Developer**
2. Click **Edit Config**. A configuration file is created at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the MCP server to `claude_desktop_config.json`. This can be automatically set up through MCP's `install` CLI command

```bash
cd dx-mcp-server
uv run mcp install main.py --name "DXDC Database Explorer" --with psycopg -v DB_URL=YOUR-DB-URL
```

or configured manually (make sure to replace the placeholders `<LOCAL-PATH-TO-CLONED-REPO>` with the path where you downloaded the cloned the repo, and `<YOUR-DB-URL>` with the Postgres database URL).
)

```json
{
  "mcpServers": {
    "DXDC Database Explorer": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "psycopg",
        "mcp",
        "run",
        "<LOCAL-PATH-TO-CLONED-REPO>/dx-mcp-server/main.py"
      ],
      "env": {
        "DB_URL": <YOUR-DB-URL>
      }
    }
  }
}
```

4. Restart Claude. Now, you should see the MCP server in "Search and Tools" on the bottom-left of the chatbox.
5. Start prompting! Each time you use a new tool, Claude will ask for your approval before proceeding.


### Cursor

1. Open Cursor and click **Cursor > Settings > Cursor Settings > MCP**.
2. Click **Add new global MCP Server** and add the MCP server to the `mcp.json` file (make sure to replace the placeholders `<LOCAL-PATH-TO-CLONED-REPO>` with the path where you downloaded the cloned the repo, and `<YOUR-DB-URL>` with the Postgres database URL).

```json
{
  "mcpServers": {
    "DXDC Database Explorer": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "psycopg",
        "mcp",
        "run",
        "<LOCAL-PATH-TO-CLONED-REPO>/dx-mcp-server/main.py"
      ],
      "env": {
        "DB_URL": <YOUR-DB-URL>
      }
    }
  }
}
```

3. Now, the MCP server should be displayed in Cursor Settings. Ensure it's toggled on. 
4. Start prompting!