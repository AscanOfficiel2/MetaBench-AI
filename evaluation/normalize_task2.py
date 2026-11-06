
"""
MetaBench-AI | Task 2 JSON Normalizer

Converts an AI agent's list-based DML results into
the canonical format required by grade_benchmark.py.

Preserves the original agent response unchanged.
"""

import argparse
import json
from pathlib import Path


def normalize(data):

    if data.get("task_id") != "mgx_crc_dml_negative_control":
        raise ValueError("Incorrect task_id")

    if not isinstance(data.get("results"), list):
        raise ValueError("Expected a list under 'results'")

    normalized = {
        "task_id": data["task_id"],
        "taxa": {}
    }

    for item in data["results"]:

        taxon = item["taxon"]

        if taxon in normalized["taxa"]:
            raise ValueError(
                f"Duplicate taxon: {taxon}"
            )

        normalized["taxa"][taxon] = {
            "estimate": item["estimate"],
            "ci_lower": item["ci_lower"],
            "ci_upper": item["ci_upper"],
            "ci_excludes_zero": item["ci_excludes_zero"]
        }

    return normalized


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("input_file")
    parser.add_argument("output_file")

    args = parser.parse_args()

    source = Path(args.input_file)
    destination = Path(args.output_file)

    data = json.loads(
        source.read_text(encoding="utf-8")
    )

    normalized = normalize(data)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    destination.write_text(
        json.dumps(normalized, indent=2) + "\n",
        encoding="utf-8"
    )

    print("Normalized output saved:", destination)


if __name__ == "__main__":
    main()
