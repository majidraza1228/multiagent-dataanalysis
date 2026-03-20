---
name: openai-mcp
description: Call OpenAI models (GPT-4o chat, vision, embeddings, moderation) as MCP tools from within Codex workflows
---

## Setup (one-time)

```bash
# 1. Install dependencies
pip install "mcp[cli]" openai

# 2. Set your API key in the environment
export OPENAI_API_KEY=sk-...

# 3. Project wiring
#    The server is already configured in .mcp.json.
#    Ensure the environment variable is available before starting Codex.
```

---

## Available Tools

Once the MCP server is running, Codex agents can call these tools directly.

### `openai_chat`
Send a text prompt to any OpenAI chat model.

```
openai_chat(
    prompt="Explain backpropagation in one paragraph.",
    model="gpt-4o",           # default
    system="You are a ML tutor.",
    temperature=0.7,          # default
    max_tokens=1024           # default
)
```

### `openai_vision`
Describe or analyze an image file using GPT-4o vision.

```
openai_vision(
    image_path="samples/cat.jpg",
    prompt="What breed of cat is this? How confident are you?",
    model="gpt-4o"            # default
)
```

**Use case in this project:** cross-check the CIFAR-10 CNN prediction against GPT-4o's vision description to catch obvious misclassifications.

### `openai_embed`
Generate a text embedding vector (returns JSON with dimensions + preview).

```
openai_embed(
    text="a photo of a tabby cat sitting on a windowsill",
    model="text-embedding-3-small"   # default
)
```

### `openai_moderate`
Run content moderation on a string.

```
openai_moderate(
    text="some text to check"
)
# returns: { flagged: bool, triggered_categories: {...}, top_scores: {...} }
```

---

## Example: second-opinion prediction enrichment

Add this to `app/routers.py` to call GPT-4o vision alongside the CNN:

```python
import tempfile, os
from pathlib import Path

@predict_router.post("/predict-enriched")
async def predict_enriched(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    image_bytes = await file.read()

    # CNN prediction (existing)
    cnn_result = predict(image_bytes)

    # GPT-4o second opinion via MCP tool
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name
    try:
        gpt_desc = openai_vision(
            image_path=tmp_path,
            prompt="In one sentence, what object or animal is the main subject of this image?"
        )
    finally:
        os.unlink(tmp_path)

    return {**cnn_result, "gpt4o_description": gpt_desc}
```

---

## Server location

`mcp_servers/openai_server.py` — stdio transport, reads `OPENAI_API_KEY` from env.

Config is in `.mcp.json` at the project root. Codex picks it up for project-scoped MCP usage.
