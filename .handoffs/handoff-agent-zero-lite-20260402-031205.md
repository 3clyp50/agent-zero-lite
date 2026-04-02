# Workflow Handoff: agent-zero-lite

> **Session**: 2026-04-02T03:12:05Z
> **Agent**: GPT-5 Codex
> **Handoff Reason**: limit

---

## Ξ State Vector

**Objective**: Resume `agent-zero-lite` from the completed dependency-slimming pass and implement two next-phase changes: remove SearXNG in favor of a builtin `_web_search` API-search provider/model path, and replace the slim Python base with a fuller Debian Linux base.

**Phase**: Pre-implementation handoff | Progress: 58% | Status: paused

**Current Focus**:
The lite fork already split optional heavy dependencies out of the default install, moved Docker runtime setup onto a shared `/opt/venv`, and switched default embeddings away from local HuggingFace. The next session should treat SearXNG removal and fuller-base adoption as one connected systems pass, because search, supervisor/runtime launch, and base-image package assumptions still point at the old local-daemon design.

**Blocker**:
- `_web_search` does not exist yet, and the exact seam is still a design choice: either intercept agent model getters via plugin extensions or add a dedicated model wrapper path in `models.py` that still respects provider/default config merging.
- Resolution path: start by reading the existing model-config plugin interception pattern and the current SearXNG call chain, then decide whether `_web_search` should own a chat-model-like wrapper, a utility-model-like wrapper, or a dedicated tool-facing adapter.

---

## Δ Context Frame

### Decisions Log
| ID | Decision | Rationale | Reversible |
|----|----------|-----------|------------|
| D1 | Lite runtime now uses a shared `/opt/venv` instead of pyenv plus multiple venvs. | Simplifies Docker build/runtime, cuts moving parts, and made optional dependency splitting possible. | yes |
| D2 | Voice/STT and local-embedding stacks were removed from default install and split into opt-in requirements files. | Default lite startup should not require `kokoro`, `whisper`, `soundfile`, or `sentence-transformers`. | yes |
| D3 | Default embedding model moved from local HuggingFace to OpenRouter `openai/text-embedding-3-small`. | Avoids mandatory local embedding runtime and keeps memory/embedding features available in the lite fork. | yes |
| D4 | Next search replacement should be plugin-driven and model-backed, not another local daemon or tool-specific branch. | The current SearXNG path is spread across Docker, supervisor, helper, and tool layers; a builtin plugin/provider route is cleaner and consistent with existing model interception patterns. | yes |
| D5 | Upcoming base-image change should target fuller Debian userland, not just another slim Python variant. | Search-daemon removal reduces image-specific coupling; the next pass can afford a more complete Linux base without carrying Kali-era assumptions. | yes |

### Constraints Active
- Preserve the optional-dependency contract: default install must continue to work without `requirements.voice.txt` and `requirements.local-embeddings.txt`.
- Do not regress the lazy-import and actionable-error behavior in `models.py`, `preload.py`, and the speech runtimes.
- `_web_search` should default to OpenRouter with `perplexity/sonar-pro-search`, but the provider/model path should still flow through existing config/default machinery where possible.
- SearXNG removal is cross-layer: Python helper/tool code, supervisor programs, runtime scripts, Docker build steps, and image exposure assumptions all need to be cleaned up together.
- The next base image should be Debian and "full" enough for a normal Linux userland; re-evaluate any `slim` assumptions before keeping current package scripts unchanged.

### Patterns In Use
- **Implicit function extensions**: `@extensible` generates `_functions/<module>/<qualname>/<start|end>` hook points for plugins to intercept framework methods -> See `helpers/extension.py:51-99`
- **Model-provider interception via builtin plugin**: `_model_config` already injects chat, utility, and embedding model resolution through Agent method hooks -> See `agent.py:711-724`
- **Provider default merging**: provider ids/config are normalized before model construction, which is the cleanest place to graft a search-capable handler -> See `models.py:774-836`
- **Shared runtime environment**: base and run images now assume `/opt/venv` is the single runtime Python env -> See `docker/base/fs/ins/install_python.sh:8-20`

### Mental Models Required
Provider indirection
: UI/config provider ids are not the final LiteLLM provider names; `helpers/providers.py` and `models._merge_provider_defaults()` can translate ids and inject defaults.

Model getter interception
: `Agent.get_chat_model()`, `get_utility_model()`, and `get_embedding_model()` intentionally return `None` until plugins replace them through implicit extension hooks.

Search as model capability
: The target design is to treat web search as a model-backed capability owned by a builtin plugin, not as a localhost web service hidden behind `tools/search_engine.py`.

Base/run image contract
: The base image owns OS packages and `/opt/venv`; the run image mostly layers repo install, preload, supervisor, and startup scripts on top.

---

## Φ Code Map

### Modified This Session
| File | Lines | Change Summary |
|------|-------|----------------|
| `docker/base/Dockerfile` | 1-2 | Base image changed from Kali rolling to `python:3.12-slim-bookworm`. |
| `docker/base/fs/ins/install_python.sh` | 6-20 | Replaced global Python/pyenv flow with shared `/opt/venv` bootstrap plus `uv` install. |
| `docker/base/fs/ins/install_searxng.sh` | 12-25 | Kept SearXNG creation but stopped using a dedicated user shell bootstrap; now invokes shared-venv installer directly. |
| `docker/base/fs/ins/install_searxng2.sh` | 10-29 | Moved SearXNG installation onto `/opt/venv` and removed dedicated SearXNG venv setup. |
| `docker/run/fs/ins/install_A0.sh` | 14-43 | Switched runtime repo path/clone target to `agent-zero-lite`, removed Playwright install, kept preload on lite repo. |
| `docker/run/fs/ins/setup_venv.sh` | 12-12 | Runtime activation now always sources `/opt/venv`. |
| `models.py` | 201-209, 656-657 | Added lazy `sentence_transformers` loader with actionable install error. |
| `plugins/_model_config/default_config.yaml` | 27-33 | Default embedding provider changed to OpenRouter `openai/text-embedding-3-small`. |
| `plugins/_whisper_stt/helpers/runtime.py` | 32-35, 99-112, 138-140 | Whisper imports are lazy and fail with voice-extra guidance. |
| `plugins/_kokoro_tts/helpers/runtime.py` | 28-32, 69-91, 115-116, 168-170 | Kokoro and `soundfile` imports are lazy and fail with voice-extra guidance. |
| `preload.py` | 7-16, 23-24, 48-49 | Speech runtime imports moved behind getter functions so default preload does not import optional extras. |
| `requirements.txt` | 1-50 | Removed browser-use, voice, and local-embedding packages from the default dependency set. |
| `requirements.voice.txt` | 1-3 | New opt-in voice dependency group for Kokoro, Whisper, and `soundfile`. |
| `requirements.local-embeddings.txt` | 1-3 | New opt-in local-embedding dependency group for sentence-transformers CPU usage. |
| `tests/test_lite_optional_dependencies.py` | 1-79 | Added regression coverage for lazy optional imports and actionable dependency errors. |

### Reference Anchors
| File | Lines | Relevance |
|------|-------|-----------|
| `agent.py` | 711-724 | Existing extensible model getter hooks that a builtin `_web_search` plugin can mirror or extend. |
| `helpers/extension.py` | 51-99 | Defines implicit `@extensible` hook layout and short-circuit semantics. |
| `helpers/extension.py` | 162-204, 282-307 | Shows how sync extension calls execute and how extension classes are discovered and merged. |
| `plugins/_model_config/extensions/python/_functions/agent/Agent/get_chat_model/start/_10_model_config.py` | 1-8 | Minimal precedent for replacing an Agent model getter through a builtin plugin. |
| `plugins/_model_config/extensions/python/_functions/agent/Agent/get_utility_model/start/_10_model_config.py` | 1-8 | Utility-model interception pattern. |
| `plugins/_model_config/extensions/python/_functions/agent/Agent/get_embedding_model/start/_10_model_config.py` | 1-8 | Embedding-model interception pattern. |
| `plugins/README.md` | 20-32 | Documents builtin plugin structure and implicit `_functions/...` extension layout. |
| `plugins/README.md` | 62-71 | Documents `hooks.py` as runtime-internal plugin behavior living in the shared `/opt/venv`. |
| `helpers/providers.py` | 63-106, 116-142 | Provider config loading, lookup, and reload path used by model config. |
| `plugins/_model_config/helpers/model_config.py` | 117-198 | Embedding model config/build path; likely template for a search-capable model selection flow. |
| `plugins/_model_config/helpers/model_config.py` | 217-249 | API-key missing-provider checks; relevant if `_web_search` adds a new provider id. |
| `tools/search_engine.py` | 12-38 | Current tool entry point still hard-wired to SearXNG helper. |
| `helpers/searxng.py` | 1-12 | Current localhost SearXNG HTTP client to delete or replace. |
| `docker/run/fs/etc/supervisor/conf.d/supervisord.conf` | 46-59 | Supervisor still launches `run_searxng`; removal surface. |
| `docker/run/fs/exe/run_searxng.sh` | 1-10 | Runtime script still starts the SearXNG webapp from `/opt/venv`. |
| `docker/run/Dockerfile` | 30-36 | Run image still grants execute perms for `run_searxng.sh` and inherits current base image tag. |
| `docker/run/docker-compose.yml` | 1-8 | Lite runtime compose entry; useful when validating any port/runtime behavior changes. |
| `docker/base/Dockerfile` | 27-31 | Base image still installs SearXNG during build, so search removal must touch base build too. |

### Entry Points
- **Primary**: `tools/search_engine.py:12` — current web-search tool execution path that still delegates to SearXNG.
- **Primary**: `models.py:774` — current provider/default merge seam; likely one of the cleanest places to add `_web_search` behavior.
- **Primary**: `helpers/extension.py:51` — implicit extension system used by builtin plugins to intercept framework functions.
- **Test Suite**: `tests/test_lite_optional_dependencies.py` — covers default-install optional-dependency guarantees.

---

## Ψ Knowledge Prerequisites

### Documentation Sections
- [ ] `plugins/README.md` § What a Plugin Can Provide — builtin plugin layout, implicit hook directories, and runtime hook conventions.
- [ ] `plugins/README.md` § Runtime Hooks (`hooks.py`) — how plugin-owned runtime behavior executes inside the shared `/opt/venv`.
- [ ] `docs/developer/plugins.md` § extension points and manifests — broader plugin authoring rules if `_web_search` becomes a permanent builtin plugin.

### Modules to Explore
- [ ] `models.py` — understand provider default merging, wrapper construction, and where a search-capable handler could slot in cleanly.
- [ ] `agent.py:711-724` — understand the Agent model getter hooks already intercepted by `_model_config`.
- [ ] `helpers/providers.py` — understand provider metadata merge and reload behavior before adding a new provider id or default.
- [ ] `tools/search_engine.py:12-38` and `helpers/searxng.py:1-12` — trace the full current search path before deleting SearXNG.
- [ ] `docker/base/Dockerfile:27-31`, `docker/run/fs/etc/supervisor/conf.d/supervisord.conf:46-59`, and `docker/run/fs/exe/run_searxng.sh:1-10` — enumerate all remaining SearXNG build and runtime touchpoints.

---

## Ω Forward Vector

### Next Actions *(priority order)*
1. **Design**: Decide the `_web_search` plugin contract and interception seam using `helpers/extension.py:51-99`, `agent.py:711-724`, and `models.py:774-836`.
2. **Implement**: Add builtin `_web_search` plugin files plus model-handler logic that defaults to OpenRouter `perplexity/sonar-pro-search` and route `tools/search_engine.py:12-38` away from `helpers/searxng.py:1-12`.
3. **Remove**: Delete the SearXNG runtime and build surface from `docker/base/Dockerfile:27-31`, `docker/run/fs/etc/supervisor/conf.d/supervisord.conf:46-59`, `docker/run/fs/exe/run_searxng.sh:1-10`, and any remaining helper or install scripts.
4. **Rebase**: Replace `python:3.12-slim-bookworm` with a fuller Debian base and reconcile Python provisioning plus `/opt/venv` bootstrap in `docker/base/Dockerfile:1-31` and `docker/base/fs/ins/install_python.sh:6-20`.
5. **Verify**: Add or update tests so the lite default install still passes without optional extras and search no longer depends on localhost SearXNG.

### Open Questions
- [ ] Should `_web_search` be expressed as a new provider id in `_model_config`, a utility-model override path, or a tool-owned wrapper that still uses `models.get_chat_model()` internally?
- [ ] Should the fuller Debian base install Python from Debian packages or bootstrap upstream Python 3.12 again?
- [ ] How should `tools/search_engine.py` format results if the new search backend returns LLM-authored text instead of SearXNG-style JSON result items?
- [ ] Does `_web_search` need its own API-key semantics, or should it piggyback entirely on existing OpenRouter provider config and validation?

### Success Criteria
- [ ] No SearXNG files, processes, or install steps remain in the lite build/runtime path.
- [ ] Search uses a builtin `_web_search` flow and defaults to OpenRouter `perplexity/sonar-pro-search`.
- [ ] Default install still passes optional-dependency coverage without `requirements.voice.txt` or `requirements.local-embeddings.txt`.
- [ ] Docker base runs on fuller Debian with a working shared `/opt/venv` and no lost Linux-userland expectations.
- [ ] Model/provider config remains coherent in UI, runtime, and API-key validation after the search integration lands.

### Hazards / Watch Points
- ⚠️ If `_web_search` bypasses existing provider/default merging, config UI and API-key validation will drift from actual runtime behavior.
- ⚠️ Removing SearXNG from Python but not from supervisor or Docker scripts will leave dead startup failures behind.
- ⚠️ Moving from the slim Python image to fuller Debian may reintroduce Python bootstrap complexity already removed in D1 unless the provisioning path is chosen deliberately.

---

## Glossary *(session-specific terms)*
| Term | Definition |
|------|------------|
| Shared runtime venv | The single `/opt/venv` Python environment now used by both base-image installs and run-image startup. |
| Implicit function extension | The `@extensible` plugin mechanism that maps framework methods to `_functions/<module>/<qualname>/<start|end>/` folders. |
| Provider indirection | The layer where config-facing provider ids are normalized and expanded into LiteLLM provider names plus default kwargs. |
| `_web_search` | Planned builtin plugin that should replace SearXNG with an API-backed search/model path. |
| Fuller Debian | The next desired base-image target: Debian with a more complete Linux userland than the current slim Python image. |
