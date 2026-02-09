# RAG AI Masterclass

A hands-on workshop for learning how to evaluate Retrieval-Augmented Generation (RAG) systems. Built around a fictional product called **CloudBase**, with a knowledge base of 8 German-language articles and a 25-question golden test dataset.

## What's in this repo

| File | Purpose |
|------|---------|
| `main.py` | FastAPI RAG server (LlamaIndex + OpenAI) with two switchable prompts |
| `collect.py` | Collect answers from the RAG system for manual review |
| `run_evaluation.py` | Keyword-based evaluation (retrieval accuracy + keyword matching) |
| `run_evaluation_llm.py` | LLM-as-Judge evaluation (semantic correctness via GPT-4o-mini) |
| `eval_review.html` | Browser-based annotation interface for human review |
| `cloudbase-testfragen.csv` | Golden dataset with 25 test questions |
| `data/` | Knowledge base (8 markdown articles about CloudBase) |
| `chat_interface.html` | Web chat UI for the RAG system |

## Setup

```bash
# Clone the repo
git clone https://github.com/pandysp/RAG-AI-Masterclass.git
cd RAG-AI-Masterclass

# Install dependencies (creates .venv automatically)
uv sync

# Add your OpenAI API key
cp openai_key.env.example openai_key.env
# Edit openai_key.env and add your key
```

## Usage

### 1. Start the RAG server

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the chat interface.

### 2. Collect answers (optional)

```bash
uv run python collect.py
```

Saves all RAG answers to `collected_answers.csv` for manual inspection.

### 3. Run keyword evaluation

```bash
uv run python run_evaluation.py
```

Checks retrieval accuracy and keyword presence. Results go to `evaluation_results.csv`.

### 4. Run LLM-as-Judge evaluation

```bash
uv run python run_evaluation_llm.py
```

Uses GPT-4o-mini to judge answer correctness semantically. Results go to `evaluation_results_llm.csv`.

### 5. Review results

Open `eval_review.html` in a browser and load the CSV from step 3. Rate each answer as correct, partial, or incorrect and add notes.

## Prompt iteration

`main.py` contains two prompts:

- **`PROMPT_BASELINE`** — Minimal prompt, no guardrails
- **`PROMPT_IMPROVED`** — Adds German language instruction, refusal behavior, anti-hallucination rules

The active prompt is set on this line:

```python
# >>> Change this line to switch prompts <<<
SYSTEM_PROMPT = PROMPT_BASELINE
```

The workshop flow:

1. Run evaluation with `PROMPT_BASELINE` → note the scores
2. Analyze errors (hallucinations, wrong language, incomplete answers)
3. Switch to `PROMPT_IMPROVED` → delete `storage/` → restart server → re-run evaluation
4. Compare scores to see the improvement

> **Important:** After changing the prompt, delete the `storage/` directory so the index is rebuilt with the new prompt template.

## License

MIT
