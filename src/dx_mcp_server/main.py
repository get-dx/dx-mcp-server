import argparse
import sys
from . import __version__
from .server import mcp


def run_command(args):
    """Run the MCP server."""
    mcp.run()

def main():
    """Main entry point for the DX MCP Server."""
    parser = argparse.ArgumentParser(description="DX MCP Server for database queries")
    parser.add_argument('--version', action='version', 
                        version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    run_parser = subparsers.add_parser('run', help='Run the MCP server')
    
    args = parser.parse_args()
    
    # If no command is provided, default to run
    if args.command is None:
        run_command(args)
    elif args.command == 'run':
        run_command(args)


if __name__ == "__main__":
    main() 