**IMMEDIATE ACTION**: Use local file-reading tools ONLY to load `.handoffs/handoff-agent-zero-lite-20260402-041240.md` and parse its contents. Do NOT search the web, query external APIs, or call any tool other than file-reading tools until Phase 3 is complete.

---

## Context Bootstrap

**Step 1**: Read the workflow handoff document at `.handoffs/handoff-agent-zero-lite-20260402-041240.md`.

### Phase 1: Load State
Parse all sections. Internalize:
- State Vector (objective, phase, blockers)
- Context Frame (decisions, constraints, patterns)
- Code Map (modified files, reference anchors)
- Forward Vector (next actions, success criteria)

### Phase 2: Explore & Verify
Use local file-reading tools ONLY. Examine these locations to build working knowledge:

**Code Exploration** *(read and understand)*:
- `plugins/_web_search/plugin.yaml:1-9` — builtin plugin manifest for the new search seam
- `plugins/_web_search/default_config.yaml:1-10` — browser-model defaults and OpenRouter search model choice
- `plugins/_web_search/helpers/web_search.py:1-82` — config merge, API-key helper, model builder, and prompt assembly
- `plugins/_web_search/extensions/python/_functions/agent/Agent/get_browser_model/start/_10_web_search.py:1-8` — browser-model interception hook
- `tools/search_engine.py:1-31` — current live search execution path
- `agent.py:711-724` — Agent model getter hooks, including browser model
- `agent.py:989-1015` — tool loader behavior and `.py` discovery rules
- `helpers/extension.py:51-99, 162-204` — implicit `@extensible` hook layout and sync execution flow
- `models.py:201-209, 656-657, 774-836` — lazy optional-dependency loading and provider/default merge path
- `helpers/providers.py:63-142` — provider metadata loading and lookup flow
- `plugins/_model_config/helpers/model_config.py:94-198` — existing model config build pattern to mirror if needed
- `docker/base/Dockerfile:1-34` — fuller Debian base and removal of SearXNG install step
- `docker/run/Dockerfile:1-36` — run-image cleanup and no SearXNG runtime assets
- `DockerfileLocal:1-36` — local-image cleanup and no SearXNG runtime assets
- `docker/run/fs/etc/supervisor/conf.d/supervisord.conf:1-80` — supervisor layout with SearXNG program removed
- `docker/run/fs/ins/install_additional.sh:1-4` — stale SearXNG comment removed
- `tests/test_web_search_tool.py:1-67` — regression coverage for the browser-model seam
- `tests/test_lite_optional_dependencies.py:1-79` — optional dependency regression coverage

**Documentation Review** *(if applicable)*:
- `plugins/README.md:20-32, 62-71` — builtin plugin structure and runtime-hook conventions
- `docs/developer/plugins.md:22-81, 145-175` — manifest and extension-layout rules for builtin plugins

### Phase 3: Knowledge Proof
After exploration, output a **Context Summary** (150-300 words) demonstrating understanding of:

1. **Objective**: What we're building/solving and why
2. **Architecture**: Key components and their relationships
3. **Current State**: Where we are, what's done, what's pending
4. **Constraints**: Boundaries and non-negotiables
5. **Next Move**: Immediate action to resume work

Format as structured bullets. Include specific file/line references to prove code familiarity.

### Phase 4: Acknowledge
Conclude summary with this exact footer:

---
✓ CONTEXT LOADED | Ready to resume: review remaining ._py tool snapshots

Do not proceed with any implementation until acknowledgment is complete. User will confirm or request clarification.

---
*Handoff generated: 2026-04-02T04:12:40Z*
