"""E2E Test configuration and fixtures simulating Hermes Agent."""

import json
import os
import tempfile
from typing import AsyncGenerator

import httpx2
import pytest
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from peewee import SqliteDatabase

from src.db.models import ALL_MODELS, db as global_db
from src.mcp.server import create_server


@pytest.fixture
def anyio_backend():
    """Default anyio backend to asyncio."""
    return "asyncio"


@pytest.fixture
def e2e_db():
    """Provide a dedicated isolated SQLite database file for E2E tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    test_db = SqliteDatabase(db_path)
    test_db.connect()

    original_db = global_db
    for model in ALL_MODELS:
        model._meta.database = test_db

    test_db.create_tables(ALL_MODELS)

    yield test_db

    test_db.close()
    for model in ALL_MODELS:
        model._meta.database = original_db

    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except OSError:
            pass


class HermesTestClient:
    """Helper wrapper around ClientSession simulating Hermes Agent tool execution."""

    def __init__(self, session: ClientSession):
        self.session = session

    async def list_tool_names(self) -> set[str]:
        result = await self.session.list_tools()
        return {tool.name for tool in result.tools}

    async def list_tools(self):
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, /, **arguments) -> dict:
        result = await self.session.call_tool(tool_name, arguments=arguments)
        if not result.content:
            return {}
        first = result.content[0]
        text = first.text if hasattr(first, "text") else str(first)
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return {"status": "error", "code": "protocol_error", "message": text}


@pytest.fixture
async def hermes_client(e2e_db) -> AsyncGenerator[HermesTestClient, None]:
    """Provide a connected, initialized HermesTestClient over streamable-http."""
    server = create_server()
    app = server.streamable_http_app()

    async with app.router.lifespan_context(app):
        transport = httpx2.ASGITransport(app=app)
        async with httpx2.AsyncClient(
            transport=transport, base_url="http://localhost:9700"
        ) as http_client:
            async with streamable_http_client(
                "http://localhost:9700/mcp", http_client=http_client
            ) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    await session.initialize()
                    yield HermesTestClient(session)
