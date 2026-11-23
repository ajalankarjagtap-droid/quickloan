"""
QuickLoan -- Session 7: MCP Server (US-06 Part 1)
==================================================

What you build this session
  QuickLoan's two database tools -- query_rates and query_eligibility --
  are reimplemented as MCP (Model Context Protocol) tools in a standalone
  server. MCP Inspector can discover and invoke them independently of any
  agent code.

  Session 8 connects the QuickLoan agent to this server. This session
  is about the server only -- the s05 agent is not changed.

What changed from Session 6
  - New file: s07/starter/mcp_server.py (this file)
  - query_rates and query_eligibility from s05 are moved here as @mcp.tool()
    functions. Same SQL queries, same return format, different decorator.
  - Agent code (s05/s06) is not touched -- evaluation still imports from s05

Why MCP (the one-sentence version)
  Direct tool binding (s05 pattern) couples tools to the agent file.
  MCP decouples them: the server runs independently, any MCP-compatible
  agent can call it, and tools can be tested and versioned separately.

Run the server
  python s07/starter/mcp_server.py
  (Server starts and waits on stdin for MCP messages -- use Inspector to send them)

Inspect with MCP Inspector
  npx @modelcontextprotocol/inspector python s07/starter/mcp_server.py
  Then open the URL printed in the terminal (includes ?MCP_INSPECTOR_API_TOKEN=...).
"""

import sqlite3
from pathlib import Path

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server instantiation
# ---------------------------------------------------------------------------

# FastMCP handles all the MCP protocol machinery (tool registration, schema
# generation, JSON-RPC message handling). You only write the business logic.
# The string here is the server name visible to MCP clients like the Inspector.
mcp = FastMCP("quickloan-tools")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH  = DATA_DIR / "fastfinance_data.db"

# ---------------------------------------------------------------------------
# TODO 1 of 2 -- implement query_rates()
# ---------------------------------------------------------------------------
# Copy the query_rates() function body from s05/solution/quickloan/tools.py.
# Change @tool to @mcp.tool() -- that is the only required change.
# The SQL queries and return format are identical.

@mcp.tool()
def query_rates(product_id: str = "all") -> str:
    """Fetch current FastFinance loan interest rates and fees from the database.

    Args:
        product_id: Filter by loan product ID (e.g. "pl_001" for personal loan).
                    Use "all" to return every loan product.

    Returns formatted rate and fee information as a plain-text string.
    """
    # TODO 1: implement the function body
    # Copy the SQL logic from s05/solution/quickloan/tools.py
    raise NotImplementedError("TODO 1: implement query_rates() in mcp_server.py")


# ---------------------------------------------------------------------------
# TODO 2 of 2 -- implement query_eligibility()
# ---------------------------------------------------------------------------
# Copy the query_eligibility() function body from s05/solution/quickloan/tools.py.
# Change @tool to @mcp.tool() -- that is the only required change.
# ---------------------------------------------------------------------------

@mcp.tool()
def query_eligibility(product_id: str = "all") -> str:
    """Fetch FastFinance loan eligibility criteria from the database.

    Args:
        product_id: Filter by loan product ID (e.g. "pl_001").
                    Use "all" to return eligibility for all products.

    Returns formatted eligibility criteria as a plain-text string.
    """
    # TODO 2: implement the function body
    # Copy the SQL logic from s05/solution/quickloan/tools.py
    raise NotImplementedError("TODO 2: implement query_eligibility() in mcp_server.py")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # mcp.run() starts the server with STDIO transport.
    # No port or HTTP -- the MCP Inspector (and the agent in S08) starts this
    # file as a subprocess and communicates over stdin/stdout.
    mcp.run()  # STDIO transport by default
