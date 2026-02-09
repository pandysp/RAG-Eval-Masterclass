"""
CloudBase RAG — LLM-as-Judge

Queries the RAG backend and uses an LLM judge to determine whether
each answer is semantically correct compared to the expected answer.

Usage:
    python run_evaluation_llm.py

Prerequisites:
    uvicorn main:app --host 127.0.0.1 --port 8000
"""

import csv
import json
import os
import sys
import time
import requests

from dotenv import load_dotenv
from openai import OpenAI

BASE_URL = "http://localhost:8000"
INPUT_CSV = "cloudbase-testfragen.csv"
OUTPUT_CSV = "evaluation_results_llm.csv"
JUDGE_MODEL = "gpt-4o-mini"

# Load API key the same way as main.py
load_dotenv(dotenv_path="./openai_key.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JUDGE_SYSTEM_PROMPT = """\
Du bist ein strenger Evaluator fuer ein RAG-System ueber das Produkt "CloudBase".
Deine Aufgabe: Pruefe, ob die tatsaechliche Antwort semantisch aequivalent zur erwarteten Antwort ist.

Regeln:
- Unterschiedliche Formulierungen sind OK, solange der Inhalt stimmt.
  Beispiel: "49Euro" und "49 Euro" sind gleichwertig.
- Alle wesentlichen Fakten (Zahlen, Namen, Daten, Fristen, Einschraenkungen) \
muessen in der tatsaechlichen Antwort enthalten sein.
- Bei Verweigerungsfragen (erwartete Antwort enthaelt "Keine Information verfuegbar" \
oder aehnlich): Die tatsaechliche Antwort muss klar ablehnen, eine Antwort zu geben. \
Jede Formulierung der Verweigerung zaehlt als korrekt.
- Wenn die tatsaechliche Antwort korrekte Informationen enthaelt, aber wesentliche \
Fakten aus der erwarteten Antwort fehlen, antworte mit NO.
- Wenn die tatsaechliche Antwort Informationen halluziniert, die nicht in der \
erwarteten Antwort stehen, antworte mit NO.

Antworte ausschliesslich als JSON (kein Markdown, keine Codebloecke):
{"verdict": "YES" oder "NO", "reason": "kurze Begruendung auf Deutsch"}\
"""

JUDGE_USER_TEMPLATE = """\
Frage: {question}
Erwartete Antwort: {expected}
Tatsaechliche Antwort: {actual}
Testgrund: {why}\
"""


def query_rag(question: str) -> dict:
    resp = requests.get(f"{BASE_URL}/query_with_context", params={"query": question})
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
    expected_doc = expected_doc.strip()
    if expected_doc.upper() == "KEINE":
        return True
    expected_docs = [d.strip() for d in expected_doc.split("|")]
    for doc in expected_docs:
        if doc in retrieved_filenames:
            return True
    return False


def judge_answer(question: str, expected: str, actual: str, why: str) -> dict:
    """Ask the LLM judge whether the actual answer is semantically correct."""
    user_msg = JUDGE_USER_TEMPLATE.format(
        question=question, expected=expected, actual=actual, why=why,
    )

    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"verdict": "ERROR", "reason": f"Judge returned invalid JSON: {raw}"}

    return result


def main():
    # Pre-flight: check server is running
    try:
        requests.get(f"{BASE_URL}/query?query=ping", timeout=5)
    except requests.exceptions.ConnectionError:
        print("ERROR: RAG server is not running!")
        print("Start it with: uvicorn main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)

    with open(INPUT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    print(f"Loaded {len(rows)} questions from {INPUT_CSV}")
    print(f"Judge model: {JUDGE_MODEL}\n")

    results = []
    retrieval_scores = []
    judge_scores = []

    for i, row in enumerate(rows, 1):
        question = row.get("frage", "").strip()
        if not question:
            continue

        print(f"[{i}/{len(rows)}] {question[:80]}...")

        # Query the RAG system
        try:
            data = query_rag(question)
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            chunks = format_chunks(sources)
        except Exception as e:
            print(f"  RAG ERROR: {e}")
            answer = f"ERROR: {e}"
            sources = []
            chunks = ""

        # Retrieval scoring
        retrieved_filenames = get_retrieved_filenames(sources)
        expected_doc = row.get("erwartetes_dokument", "")
        retrieval_hit = check_retrieval(expected_doc, retrieved_filenames)
        retrieval_scores.append(retrieval_hit)

        # LLM Judge scoring
        expected_answer = row.get("erwartete_antwort", "")
        why = row.get("warum", "")

        if answer.startswith("ERROR:"):
            verdict = {"verdict": "NO", "reason": "RAG query failed"}
        else:
            verdict = judge_answer(question, expected_answer, answer, why)

        is_correct = verdict.get("verdict", "").upper() == "YES"
        judge_scores.append(is_correct)

        status = "PASS" if retrieval_hit and is_correct else "FAIL"
        print(
            f"  Retrieval: {'HIT' if retrieval_hit else 'MISS'} | "
            f"Judge: {verdict.get('verdict', '?')} | {status}"
        )
        if not is_correct:
            print(f"  Reason: {verdict.get('reason', '')}")

        results.append({
            **row,
            "rag_answer": answer,
            "retrieved_chunks": chunks,
            "retrieval_hit": "TRUE" if retrieval_hit else "FALSE",
            "retrieved_files": ", ".join(retrieved_filenames),
            "judge_verdict": verdict.get("verdict", "ERROR"),
            "judge_reason": verdict.get("reason", ""),
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
    judge_passes = sum(judge_scores)
    perfect = sum(1 for r, j in zip(retrieval_scores, judge_scores) if r and j)

    print(f"\n{'='*60}")
    print(f"  RESULTS SUMMARY ({total} questions)")
    print(f"{'='*60}")
    print(f"  Retrieval accuracy : {retrieval_hits}/{total} ({retrieval_hits/total*100:.1f}%)")
    print(f"  Judge pass rate    : {judge_passes}/{total} ({judge_passes/total*100:.1f}%)")
    print(f"  Perfect (both)     : {perfect}/{total} ({perfect/total*100:.1f}%)")
    print(f"{'='*60}")
    print(f"  Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
