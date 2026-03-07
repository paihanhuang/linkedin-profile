---
paths:
  - "mcp-server/**"
---

# MCP Server Conventions

- Use FastMCP framework for all server implementations
- Each tool in its own file under `mcp-server/src/tools/`
- Tool functions must have clear docstrings — these become the tool descriptions Claude sees
- Keep tool output under 25,000 tokens (MCP output limit)
- Handle errors with clear, actionable messages — distinguish client errors from server errors
- Support pagination for large results
- All tools must be stateless — no global mutable state between calls
- Type hints on all function signatures
- Test each tool independently before registering with server
