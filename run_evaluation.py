"""
CloudBase RAG — Keyword Assessment

Queries the RAG backend and assesses each answer using:
1. Retrieval accuracy — Was the correct source document retrieved?
2. Keyword match    — What % of expected keywords appear in the answer?

Usage:
    python run_evaluation.py

Prerequisites:
    uvicorn main:app --host 127.0.0.1 --port 8000
"""

import csv
import os
import sys
import time
import requests

BASE_URL = "http://localhost:8000"
INPUT_CSV = "cloudbase-testfragen.csv"
OUTPUT_CSV = "evaluation_results.csv"


def query_rag(question: str) -> dict:
    resp = requests.get(f"{BASE_URL}/query_with_context", params={"query": question}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def format_chunks(sources: list) -> str:
    parts = []
    for i, src in enumerate(sources, 1):
        filename = os.path.basename(src.get("filename", "unknown"))
        score = src.get("score")
        text = src.get("text", "")
        score_str = f" (score: {score:.4f})" if score is not None else ""
        parts.append(f"[Chunk {i} | {filename}{score_str}]\n{text}")
    return "\n---\n".join(parts)


def get_retrieved_filenames(sources: list) -> list:
    filenames = []
    for src in sources:
        raw = src.get("filename", "")
        if raw:
            filenames.append(os.path.basename(raw))
    return filenames


def check_retrieval(expected_doc: str, retrieved_filenames: list) -> bool:
    """Check if at least one expected document was retrieved.
    Expected can be pipe-separated (e.g. 'integrationen.md|produkt-professional.md').
    'KEINE' means no specific document is expected (unanswerable question).
    """
    expected_doc = expected_doc.strip()
    if expected_doc.upper() == "KEINE":
        return True
    expected_docs = [d.strip() for d in expected_doc.split("|")]
    return any(doc in retrieved_filenames for doc in expected_docs)


def check_keywords(expected_keywords: str, answer: str) -> tuple:
    """Check which expected keywords appear in the answer (case-insensitive).
    Returns (found_keywords, missing_keywords, ratio).
    """
    if not expected_keywords.strip():
        return [], [], 1.0
    keywords = [kw.strip() for kw in expected_keywords.split(",") if kw.strip()]
    answer_lower = answer.lower()
    found = [kw for kw in keywords if kw.lower() in answer_lower]
    missing = [kw for kw in keywords if kw.lower() not in answer_lower]
    ratio = len(found) / len(keywords) if keywords else 1.0
    return found, missing, ratio


def main():
    # Pre-flight: check server is running
    try:
        requests.get(f"{BASE_URL}/query?query=ping", timeout=5)
    except requests.exceptions.RequestException:
        print("ERROR: RAG server is not running!")
        print("Start it with: uvicorn main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)

    with open(INPUT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    print(f"Loaded {len(rows)} questions from {INPUT_CSV}\n")

    results = []
    retrieval_scores = []
    keyword_scores = []

    for i, row in enumerate(rows, 1):
        question = row.get("frage", "").strip()
        if not question:
            continue

        print(f"[{i}/{len(rows)}] {question[:80]}...")

        try:
            data = query_rag(question)
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            chunks = format_chunks(sources)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"  ERROR: {e}")
            answer = f"ERROR: {e}"
            sources = []
            chunks = ""

        # Retrieval scoring
        retrieved_filenames = get_retrieved_filenames(sources)
        expected_doc = row.get("erwartetes_dokument", "")
        retrieval_hit = check_retrieval(expected_doc, retrieved_filenames)
        retrieval_scores.append(retrieval_hit)

        # Keyword scoring
        expected_keywords = row.get("erwartete_keywords", "")
        found_kw, missing_kw, kw_ratio = check_keywords(expected_keywords, answer)
        keyword_scores.append(kw_ratio)

        if retrieval_hit and kw_ratio == 1.0:
            status = "OK"
        elif retrieval_hit or kw_ratio > 0:
            status = "PARTIAL"
        else:
            status = "FAIL"
        print(
            f"  Retrieval: {'HIT' if retrieval_hit else 'MISS'} | "
            f"Keywords: {len(found_kw)}/{len(found_kw)+len(missing_kw)} | {status}"
        )
        if missing_kw:
            print(f"  Missing keywords: {', '.join(missing_kw)}")

        results.append({
            **row,
            "rag_answer": answer,
            "retrieved_chunks": chunks,
            "retrieval_hit": "TRUE" if retrieval_hit else "FALSE",
            "retrieved_files": ", ".join(retrieved_filenames),
            "keyword_found": ", ".join(found_kw) if found_kw else "",
            "keyword_missing": ", ".join(missing_kw) if missing_kw else "",
            "keyword_score": f"{kw_ratio:.2f}",
        })

        time.sleep(0.5)

    if not results:
        print("No results to write.")
        sys.exit(1)

    fieldnames = list(results[0].keys())
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    # Summary
    total = len(results)
    retrieval_hits = sum(retrieval_scores)
    avg_keyword = sum(keyword_scores) / total if total else 0
    perfect = sum(1 for r, k in zip(retrieval_scores, keyword_scores) if r and k == 1.0)

    print(f"\n{'='*60}")
    print(f"  RESULTS SUMMARY ({total} questions)")
    print(f"{'='*60}")
    print(f"  Retrieval accuracy : {retrieval_hits}/{total} ({retrieval_hits/total*100:.1f}%)")
    print(f"  Avg keyword score  : {avg_keyword*100:.1f}%")
    print(f"  Perfect answers    : {perfect}/{total} ({perfect/total*100:.1f}%)")
    print(f"{'='*60}")
    print(f"  Results saved to {OUTPUT_CSV}")
    print(f"  Open eval_review.html to review results visually.")


if __name__ == "__main__":
    main()
