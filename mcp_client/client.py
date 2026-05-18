"""MCP client that connects to our custom MCP server over stdio.

Spawns the server as a subprocess and communicates via the MCP protocol.
This replaces direct Google API calls — agents now go through MCP.
"""

import asyncio
import sys
import os
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Path to our MCP server script
SERVER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "mcp_server",
    "server.py"
)

# Parameters: launch the server as a Python subprocess
SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,   # current Python interpreter
    args=[SERVER_PATH],
    env=None
)


@asynccontextmanager
async def mcp_session():
    """Context manager — opens an MCP session to our server."""
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def _call_tool(tool_name: str, arguments: dict) -> dict:
    async with mcp_session() as session:
        result = await session.call_tool(tool_name, arguments=arguments)
        # Result content is a list of TextContent / etc.
        if result.content:
            import json
            try:
                return json.loads(result.content[0].text)
            except (json.JSONDecodeError, AttributeError):
                return {"success": False, "error": "Could not parse MCP response"}
        return {"success": False, "error": "No content returned"}


# --- Synchronous wrappers for use in Streamlit / orchestrator ---
def send_email_via_mcp(to: str, subject: str, body: str) -> dict:
    return asyncio.run(_call_tool("send_email", {
        "to": to, "subject": subject, "body": body
    }))


def create_event_via_mcp(
    title: str, description: str,
    start: str, end: str, attendees: list
) -> dict:
    return asyncio.run(_call_tool("create_calendar_event", {
        "title": title,
        "description": description,
        "start": start,
        "end": end,
        "attendees": attendees
    }))


# --- List available tools (для демо: можно показать что MCP реально подключен) ---
async def _list_tools():
    async with mcp_session() as session:
        tools = await session.list_tools()
        return [{"name": t.name, "description": t.description} for t in tools.tools]


def list_mcp_tools() -> list:
    return asyncio.run(_list_tools())