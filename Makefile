.PHONY: help setup server collect eval eval-llm review clean reset

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies and prepare env file
	uv sync
	@test -f openai_key.env || (cp openai_key.env.example openai_key.env && echo "Created openai_key.env — add your API key")

server: ## Start the RAG server
	uv run uvicorn main:app --host 127.0.0.1 --port 8000

collect: ## Collect RAG answers for manual review
	uv run python collect.py

eval: ## Run keyword evaluation
	uv run python run_evaluation.py

eval-llm: ## Run LLM-as-Judge evaluation
	uv run python run_evaluation_llm.py

review: ## Open the annotation interface in the browser
	open eval_review.html || xdg-open eval_review.html 2>/dev/null

clean: ## Remove result CSVs and cached outputs
	rm -f collected_answers.csv evaluation_results.csv evaluation_results_llm.csv cached_outputs.json

reset: clean ## Remove index storage (forces rebuild on next server start)
	rm -rf storage/
