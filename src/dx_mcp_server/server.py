import os
from urllib.parse import urlparse

import psycopg
from mcp.server.fastmcp import FastMCP


SERVER_NAME = "DX Data Cloud"
dependencies = ["psycopg"]

mcp = FastMCP(SERVER_NAME, dependencies=dependencies)
db_uri = os.environ.get("DB_URL")


@mcp.tool()
def queryData(sql: str) -> str:
    """
    Execute a SQL query against the DX Data Cloud PostgreSQL database.
    Always query from information_schema if you are uncertain about which tables and columns to look at.
    Args:
        sql (str): SQL query to execute
        
    Returns:
        str: Formatted query results or error message
    """
    if not db_uri:
        return "Error: DB_URL environment variable is not set"

    try:
        with (psycopg.connect(db_uri, row_factory=psycopg.rows.tuple_row) as conn, 
              conn.cursor() as cur):
            cur.execute(sql)
            
            if cur.description:
                results = cur.fetchall()
                
                if not results:
                    return "Query executed successfully, but returned no rows."
                
                header = ", ".join([desc[0] for desc in cur.description])
                rows = [header]
                
                rows.extend(", ".join(map(str, row)) for row in results)
                return "\n".join(rows)
            else:
                return cur.statusmessage or "Command executed successfully, no rows returned."
    except psycopg.Error as e:
        return f"Database Error: {str(e)}"
    except Exception as e:
        return f"Error executing query: {str(e)}"