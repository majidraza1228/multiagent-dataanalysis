# multiagent-dataanalysis — Codex Agent Instructions

This file is read at the start of every Codex session for this project.
All agents spawned in this project should follow the rules below.

---

## Agent Routing

Before spawning any agent, classify the task and assign a Codex execution profile.
Never spawn an agent without explicitly setting its profile.

### Step 1 — Classify the task

Read the task description and score it against these signals:

**High-reasoning signals** (complex, high judgment, costly if wrong):
- Designing or choosing a model architecture
- Evaluating, grading, or scoring outputs
- Debugging non-obvious failures
- Making trade-offs between approaches
- Any decision where a wrong choice requires significant rework
- Comparing multiple strategies and picking one

**Fast-execution signals** (mechanical, well-defined, low judgment):
- Writing config files (`requirements.txt`, `.gitignore`, `Makefile`, `.mcp.json`)
- Scaffolding folder structures or placeholder files
- Boilerplate endpoints, routers, schemas
- File I/O, logging setup, JSONL reading/writing
- Anything where the output is fully specified in advance

**Balanced signals** (moderate, general coding):
- Feature implementation that requires reading existing code
- Test writing
- Refactoring with clear instructions
- Anything that doesn't clearly fit high-reasoning or fast-execution

### Step 2 — Assign the profile

| Classification | Codex profile | When |
|---|---|---|
| High complexity / judgment | `high` | Architecture, grading, debugging, trade-offs |
| Low complexity / mechanical | `fast` | Scaffolding, config, boilerplate, file I/O |
| Moderate / general coding | `balanced` | Default for everything else |

### Step 3 — State your reasoning before spawning

Before every agent spawn, output a one-line classification like this:

```
[ROUTING] Task: "analyze multi-sheet workbook quality and log MLflow artifacts"
          Signals: workbook heuristics, scoring strategy, MLflow design
          Codex profile: high
```

Then spawn the agent with the selected Codex profile.

### Step 4 — Apply the cheapest profile that can do the job

If a task has mixed signals, split it:
- Give the judgment-heavy part to a `high` agent
- Give the mechanical part to a `fast` agent
- Use `balanced` for general implementation work

---

## Agent Spawning Rules

1. **Always load relevant project playbooks** from `.codex/skills/` before writing the agent prompt. Include only the files needed for the task.
2. **Define file ownership** per agent. No two agents should write to the same file. If a handoff is needed, use a comment placeholder and wire it in post-merge.
3. **Run agents in parallel** when their file ownership is non-overlapping. Never run sequentially if tasks are independent.
4. **Checkpoint after every agent** by updating `.agent_memory/session.json` with `last_completed`, `agents_done`, and `next`.
5. **Always run the grader** (`python grader.py`) after merging agent outputs. Spawn a targeted fix agent for any stage scoring below 6. Use `fast` for fix agents unless the fix requires judgment.

---

## Session Resume

On session start, read `.agent_memory/session.json` first.
If `agents_done` is non-empty, skip completed stages and resume from `next`.

---

## Available Project Playbooks

Load these before writing agent prompts for the relevant task:

| Playbook | Use for |
|---|---|
| `.codex/skills/pytorch-model/` | Workbook analysis engine, quality scoring |
| `.codex/skills/mlflow-tracking/` | Experiment tracking, profile artifacts |
| `.codex/skills/fastapi-backend/` | API endpoints, workbook analysis |
| `.codex/skills/gradio-frontend/` | Gradio UI, workbook summary |
| `.codex/skills/jsonl-monitor/` | Analysis logging, drift detection |
| `.codex/skills/project-scaffold/` | `requirements.txt`, `Makefile`, `.gitignore` |
| `.codex/skills/openai-mcp/` | OpenAI chat, vision, embeddings via MCP |
| `.codex/skills/git-worktree-parallel/` | Worktree-based multi-agent execution |

---

## Routing Quick Reference

```
Task involves...                          → Codex profile
────────────────────────────────────────────────────────
Workbook analysis heuristics              → high
MLflow experiment design                  → high
Grading / scoring / evaluating            → high
Debugging a non-obvious failure           → high
────────────────────────────────────────────────────────
FastAPI endpoints / routers               → fast
Gradio UI scaffold                        → fast
requirements.txt / Makefile / .gitignore  → fast
JSONL logging / file I/O                  → fast
Placeholder / scaffold files              → fast
────────────────────────────────────────────────────────
Test writing                              → balanced
Refactoring with clear instructions       → balanced
Mid-complexity feature implementation     → balanced
General coding (default)                  → balanced
```

## How To Read Routing

This file routes work by capability level, not by hardcoded vendor model name.

- `high` means use the strongest available reasoning profile for architecture, heuristics, grading, and trade-off decisions
- `fast` means use a lower-cost faster profile for structured implementation work such as routes, schemas, logging, and scaffolding
- `balanced` means use the default middle-ground profile for general coding and refactoring

For this project, the intended task routing is:

- analysis pipeline work → `high`
- deployment work → `fast`
- reliability work → `fast`
- moderate cross-cutting coding work → `balanced`

If you need the exact underlying model name, that depends on the Codex runtime configuration outside this repository. `AGENTS.md` defines which capability tier should be used for a task, not the provider-specific model alias.
