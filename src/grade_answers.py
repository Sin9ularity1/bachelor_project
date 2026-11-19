
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"

# Find the newest baseline CSV, excluding previously graded files.
baseline_files = sorted(RESULTS_DIR.glob("baseline_*.csv"))
baseline_files = [
    path for path in baseline_files
    if not path.stem.endswith("_graded")
]

if not baseline_files:
    raise FileNotFoundError("No baseline CSV found in results/")

INPUT_FILE = baseline_files[-1]
OUTPUT_FILE = INPUT_FILE.with_name(
    INPUT_FILE.stem + "_graded.csv"
)


def normalize(text):
    """Normalize text for basic comparison."""
    text = text.lower()
    text = text.replace("’", "'")
    text = text.replace(",", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def grade_answer(expected, generated):
    """
    Conservative automated grading.

    Returns:
      correct      - Expected answer appears in the response.
      incorrect    - Model explicitly says it does not know.
      needs_review - Automatic matching is inconclusive.
    """
    expected_normalized = normalize(expected)
    generated_normalized = normalize(generated)

    if not generated_normalized:
        return "incorrect"

    # An explicit refusal takes priority over matching.
    if re.search(
        r"\b(i do not know|i don't know|i cannot determine|"
        r"i can't determine)\b",
        generated_normalized
    ):
        return "incorrect"

    if expected_normalized in generated_normalized:
        return "correct"

    return "needs_review"


def main():
    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        rows = list(csv.DictReader(file))

    counts = {
        "correct": 0,
        "incorrect": 0,
        "needs_review": 0
    }

    for row in rows:
        grade = grade_answer(
            row["expected_answer"],
            row["generated_answer"]
        )

        row["answer_grade"] = grade
        counts[grade] += 1

    fieldnames = list(rows[0].keys())

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n-----------------------------")
    print("Answer grading complete")
    print(f"Input: {INPUT_FILE.name}")
    print(f"Total questions: {len(rows)}")
    print(f"Correct (exact phrase): {counts['correct']}")
    print(f"Incorrect (explicit refusal/empty): {counts['incorrect']}")
    print(f"Needs manual review: {counts['needs_review']}")
    print(f"Output: {OUTPUT_FILE.name}")
    print("-----------------------------")

    print("\nQuestions requiring attention:")

    for row in rows:
        if row["answer_grade"] != "correct":
            print(
                f"  {row['id']}: "
                f"{row['answer_grade']} - "
                f"{row['question']}"
            )


if __name__ == "__main__":
    main()
