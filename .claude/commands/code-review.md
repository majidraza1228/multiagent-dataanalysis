Perform a full automated code review of this repository, then publish all findings as GitHub PR comments. Follow these steps exactly:

## Step 1 — Explore and review the codebase

Use the Explore subagent (thorough) to read every significant source file (.py, .ts, .js, config files, requirements). For each file identify:

- **SECURITY** vulnerabilities: injection, hardcoded secrets, insecure configs, unvalidated input, weak crypto, auth bypass, CORS misconfig, ReDoS
- **BUG** / logic errors: race conditions, unhandled exceptions, silent swallowing, type errors, off-by-one, data loss
- **PERF** issues: blocking I/O in async context, O(n²) loops, unbounded memory, unnecessary buffering
- **TODO** / quality: magic numbers, dead code, missing error context, late imports, inconsistent patterns

For each finding record:
- file path and line number(s)
- severity: 🔴 Critical/High, 🟡 Medium, 🟢 Low
- the problematic code snippet
- a concrete fix with corrected code

## Step 2 — Create a branch and empty commit

Run:
```
git checkout -b code-review/$(date +%Y-%m-%d)
git commit --allow-empty -m "chore: open code review tracking PR"
git push -u origin HEAD
```

Do NOT modify any source files.

## Step 3 — Create the PR

Use `gh pr create` with:
- `--base main`
- `--title` = `"Code Review: <date> findings"`
- `--body` listing the files reviewed and a severity legend (🔴/🟡/🟢). Do NOT put the full findings in the body — those go in individual comments.

## Step 4 — Post each finding as a separate PR comment

For every finding from Step 1, run `gh pr comment <number> --body "..."`.

Each comment must follow this template:

```
### <severity emoji> `<file>:<line>` — <short title>

**<tag: SECURITY / BUG / PERF / TODO>**

\```python
<problematic code>
\```

<1-2 sentence explanation of the risk or impact>

**Fix:**
\```python
<corrected code>
\```
```

Post one comment per finding. Do not batch findings into a single comment.

## Step 5 — Report back

After all comments are posted, output a markdown table summarising:
- PR URL
- Total findings by severity
- Files with the most issues
