# Eval Prompts

This file lists the prompt content currently used by the evaluation framework.

## Purpose

The project uses two kinds of evaluation logic:

- deterministic assertions and rubric matching
- optional LLM-based judging

Only the LLM-based judge uses explicit prompt text. The rubric judge does not call a model. It checks the presence of expected concepts or keywords in the output.

## Current LLM Judge Prompts

Source: [`eval_framework/judges.py`](/Users/syedraza/multiagent-dataanalysis/eval_framework/judges.py)

### System Prompt

```text
You are an evaluation judge. Return compact JSON with keys `passed` (bool) and `reason` (string).
```

### Default User Instruction Prompt

```text
Does the actual output satisfy the expectation?
```

### Structured User Payload

The LLM judge sends a structured payload to the model in JSON form:

```json
{
  "instruction": "<prompt>",
  "path": "<assertion path>",
  "expected": "<expected value>",
  "prediction": "<full prediction object>"
}
```

This means the effective user-side eval prompt is composed from:

- the assertion-specific `prompt` if provided
- the assertion `path`
- the expected value
- the actual prediction payload

## Current Rubric Judge Inputs

The rubric judge does not use a natural-language prompt. It uses keyword matching against the output.

Example rubric values currently generated in [`evals/generate_cases.py`](/Users/syedraza/multiagent-dataanalysis/evals/generate_cases.py):

```json
["numeric", "summary", "impute", "duplicate"]
```

Example rubric-style assertion:

```json
{
  "path": "recommendations",
  "op": "rubric_judge",
  "judge": "rubric",
  "value": ["numeric", "summary"],
  "threshold": 1
}
```

## Where Prompts Can Change

Prompt behavior can currently change in these places:

- [`eval_framework/judges.py`](/Users/syedraza/multiagent-dataanalysis/eval_framework/judges.py) for the OpenAI judge system prompt and default user instruction
- dataset assertions if you add a custom `prompt` field to an `llm_judge` assertion

Example custom assertion:

```json
{
  "path": "recommendations",
  "op": "llm_judge",
  "judge": "openai",
  "prompt": "Decide whether the recommendations are useful, specific, and grounded in the workbook summary.",
  "value": {
    "must_be_grounded": true
  }
}
```

## Recommended Prompt Management

If the eval layer grows, move prompts into a versioned config structure such as:

- `evals/prompts/llm_judge_default.txt`
- `evals/prompts/recommendation_quality.txt`
- `evals/prompts/summary_grounding.txt`

That would make prompt experiments easier to track across models and eval runs.
