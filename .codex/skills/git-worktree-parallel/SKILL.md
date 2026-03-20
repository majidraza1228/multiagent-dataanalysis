---
name: git-worktree-parallel
description: Git worktree setup for parallel agent execution, cascade pattern, merge back, and cleanup
---

```bash
# initialize repo and create 2 worktrees
git init ml-image-classifier && cd ml-image-classifier
git commit --allow-empty -m "init"

git worktree add ../ml-api-agent -b ml-api-agent
git worktree add ../ml-frontend-agent -b ml-frontend-agent
```

```bash
# run two agents in parallel
(cd ../ml-api-agent && claude --print "build the FastAPI backend") > api_result.json &
(cd ../ml-frontend-agent && claude --print "build the Gradio frontend") > ui_result.json &
wait
echo "Both agents done"
```

```bash
# cascade pattern: start agent B as soon as agent A writes result JSON
(cd ../ml-api-agent && claude --print "build the FastAPI backend, write openapi.json when done") > /dev/null
# agent A done → trigger B with context
(cd ../ml-frontend-agent && claude --print "build Gradio UI, use openapi.json at ../ml-api-agent/openapi.json for API contract")
```

```bash
# merge worktrees back to main
cd ml-image-classifier

git merge ml-api-agent --no-ff -m "merge: FastAPI backend from agent"
git merge ml-frontend-agent --no-ff -m "merge: Gradio frontend from agent"
```

```bash
# cleanup worktrees and branches
git worktree remove ../ml-api-agent
git worktree remove ../ml-frontend-agent
git branch -d ml-api-agent ml-frontend-agent
```
