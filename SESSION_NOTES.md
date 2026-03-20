# Session Notes

## Current Status

- Project name: `multiagent-dataanalysis`
- Local path: `/Users/syedraza/multiagent-dataanalysis`
- Git remote: `https://github.com/majidraza1228/multiagent-dataanalysis.git`
- Main branch: `main`

## Environment Notes

- Use Python `3.11`
- Create and activate `.venv` before running the project
- Install dependencies with `pip install -r requirements.txt`
- `huggingface_hub==0.23.5` is pinned for Gradio compatibility

## Demo Notes

- Default demo uses `3` terminals: backend, UI, monitoring
- Expanded demo uses `4` terminals: backend, UI, MLflow, monitoring
- Demo instructions are in `DEMO.md`
- Sample files are in `samples/`
- If needed, convert CSV demo files to `.xlsx` before presenting

## MLflow Notes

- MLflow may run on `5000` or `5001`
- Use `MLFLOW_TRACKING_URI` when the server is not on the default port
- MLflow scripts now read `MLFLOW_TRACKING_URI` from the environment
- Copy sample files into `data/` before running `python model/train.py`

## Agentic Workflow Notes

- Routing rules are in `AGENTS.md`
- `high` is for architecture and heuristics
- `fast` is for structured implementation and reliability glue
- `balanced` is for moderate general coding tasks

## Recommended Startup Prompt

```text
Read AGENTS.md, README.md, DEMO.md, and SESSION_NOTES.md first.
Then continue from the current project state.
```

## Open Items

- Add new tasks here before ending a session
- Record any environment-specific issues here
- Record the next exact action if work is unfinished
