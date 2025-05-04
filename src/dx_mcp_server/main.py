import argparse
import sys
from . import __version__
from .server import mcp


def main():
    """Main entry point for the DX MCP Server."""
    parser = argparse.ArgumentParser(description="DX MCP Server for database queries")
    parser.add_argument('--version', action='version', 
                        version=f'%(prog)s {__version__}')
    args = parser.parse_args()
    
    mcp.run()


if __name__ == "__main__":
    main() 