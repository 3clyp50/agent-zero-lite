from __future__ import annotations

from copy import deepcopy
from typing import Any

import models
from helpers import plugins
from plugins._model_config.helpers.model_config import build_model_config

PLUGIN_NAME = "_web_search"
CONFIG_SECTION = "browser_model"
LOCAL_PROVIDERS = {"ollama", "lm_studio"}
SEARCH_ENGINE_RESULTS = 10

SEARCH_SYSTEM_PROMPT = """You are Agent Zero's live web search backend.
Use current web sources and return only the most relevant results.

Output format:
1. Title
   URL: https://...
   Summary: one concise sentence

Rules:
- Return at most {max_results} results.
- Prefer authoritative and recent sources.
- Do not include reasoning, preambles, or markdown fences.
- If no useful live sources are found, say so briefly.
"""


def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def get_config(agent=None) -> dict[str, Any]:
    defaults = plugins.get_default_plugin_config(PLUGIN_NAME) or {}
    current = plugins.get_plugin_config(PLUGIN_NAME, agent=agent) or {}
    return _merge_dicts(defaults, current) if isinstance(defaults, dict) and isinstance(current, dict) else current or defaults


def get_browser_model_config(agent=None) -> dict[str, Any]:
    cfg = get_config(agent)
    section = cfg.get(CONFIG_SECTION, {}) if isinstance(cfg, dict) else {}
    if not isinstance(section, dict):
        section = {}

    defaults = plugins.get_default_plugin_config(PLUGIN_NAME) or {}
    default_section = defaults.get(CONFIG_SECTION, {}) if isinstance(defaults, dict) else {}
    if isinstance(default_section, dict):
        return _merge_dicts(default_section, section)
    return section


def has_provider_api_key(provider: str, configured_api_key: str = "") -> bool:
    configured_value = (configured_api_key or "").strip()
    if configured_value and configured_value != "None":
        return True

    provider_lower = provider.lower()
    if provider_lower in LOCAL_PROVIDERS:
        return True

    api_key = models.get_api_key(provider_lower)
    return bool(api_key and api_key.strip() and api_key != "None")


def build_browser_model(agent=None):
    cfg = get_browser_model_config(agent)
    mc = build_model_config(cfg, models.ModelType.CHAT)
    return models.get_chat_model(mc.provider, mc.name, model_config=mc, **mc.build_kwargs())


def build_search_messages(query: str, max_results: int = SEARCH_ENGINE_RESULTS) -> tuple[str, str]:
    system_message = SEARCH_SYSTEM_PROMPT.format(max_results=max_results)
    user_message = query.strip()
    return system_message, user_message
