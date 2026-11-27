"""
quickloan/tools.py
------------------
Tool definitions and LLM setup for QuickLoan.

Session 5 adds two @tool functions that give the LLM live access to the
FastFinance database. Instead of relying only on RAG policy chunks (Session 4),
the LLM can now call query_rates() and query_branch() to get exact data.

New this session:
  query_rates()   -- fetches current loan rates and product details from the DB
  query_branch()  -- fetches FastFinance branch locations and contact details
  TOOLS           -- list of available tools (used by both bind_tools and _run_tool)
  llm_with_tools  -- the respond LLM with tools bound
  _run_tool()     -- helper that executes whichever tool the LLM requested

Carries forward from Session 4:
  llm             -- still used internally; llm_with_tools wraps it
  classifier_llm  -- unchanged: classifier does not use tools
"""
import os
import sqlite3
from collections import OrderedDict

# langchain_core.tools is a submodule that ships several tool-related utilities:
#   tool            -- decorator used here: wraps a plain function into a LangChain Tool object
#   BaseTool        -- base class all tools inherit from (used internally by @tool)
#   StructuredTool  -- explicit alternative to @tool when you need more control
#   InjectedToolArg -- marks arguments the system fills in, not the LLM
# We only import `tool` because the @tool decorator handles everything automatically.
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from .config import (
    CLASSIFIER_MAX_TOKENS, CLASSIFIER_MODEL, CLASSIFIER_TEMPERATURE,
    DB_PATH, MAX_TOKENS, MODEL_NAME, TEMPERATURE,
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found.\n"
        "Did you copy .env.example to .env and fill in your key?\n"
        "  Windows:  copy .env.example .env\n"
        "  Mac/Linux: cp .env.example .env"
    )

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)

# openai/gpt-oss-20b thinks internally before emitting the visible token.
# reasoning_effort="low" caps internal thinking at 3-33 tokens (default is 60-98),
# so the one-word answer fits inside max_tokens=200. Without it, the model can
# exhaust its budget on thinking and return an empty string.
classifier_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=CLASSIFIER_MODEL,
    temperature=CLASSIFIER_TEMPERATURE,
    max_tokens=CLASSIFIER_MAX_TOKENS,
    reasoning_effort="low",
)


# ---------------------------------------------------------------------------
# TODO 1 of 4 -- implement query_rates()
# ---------------------------------------------------------------------------
# query_rates() fetches FastFinance India loan rates from the SQLite database.
#
# Decorate with @tool and give it a clear docstring -- the docstring becomes
# the tool's description in the JSON schema sent to the LLM. The LLM reads
# it to decide when and how to call the tool. Poor docstrings = wrong calls.
#
# Steps:
#
#   1. Decorate with @tool:
#        @tool
#        def query_rates(product_type: str = "all") -> str:
#
#   2. Write a descriptive docstring explaining:
#        - what the function does (fetch FastFinance loan rates)
#        - what product_type accepts: "personal", "home", "business", "gold", or "all"
#        - what the return value looks like
#
#   3. Open a SQLite connection (use check_same_thread=False):
#        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
#
#   4. Query with a JOIN between rate_slabs and loan_products:
#      If product_type == "all":
#        rows = conn.execute(
#            "SELECT lp.product_name, lp.min_tenure_months, lp.max_tenure_months, "
#            "lp.max_loan_amount, lp.processing_fee_pct, rs.min_cibil, rs.max_cibil, rs.annual_rate_pct "
#            "FROM rate_slabs rs "
#            "JOIN loan_products lp ON rs.product_id = lp.product_id "
#            "ORDER BY lp.product_id, rs.min_cibil DESC"
#        ).fetchall()
#      Otherwise (use parameterised LIKE for the product type):
#        rows = conn.execute(
#            "SELECT lp.product_name, lp.min_tenure_months, lp.max_tenure_months, "
#            "lp.max_loan_amount, lp.processing_fee_pct, rs.min_cibil, rs.max_cibil, rs.annual_rate_pct "
#            "FROM rate_slabs rs "
#            "JOIN loan_products lp ON rs.product_id = lp.product_id "
#            "WHERE lp.product_id LIKE ? "
#            "ORDER BY rs.min_cibil DESC",
#            (f"%{product_type}%",),
#        ).fetchall()
#      conn.close()
#
#   5. Group rows by product name, then format as one line per product:
#        "Personal Loan: 11.50% p.a. (CIBIL 750-900), 13.00% p.a. (CIBIL 720-749) | tenure 12-60 months | up to Rs.5 lakh | processing fee 2.0%"
#
#   6. Return "\n".join(lines) or a "No rate data found" message.
#
# WHY check_same_thread=False?
#   SQLite raises ProgrammingError if a connection is used from a different thread
#   than the one that created it. LangGraph runs tool calls in a thread-pool
#   executor, so the tool may run on a different thread than the one that opened
#   the connection. This flag disables that check.
# ---------------------------------------------------------------------------

# TODO 1: implement query_rates() below -- keep the @tool decorator and docstring
raise NotImplementedError("TODO 1: implement query_rates() in quickloan/tools.py")


# ---------------------------------------------------------------------------
# TODO 2 of 4 -- implement query_branch()
# ---------------------------------------------------------------------------
# query_branch() fetches FastFinance branch locations from the SQLite database.
#
# Steps:
#
#   1. Decorate with @tool:
#        @tool
#        def query_branch(city: str = "all") -> str:
#
#   2. Write a descriptive docstring explaining:
#        - what the function does (fetch branch info)
#        - what city accepts: any city name or "all"
#        - what the return value looks like
#
#   3. Open connection (check_same_thread=False):
#        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
#
#   4. Fetch branches:
#      - If city == "all": SELECT all branches (ORDER BY city)
#        SELECT city, address, phone, email FROM branch_contacts ORDER BY city
#      - Otherwise: filter by city using parameterised LIKE (% wildcards):
#        SELECT city, address, phone, email
#        FROM branch_contacts WHERE city LIKE ?
#        Use (f"%{city}%",) as the parameter
#      conn.close()
#
#   5. Format each branch as:
#        f"{city_}: {address} | Ph: {phone} | Email: {email}"
#      Return "\n".join(parts)
#
#   6. If no rows: return f"No FastFinance branches found for city: '{city}'."
#
# ---------------------------------------------------------------------------

# TODO 2: implement query_branch() below -- keep the @tool decorator and docstring
raise NotImplementedError("TODO 2: implement query_branch() in quickloan/tools.py")


# ---------------------------------------------------------------------------
# TODO 3 of 4 -- TOOLS list + llm_with_tools + _run_tool()
# ---------------------------------------------------------------------------
# Three steps:
#
#   Step A: build the TOOLS list
#     Declaring TOOLS as a named list makes it easy to add or remove tools
#     in one place. Both bind_tools() and _run_tool's registry are built from
#     this single list.
#
#        TOOLS = [
#            query_rates,
#            query_branch,
#        ]
#
#   Step B: create llm_with_tools
#     bind_tools() reads each function's type hints and docstring, converts them
#     to a JSON schema, and includes that schema in every request sent to the LLM.
#
#        llm_with_tools = llm.bind_tools(TOOLS)
#
#   Step C: implement _run_tool()
#
#        def _run_tool(tool_name: str, tool_args: dict) -> str:
#
#     Build a registry dict from TOOLS:
#        _registry = {t.name: t for t in TOOLS}
#     Return an error string if the tool name is unknown.
#     Otherwise call the tool's .invoke() method:
#        return _registry[tool_name].invoke(tool_args)
#     Wrap in try/except and return an error string on failure.
#
# WHY .invoke() and not a plain function call?
#   .invoke() validates arguments against the tool's schema before executing,
#   and it integrates with LangSmith -- the tool call appears as a separate trace span.
# ---------------------------------------------------------------------------

# TODO 3: add TOOLS list, llm_with_tools, and _run_tool() below
raise NotImplementedError("TODO 3: add TOOLS, llm_with_tools, and _run_tool() in quickloan/tools.py")
