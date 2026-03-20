#!/usr/bin/env python3
"""
OpenAI MCP Server
Exposes OpenAI API capabilities as MCP tools for Codex-based workflows.

Tools:
  - openai_chat       : text chat completions (GPT-4o, GPT-4-turbo, etc.)
  - openai_vision     : describe or analyze an image file via GPT-4o vision
  - openai_embed      : generate text embeddings (text-embedding-3-small)
  - openai_moderate   : run OpenAI content moderation on a string

Usage:
  python mcp_servers/openai_server.py
  (or configured via .mcp.json)
"""

import os
import base64
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from openai import OpenAI

mcp = FastMCP("openai")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# ---------------------------------------------------------------------------
# Tool: openai_chat
# ---------------------------------------------------------------------------
@mcp.tool()
def openai_chat(
    prompt: str,
    model: str = "gpt-4o",
    system: str = "You are a helpful assistant.",
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """
    Send a chat prompt to an OpenAI model and return the response text.

    Args:
        prompt:      The user message to send.
        model:       OpenAI model ID (default: gpt-4o).
        system:      System prompt (default: helpful assistant).
        temperature: Sampling temperature 0-2 (default: 0.7).
        max_tokens:  Maximum tokens in the response (default: 1024).

    Returns:
        The assistant's response as a string.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Tool: openai_vision
# ---------------------------------------------------------------------------
@mcp.tool()
def openai_vision(
    image_path: str,
    prompt: str = "Describe this image in detail.",
    model: str = "gpt-4o",
) -> str:
    """
    Send an image file to GPT-4o vision and get a text response.

    Args:
        image_path: Absolute or relative path to an image file (jpg, png, gif, webp).
        prompt:     Question or instruction about the image.
        model:      Vision-capable model (default: gpt-4o).

    Returns:
        The model's description or answer as a string.
    """
    path = Path(image_path)
    if not path.exists():
        return f"Error: file not found: {image_path}"

    suffix = path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Tool: openai_embed
# ---------------------------------------------------------------------------
@mcp.tool()
def openai_embed(
    text: str,
    model: str = "text-embedding-3-small",
) -> str:
    """
    Generate an embedding vector for the given text.

    Args:
        text:  The input text to embed.
        model: Embedding model (default: text-embedding-3-small).

    Returns:
        JSON string with keys: model, dimensions, preview (first 8 values).
    """
    response = client.embeddings.create(input=text, model=model)
    vector = response.data[0].embedding
    return json.dumps({
        "model": model,
        "dimensions": len(vector),
        "preview": [round(v, 6) for v in vector[:8]],
    })


# ---------------------------------------------------------------------------
# Tool: openai_moderate
# ---------------------------------------------------------------------------
@mcp.tool()
def openai_moderate(text: str) -> str:
    """
    Run OpenAI content moderation on a string.

    Args:
        text: The text to check.

    Returns:
        JSON string with flagged (bool), categories that triggered, and scores.
    """
    response = client.moderations.create(input=text)
    result = response.results[0]
    triggered = {k: round(v, 4) for k, v in result.category_scores.__dict__.items() if v > 0.01}
    return json.dumps({
        "flagged": result.flagged,
        "triggered_categories": {k: v for k, v in triggered.items() if getattr(result.categories, k, False)},
        "top_scores": dict(sorted(triggered.items(), key=lambda x: -x[1])[:5]),
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
