"""Synchronous bridge for calling the banking MCP servers from agents."""

import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from identity.authorization import authorize_tool


async def _call_tool(server_module: str, tool_name: str, arguments: dict[str, Any]) -> dict:
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module],
    )
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)

    if result.isError:
        raise RuntimeError(f"MCP tool {tool_name!r} returned an error")
    if result.structuredContent:
        return result.structuredContent
    for content in result.content:
        if getattr(content, "type", None) == "text":
            return json.loads(content.text)
    raise RuntimeError(f"MCP tool {tool_name!r} returned no structured result")


def call_mcp_tool(server_module: str, tool_name: str, arguments: dict[str, Any]) -> dict:
    """Call one MCP tool synchronously from a Gemini function tool."""
    authorize_tool(tool_name)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_call_tool(server_module, tool_name, arguments))

    # Specialist agents can be called from FastAPI's running event loop.
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(
            asyncio.run,
            _call_tool(server_module, tool_name, arguments),
        ).result()