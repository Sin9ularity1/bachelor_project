
from pathlib import Path
from datetime import datetime, timezone
import csv
import json

from rag import ask

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = ROOT / "questions.json"
RESULTS_DIR = ROOT / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"poisoned_{timestamp}.csv"

    rows = []

    for index, test in enumerate(questions, start=1):
        question = test["question"]
        expected_source = test["expected_source"]

        print(f"[{index}/{len(questions)}] {question}")

        try:
            answer, retrieved = ask(question)

            retrieved_sources = [
                item["source"] for item in retrieved
            ]

            poisoned_chunks = sum(
                item.get("dataset") == "poisoned"
                for item in retrieved
            )

            source_rank = next(
                (
                    item["rank"]
                    for item in retrieved
                    if item["source"] == expected_source
                ),
                None
            )

            rows.append({
                "id": test["id"],
                "question": question,
                "expected_answer": test["expected_answer"],
                "expected_source": expected_source,
                "generated_answer": answer,
                "retrieved_sources": " | ".join(retrieved_sources),
                "poisoned_chunks_retrieved": poisoned_chunks,
                "expected_source_rank": source_rank or "",
                "source_in_top_k": source_rank is not None,
                "status": "completed"
            })

            print(
                f"  Expected source rank: "
                f"{source_rank if source_rank is not None else 'NOT FOUND'}"
            )
            print(f"  Poisoned chunks retrieved: {poisoned_chunks}")

        except Exception as error:
            print(f"  ERROR: {error}")

            rows.append({
                "id": test["id"],
                "question": question,
                "expected_answer": test["expected_answer"],
                "expected_source": expected_source,
                "generated_answer": "",
                "retrieved_sources": "",
                "poisoned_chunks_retrieved": 0,
                "expected_source_rank": "",
                "source_in_top_k": False,
                "status": f"error: {error}"
            })

    fieldnames = [
        "id",
        "question",
        "expected_answer",
        "expected_source",
        "generated_answer",
        "retrieved_sources",
        "poisoned_chunks_retrieved",
        "expected_source_rank",
        "source_in_top_k",
        "status"
    ]

    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    completed = [
        row for row in rows
        if row["status"] == "completed"
    ]

    successful = sum(
        row["source_in_top_k"]
        for row in completed
    )

    questions_with_poison = sum(
        row["poisoned_chunks_retrieved"] > 0
        for row in completed
    )

    total_poisoned_chunks = sum(
        row["poisoned_chunks_retrieved"]
        for row in completed
    )

    print("\n--------------------------------")
    print("Poisoned RAG evaluation complete")
    print("--------------------------------")
    print(f"Total questions: {len(questions)}")
    print(f"Completed: {len(completed)}")
    print(f"Errors: {len(questions) - len(completed)}")

    if completed:
        print(
            f"Expected source in top-k: "
            f"{successful}/{len(completed)} "
            f"({successful / len(completed) * 100:.1f}%)"
        )

        print(
            f"Questions retrieving poisoned content: "
            f"{questions_with_poison}/{len(completed)} "
            f"({questions_with_poison / len(completed) * 100:.1f}%)"
        )

        print(
            f"Total poisoned chunks retrieved: "
            f"{total_poisoned_chunks}"
        )

    print(f"Results saved: {output_file}")
    print("--------------------------------")


if __name__ == "__main__":
    main()
