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
git clone https://github.com/pandysp/RAG-AI-Masterclass.git
cd RAG-AI-Masterclass
make setup        # installs dependencies, creates openai_key.env
# Edit openai_key.env and add your API key
```

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Usage

Run `make` to see all available commands:

```
  help         Show this help
  setup        Install dependencies and prepare env file
  server       Start the RAG server
  collect      Collect RAG answers for manual review
  eval         Run keyword evaluation
  eval-llm     Run LLM-as-Judge evaluation
  review       Open the annotation interface in the browser
  clean        Remove result CSVs and cached outputs
  reset        Remove index storage (forces rebuild on next server start)
```

### Quick start

```bash
make server       # 1. Start the RAG server (http://127.0.0.1:8000)
make eval         # 2. Run keyword evaluation → evaluation_results.csv
make review       # 3. Open annotation interface in browser
```

### All evaluation scripts

| Command | Script | What it does |
|---------|--------|-------------|
| `make collect` | `collect.py` | Saves RAG answers to `collected_answers.csv` for manual inspection |
| `make eval` | `run_evaluation.py` | Retrieval accuracy + keyword matching → `evaluation_results.csv` |
| `make eval-llm` | `run_evaluation_llm.py` | LLM-as-Judge (GPT-4o-mini) → `evaluation_results_llm.csv` |

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
3. Switch to `PROMPT_IMPROVED` → `make reset` → restart server → re-run evaluation
4. Compare scores to see the improvement

> **Important:** After changing the prompt, run `make reset` so the index is rebuilt on next server start.

## License

MIT
