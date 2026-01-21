# DX MCP Server

<h4>Use natural language to write and execute queries on your organizational data in DX Data Cloud!</h4>

![AI Query Interface with DX MCP Server](./assets/Ai%20image%20(1).png)

## About

The DX MCP Server is a Python-based tool that empowers AI applications, such as [Claude for Desktop](https://claude.ai/download) and [Cursor](https://www.cursor.com/), to interact with your DX Data Cloud database. The server includes tools to:
- establish a connection to your Postgres database, allowing the AI to actively formulate and execute queries on the database
- find/utilize context about your software entities and their relationships and scorecards via DX catalog tools

Learn more about the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction).

## Demo

https://github.com/user-attachments/assets/c6ce12a5-4562-4b44-b235-2d04871c3142

## Getting Started

There are two ways to use the DX MCP Server:
1. **Remote hosting** (recommended): Connect to our hosted server at `https://ai.getdx.com/mcp`
2. **Local hosting**: Run the server on your machine

### Prerequisites

- A DX account with access to Data Cloud

- **For remote hosting**: 
  - A web API token with read scopes granted (found in your [DX account settings](https://app.getdx.com/admin/webapi))

- **For local hosting**: 
  - Python 3.10 or higher
  - Your database connection URL (configured on DX's [DB Users settings page](https://app.getdx.com/datacloud/dbusers))
  - A web API token with read scopes granted (found in your [DX account settings](https://app.getdx.com/admin/webapi))

---

## Option 1: Remote Hosting (Recommended)

The hosted MCP server uses streamable HTTP transport and is available at `https://ai.getdx.com/mcp`. This option requires no local installation; just configure your AI client with the mcp using http transport and provided with a valid Web API Token.

### Claude Code

Run this command in your terminal:

```bash
claude mcp add --transport http dx-mcp https://ai.getdx.com/mcp --header "Authorization: Bearer [YOUR_WEB_API_TOKEN]"
```

### Cursor

Add this configuration to your MCP settings (**Cursor > Settings > Cursor Settings > MCP**):

```json
{
  "mcpServers": {
    "dx-mcp": {
      "url": "https://ai.getdx.com/mcp",
      "headers": {
        "Authorization": "Bearer [YOUR_WEB_API_TOKEN]"
      }
    }
  }
}
```

### Claude for Desktop

Add this configuration via **Claude > Settings > Developer > Edit Config**:

```json
{
  "mcpServers": {
    "dx-mcp": {
      "url": "https://ai.getdx.com/mcp",
      "headers": {
        "Authorization": "Bearer [YOUR_WEB_API_TOKEN]"
      }
    }
  }
}
```

---

## Option 2: Local Installation

If you prefer to run the DX MCP Server locally, you can install it via PyPI or run it from source.

### Installation Method 1: Install from PyPI

Install the package using pip:

```bash
pip install dx-mcp-server
```

> **Note for macOS users**: If you encounter an "externally-managed-environment" error, use `pipx` instead:
> ```bash
> pipx install dx-mcp-server
> ```

### Installation Method 2: Clone from Source

Clone this repository to run from source:

```bash
git clone https://github.com/get-dx/dx-mcp-server
cd dx-mcp-server
```

### Configuration

Once installed, configure your AI client with the appropriate settings:

#### Claude Code

Run this command in your terminal (adjust based on your installation method):

```bash
# If installed via pip/pipx
claude mcp add dx-mcp-server --env DB_URL=YOUR_DB_URL --env WEB_API_TOKEN=YOUR_TOKEN -- $(which dx-mcp-server)
```

#### Claude for Desktop

Click **Claude > Settings > Developer > Edit Config** and add:

**If you installed via pip:**

```json
{
  "mcpServers": {
    "dx-mcp": {
      "command": "dx-mcp-server", 
      "args": ["run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL",
        "WEB_API_TOKEN": "YOUR-WEB-API-TOKEN"
      }
    }
  }
}
```

**If you're running from source:**

```json
{
  "mcpServers": {
    "dx-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/dx-mcp-server", "run", "-m", "dx_mcp_server", "run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL",
        "WEB_API_TOKEN": "YOUR-WEB-API-TOKEN"
      }
    }
  }
}
```

#### Cursor

Click **Cursor > Settings > Cursor Settings > MCP > Add new global MCP Server** and add:

**If you installed via pip:**

```json
{
  "mcpServers": {
    "dx-mcp": {
      "command": "dx-mcp-server", 
      "args": ["run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL",
        "WEB_API_TOKEN": "YOUR-WEB-API-TOKEN"
      }
    }
  }
}
```

**If you're running from source:**

```json
{
  "mcpServers": {
    "dx-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/dx-mcp-server", "run", "-m", "dx_mcp_server", "run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL",
        "WEB_API_TOKEN": "YOUR-WEB-API-TOKEN"
      }
    }
  }
}
```

### Configuration Parameters

- **`DB_URL`** (required): Your DX Data Cloud Postgres connection string. Get this from [DX DB Users settings](https://app.getdx.com/datacloud/dbusers).
  - Format: `postgresql://username:password@host:port/database`
- **`WEB_API_TOKEN`**: Your DX Web API Token. This enables additional catalog and entity tools. Find this in your DX account settings.

### Usage

After saving the configuration, restart your AI client. You should see "dx-mcp" in the available MCP servers. When you ask questions about your data or catalog, the AI will use these tools to query your database or hit the relevant web apis.

---

## Troubleshooting

### Path Resolution Issues 
The most common issue involves the MCP client not finding the `dx-mcp-server`/`uv` command, as GUI applications don't inherit the same PATH environment variables as the terminal. The solution is to use the full path to the executable in the json config.

#### For pip/pipx installations:

Find the full path to `dx-mcp-server`:

```bash
# Find the path on macOS/Linux
which dx-mcp-server

# Find the path on Windows (in Command Prompt)
where dx-mcp-server
```

Then use the full path in your configuration:

```json
{
  "mcpServers": {
    "dx-mcp": {
      "command": "/full/path/to/dx-mcp-server",
      "args": ["run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL",
        "WEB_API_TOKEN": "YOUR-WEB-API-TOKEN"
      }
    }
  }
}
```

#### For source installations:

Find the full path to `uv`:

```bash
# Find the path on macOS/Linux
which uv

# Find the path on Windows (in Command Prompt)
where uv
```

Then use the full path in your configuration:

```json
{
  "mcpServers": {
    "dx-mcp": {
      "command": "/full/path/to/uv",
      "args": ["--directory", "/absolute/path/to/dx-mcp-server", "run", "-m", "dx_mcp_server", "run"],
      "env": {
        "DB_URL": "YOUR-DATABASE-URL",
        "WEB_API_TOKEN": "YOUR-WEB-API-TOKEN"
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

The logs will show warning and error messages when starting or running the MCP server.