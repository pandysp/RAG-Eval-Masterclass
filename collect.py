"""
CloudBase RAG — Collect answers

Queries the RAG backend for every question in the golden dataset
and saves answers with retrieved chunks for manual inspection.

Usage:
    python collect.py

Prerequisites:
    uvicorn main:app --host 127.0.0.1 --port 8000
"""

import os
import sys
import pandas as pd
import requests
from tqdm import tqdm

API_URL = "http://127.0.0.1:8000/query_with_context"
INPUT_CSV = "cloudbase-testfragen.csv"
OUTPUT_CSV = "collected_answers.csv"


def query_rag(query: str) -> dict:
    try:
        response = requests.get(API_URL, params={"query": query}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")
        return {"answer": "", "sources": []}


def format_chunks(sources: list) -> str:
    parts = []
    for i, src in enumerate(sources, 1):
        filename = os.path.basename(src.get("filename", "unknown"))
        score = src.get("score")
        text = src.get("text", "")
        score_str = f" (score: {score:.4f})" if score is not None else ""
        parts.append(f"[Chunk {i} | {filename}{score_str}]\n{text}")
    return "\n---\n".join(parts)


def main():
    # Pre-flight: check server is running
    try:
        requests.get("http://127.0.0.1:8000/query?query=ping", timeout=5)
    except requests.exceptions.ConnectionError:
        print("ERROR: RAG server is not running!")
        print("Start it with: uvicorn main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV, sep=";")
    print(f"{len(df)} questions loaded from {INPUT_CSV}\n")

    results = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Collecting answers"):
        frage = row["frage"]
        response = query_rag(frage)

        sources = response.get("sources", [])
        retrieved_files = [
            os.path.basename(s.get("filename", "")) for s in sources if s.get("filename")
        ]

        results.append({
            "frage": frage,
            "warum": row.get("warum", ""),
            "erwartete_antwort": row["erwartete_antwort"],
            "erwartetes_dokument": row["erwartetes_dokument"],
            "erwartete_keywords": row.get("erwartete_keywords", ""),
            "rag_answer": response.get("answer", ""),
            "retrieved_files": ", ".join(retrieved_files),
            "retrieved_chunks": format_chunks(sources),
        })

    out = pd.DataFrame(results)
    out.to_csv(OUTPUT_CSV, index=False, sep=";")
    print(f"\nAnswers saved to {OUTPUT_CSV}")
    print(f"You can review them in eval_review.html or open the CSV directly.")


if __name__ == "__main__":
    main()
