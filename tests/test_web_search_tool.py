from __future__ import annotations

import ast
import asyncio
from pathlib import Path

from tools.search_engine import SearchEngine


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DummyBrowserModel:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def unified_call(self, **kwargs):
        self.calls.append(kwargs)
        return (
            "1. Example result\n   URL: https://example.com\n   Summary: Example source.",
            "",
        )


class DummyAgent:
    def __init__(self, browser_model) -> None:
        self.browser_model = browser_model
        self.interventions: list[str] = []

    def get_browser_model(self):
        return self.browser_model

    async def handle_intervention(self, message):
        self.interventions.append(message)


def _imported_modules(source: str) -> set[str]:
    parsed = ast.parse(source)
    modules: set[str] = set()
    for node in parsed.body:
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_search_engine_uses_browser_model_seam_and_formats_result() -> None:
    model = DummyBrowserModel()
    agent = DummyAgent(model)
    tool = SearchEngine(agent, "search_engine", None, {}, "", None)

    response = asyncio.run(tool.execute(query="agent zero web search"))

    assert response.message.startswith("1. Example result")
    assert agent.interventions == [response.message]
    assert model.calls[0]["user_message"] == "agent zero web search"
    assert "live web search backend" in model.calls[0]["system_message"]


def test_search_engine_source_no_longer_imports_searxng() -> None:
    source = (PROJECT_ROOT / "tools/search_engine.py").read_text(encoding="utf-8")
    imported = _imported_modules(source)

    assert "helpers.searxng" not in imported
    assert "helpers.duckduckgo_search" not in imported
    assert "helpers.perplexity_search" not in imported
