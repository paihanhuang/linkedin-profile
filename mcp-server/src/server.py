"""FastMCP server entry point — registers all tools and runs the server."""

import logging

from fastmcp import FastMCP

from src.tools.patterns import save_pattern, get_pattern, search_patterns, delete_pattern
from src.tools.scaffold import scaffold_project
from src.tools.checklist import check_criteria

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

mcp = FastMCP("claude-mcp-server")

mcp.tool()(save_pattern)
mcp.tool()(get_pattern)
mcp.tool()(search_patterns)
mcp.tool()(delete_pattern)
mcp.tool()(scaffold_project)
mcp.tool()(check_criteria)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
