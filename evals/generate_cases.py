from __future__ import annotations

import argparse
import csv
import json
from copy import deepcopy
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("evals/generated")
DEFAULT_DATASET = DEFAULT_OUTPUT_DIR / "generated_cases.jsonl"
SOURCE_FILES = [
    Path("samples/sales.csv"),
    Path("samples/operations_report.csv"),
    Path("samples/messy_sales.csv"),
]


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def mutate_rows(fieldnames: list[str], rows: list[dict[str, str]], variant: int) -> tuple[str, list[dict[str, str]]]:
    mutated = deepcopy(rows)
    mutation = variant % 3
    if mutation == 0 and mutated:
        mutated.append(deepcopy(mutated[0]))
        label = "duplicate_tail"
    elif mutation == 1 and mutated and fieldnames:
        mutated[0][fieldnames[0]] = ""
        label = "missing_head"
    else:
        fieldnames.reverse()
        relabeled = []
        for row in mutated:
            relabeled.append({field: row.get(field, "") for field in fieldnames})
        mutated = relabeled
        label = "reordered_columns"
    return label, mutated


def build_assertions(path: str) -> list[dict]:
    return [
        {"path": "sheet_count", "op": "eq", "value": 1},
        {"path": "summary.total_rows", "op": "gte", "value": 1},
        {"path": "summary.total_columns", "op": "gte", "value": 1},
        {
            "path": "recommendations",
            "op": "rubric_judge",
            "judge": "rubric",
            "value": ["numeric", "summary", "impute", "duplicate"],
            "threshold": 1,
        },
        {"path": "workbook_name", "op": "regex", "value": path.split("/")[-1].replace(".", r"\.")},
    ]


def generate_cases(output_dir: Path, copies_per_source: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    for source_path in SOURCE_FILES:
        fieldnames, rows = read_rows(source_path)
        for variant in range(copies_per_source):
            variant_fieldnames = list(fieldnames)
            label, mutated_rows = mutate_rows(variant_fieldnames, rows, variant)
            generated_name = f"{source_path.stem}_{label}_{variant}.csv"
            relative_path = output_dir / generated_name
            write_rows(relative_path, variant_fieldnames, mutated_rows)
            cases.append(
                {
                    "id": f"{source_path.stem}_{label}_{variant}",
                    "input": {"path": str(relative_path), "filename": generated_name},
                    "assertions": build_assertions(str(relative_path)),
                    "tags": ["generated", source_path.stem, label],
                }
            )

    dataset_path = output_dir / DEFAULT_DATASET.name
    dataset_path.write_text("\n".join(json.dumps(case) for case in cases) + "\n", encoding="utf-8")
    return dataset_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate synthetic eval cases at scale from sample CSVs.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for generated CSVs and JSONL.")
    parser.add_argument("--copies-per-source", type=int, default=10, help="Number of mutated cases per source file.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dataset_path = generate_cases(Path(args.output_dir), max(args.copies_per_source, 1))
    print(f"Generated dataset: {dataset_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
