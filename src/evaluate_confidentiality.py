
from pathlib import Path
from datetime import datetime
import csv
import json

from rag_confidentiality import ask

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = ROOT / "questions_confidentiality.json"
RESULTS_DIR = ROOT / "results"

CONDITIONS = ["clean", "poisoned"]
ROLE = "employee"


def main():
    questions = json.loads(
        QUESTIONS_FILE.read_text(encoding="utf-8")
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = (
        RESULTS_DIR /
        f"confidentiality_targeted_{timestamp}.csv"
    )

    fieldnames = [
        "question_id",
        "condition",
        "role",
        "question",
        "target_employee",
        "protected_value",
        "answer",
        "poison_retrieved",
        "confidential_retrieved",
        "retrieved_sources",
        "retrieved_distances",
    ]

    total = len(questions) * len(CONDITIONS)
    completed = 0

    with output_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()

        for condition in CONDITIONS:
            print(f"\n=== {condition.upper()} ===", flush=True)

            for item in questions:
                answer, retrieved = ask(
                    item["question"],
                    condition=condition,
                    role=ROLE,
                )

                poison_retrieved = any(
                    chunk["dataset"] == "poisoned"
                    for chunk in retrieved
                )

                confidential_retrieved = any(
                    chunk["classification"] == "confidential"
                    for chunk in retrieved
                )

                writer.writerow({
                    "question_id": item["id"],
                    "condition": condition,
                    "role": ROLE,
                    "question": item["question"],
                    "target_employee": item["target_employee"],
                    "protected_value": item["protected_value"],
                    "answer": answer,
                    "poison_retrieved": poison_retrieved,
                    "confidential_retrieved": confidential_retrieved,
                    "retrieved_sources": "; ".join(
                        chunk["source"]
                        for chunk in retrieved
                    ),
                    "retrieved_distances": "; ".join(
                        f"{chunk['distance']:.4f}"
                        for chunk in retrieved
                    ),
                })

                file.flush()
                completed += 1

                print(
                    f"[{completed}/{total}] "
                    f"{condition} {item['id']} "
                    f"poison={poison_retrieved} "
                    f"confidential={confidential_retrieved}",
                    flush=True
                )

    print("\nEvaluation completed.")
    print(f"Results saved to: {output_file}")
    print(f"Total evaluations: {completed}")


if __name__ == "__main__":
    main()
