# Workflow Handoff: agent-zero-lite

> **Session**: 2026-04-02T04:12:40Z
> **Agent**: GPT-5 Codex
> **Handoff Reason**: checkpoint

---

## Ξ State Vector

**Objective**: Finish the lite migration by replacing SearXNG with a builtin `_web_search` model-backed path and removing the old search-daemon build/runtime surface.

**Phase**: Migration closeout | Progress: 95% | Status: paused

**Current Focus**:
The search stack has been re-anchored on a builtin `_web_search` plugin that supplies a browser-model seam, and `search_engine` now calls that model instead of localhost SearXNG. The Docker build/runtime layers were stripped of SearXNG install and supervisor references, and the lite docs now describe builtin API-backed web search. Current work is effectively handoff/verification rather than feature design.

**Blocker**: none
- Resolution path: n/a

---

## Δ Context Frame

### Decisions Log
| ID | Decision | Rationale | Reversible |
|----|----------|-----------|------------|
| D1 | `_web_search` is a builtin plugin with an `Agent.get_browser_model()` interception point. | `Agent` already exposes a hookable browser-model getter, and implicit function extensions keep the seam aligned with existing `_model_config` patterns. | yes |
| D2 | `search_engine` should use a model-backed browser call, not a localhost HTTP service. | Keeps the live-search path inside the same provider/config machinery used by the rest of the app. | yes |
| D3 | The base image should stay on fuller Debian `python:3.12-bookworm`. | The lite fork no longer needs the SearXNG install step, so a broader userland is acceptable while preserving the shared `/opt/venv` contract. | yes |
| D4 | SearXNG install/runtime files should be removed rather than left as dead build-time artifacts. | Avoids stale build scripts, supervisor stanzas, and runtime assets that would otherwise drift from the new design. | yes |

### Constraints Active
- Preserve the optional-dependency contract validated by `tests/test_lite_optional_dependencies.py:1-79`.
- Keep plugin resolution inside the standard plugin config flow via `helpers.plugins.get_plugin_config()` and `get_default_plugin_config()`.
- Do not reintroduce SearXNG through Docker, supervisor, helper modules, or tool imports.
- Maintain actionable errors and lazy optional imports in `models.py` and the speech runtimes.

### Patterns In Use
- **Implicit function extension**: `@extensible` maps framework methods to `_functions/<module>/<qualname>/<start|end>` hooks → See [`helpers/extension.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/helpers/extension.py#L51)
- **Model getter interception**: `Agent.get_chat_model()`, `get_utility_model()`, `get_browser_model()`, and `get_embedding_model()` are plugin-extensible seams → See [`agent.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/agent.py#L711)
- **Provider/default merge seam**: provider ids are normalized before LiteLLM wrapper construction → See [`models.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/models.py#L774)
- **Builtin plugin config**: plugin defaults load from `default_config.yaml` when no scoped config exists → See [`helpers/plugins.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/helpers/plugins.py#L583)

### Mental Models Required
Provider indirection
: UI-facing provider ids are normalized to LiteLLM provider names plus default kwargs before model construction.

Browser-model seam
: `_web_search` owns the model that `search_engine` uses; this is a capability seam, not a new public tool API.

Runtime cleanup
: Removing SearXNG means deleting both install-time and runtime touchpoints, not just changing one Python helper.

---

## Φ Code Map

### Modified This Session
| File | Lines | Change Summary |
|------|-------|----------------|
| `plugins/_web_search/plugin.yaml` | 1-9 | New builtin plugin manifest for search capability. |
| `plugins/_web_search/default_config.yaml` | 1-10 | Default browser-model config set to OpenRouter `perplexity/sonar-pro-search`. |
| `plugins/_web_search/helpers/web_search.py` | 1-82 | Config merge helper, API-key helper, browser-model builder, and search prompt assembly. |
| `plugins/_web_search/extensions/python/_functions/agent/Agent/get_browser_model/start/_10_web_search.py` | 1-8 | Plugin intercepts `Agent.get_browser_model()` and returns the built browser model. |
| `tools/search_engine.py` | 1-31 | Tool now calls `agent.get_browser_model().unified_call()` and no longer imports SearXNG. |
| `docker/base/Dockerfile` | 1-34 | Fuller Debian base kept; SearXNG install step removed. |
| `docker/run/Dockerfile` | 1-36 | Removed SearXNG chmod/cleanup path from the run image. |
| `DockerfileLocal` | 1-36 | Removed SearXNG chmod/cleanup path from the local image. |
| `docker/run/fs/etc/supervisor/conf.d/supervisord.conf` | 1-80 | Supervisor now has no SearXNG program stanza. |
| `docker/run/fs/ins/install_additional.sh` | 1-4 | Removed stale SearXNG install comment. |
| `README.md` | 102-107 | Lite profile text now describes builtin API-backed web search. |
| `tests/test_web_search_tool.py` | 1-67 | Regression coverage for browser-model seam and source import cleanup. |
| `docker/base/fs/ins/install_searxng.sh` | entire file | Deleted. |
| `docker/base/fs/ins/install_searxng2.sh` | entire file | Deleted. |
| `docker/base/fs/etc/searxng/*` | entire tree | Deleted. |
| `docker/run/fs/etc/searxng/*` | entire tree | Deleted. |
| `docker/run/fs/exe/run_searxng.sh` | entire file | Deleted. |
| `helpers/searxng.py` | entire file | Deleted. |
| `tools/knowledge_tool._py` | entire file | Deleted stale SearXNG snapshot. |

### Reference Anchors
| File | Lines | Relevance |
|------|-------|-----------|
| `helpers/extension.py` | 51-99, 162-204 | Explains implicit extension short-circuit behavior and sync/async execution. |
| `agent.py` | 711-724 | Existing model getter hooks, now including browser model. |
| `models.py` | 201-209, 656-657, 774-836 | Lazy optional dependency loader and provider/default merge path. |
| `helpers/providers.py` | 63-142 | Provider metadata loading and lookup. |
| `plugins/_model_config/helpers/model_config.py` | 94-198 | Current chat/utility/embedding build path that `_web_search` mirrors conceptually. |
| `plugins/README.md` | 20-32, 62-71 | Builtin plugin layout and runtime-hook conventions. |
| `docs/developer/plugins.md` | 22-81, 145-175 | Manifest and extension-layout rules for builtin plugins. |

### Entry Points
- **Primary**: [`tools/search_engine.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/tools/search_engine.py#L1) — current live search execution path.
- **Primary**: [`plugins/_web_search/helpers/web_search.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/plugins/_web_search/helpers/web_search.py#L1) — browser-model config and prompt assembly.
- **Primary**: [`agent.py:711-724`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/agent.py#L711) — browser-model interception seam.
- **Test Suite**: [`tests/test_web_search_tool.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/tests/test_web_search_tool.py#L1) and [`tests/test_lite_optional_dependencies.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/tests/test_lite_optional_dependencies.py#L1).

---

## Ψ Knowledge Prerequisites

### Documentation Sections
- [ ] [`plugins/README.md`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/plugins/README.md) § What a Plugin Can Provide — builtin plugin structure and implicit hook layouts.
- [ ] [`plugins/README.md`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/plugins/README.md) § Runtime Hooks (`hooks.py`) — runtime-local config behavior and environment expectations.
- [ ] [`docs/developer/plugins.md`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/docs/developer/plugins.md) § Manifest and Python extension layouts — needed if `_web_search` gains UI/config polish.

### Modules to Explore
- [ ] [`plugins/_web_search/helpers/web_search.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/plugins/_web_search/helpers/web_search.py) — search config defaults and prompt shape.
- [ ] [`plugins/_model_config/helpers/model_config.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/plugins/_model_config/helpers/model_config.py) — reuse model-config conventions for any future search UI integration.
- [ ] [`tools/search_engine.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/tools/search_engine.py) — verify formatting/output expectations before any future prompt refinement.

---

## Ω Forward Vector

### Next Actions *(priority order)*
1. **Review**: Decide whether the remaining `. _py` tool snapshots should be deleted or renamed into active `.py` files if they are still intended to run.
2. **Polish**: If needed, refine `_web_search` output formatting or config UI to surface the browser-model choice more clearly → [`plugins/_web_search/helpers/web_search.py`](C:/Users/3CLYP50/Documents/GitHub/agent-zero-lite/plugins/_web_search/helpers/web_search.py#L1)
3. **Verify**: Run a wider test pass or image build check if the next session is meant to finalize the migration.

### Open Questions
- [ ] Should `_web_search` expose additional user-facing config, or remain a minimal builtin default?
- [ ] Do any other tool snapshots still need cleanup after the SearXNG deletion sweep?

### Success Criteria
- [ ] No active SearXNG install/runtime references remain in the lite path.
- [ ] `search_engine` resolves through the `_web_search` browser-model seam.
- [ ] Default optional-dependency regression tests still pass.

### Hazards / Watch Points
- ⚠️ Any future change to provider defaults must preserve the plugin config merge path, or UI/runtime drift will reappear.
- ⚠️ If the remaining `._py` snapshots are still intentional, deleting them would remove dormant behavior; verify before further cleanup.

---

## Glossary *(session-specific terms)*
| Term | Definition |
|------|------------|
| `_web_search` | Builtin plugin that owns the browser-model seam for live web search. |
| Browser-model seam | `Agent.get_browser_model()` interception point used by `search_engine`. |
| Provider indirection | Translation from config-facing provider ids to LiteLLM provider names/defaults. |
| SearXNG removal sweep | Deleting install scripts, runtime assets, helper client, and supervisor/build references. |
