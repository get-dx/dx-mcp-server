import os
from typing import Optional
from urllib.parse import urlparse

import psycopg
from mcp.server.fastmcp import FastMCP


DB_URI = os.environ.get("DB_URL")
if not DB_URI:
    raise ValueError("DB_URL environment variable is not set")

parsed_uri = urlparse(DB_URI)
db_name = parsed_uri.path.lstrip('/')
server_title = "DX Data"

mcp = FastMCP(server_title, dependencies=["psycopg"])


@mcp.tool()
def queryData(sql: str) -> str:
    """
    Execute a SQL query against the PostgreSQL database.
    Always query from information_schema if you are uncertain about which tables and columns to look at.
    Args:
        sql (str): SQL query to execute
        
    Returns:
        str: Formatted query results or error message
    """
    try:
        with psycopg.connect(DB_URI, row_factory=psycopg.rows.tuple_row) as conn:

            with conn.cursor() as cur:
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


if __name__ == "__main__":
    mcp.run()
