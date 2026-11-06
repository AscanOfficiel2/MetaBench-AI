
"""
MetaBench-AI | Task 2 Gemini Agent
DML and Negative-Control Evaluation

Generates Python analysis code for human review.
Execution takes place separately inside Docker.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# ==========================================================
# CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

PROMPT_FILE = (
    ROOT / "Task_prompts"
    / "task2_prompt_dml_negative_control.md"
)

WORKSPACE = ROOT / "evaluation" / "agent_workspace"
RUNS = ROOT / "evaluation_runs"

MODEL = "gemini-3.8-flash"

WORKSPACE.mkdir(parents=True, exist_ok=True)
RUNS.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")


# ==========================================================
# GEMINI CLIENT
# ==========================================================

def get_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY missing from .env"
        )

    return genai.Client(api_key=api_key)


# ==========================================================
# EXTRACT PYTHON CODE
# ==========================================================

def extract_python_code(response):

    match = re.search(
        r"```(?:python|py)\s*\n(.*?)```",
        response,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not match:
        raise ValueError(
            "Gemini did not return a fenced Python script."
        )

    return match.group(1).strip() + "\n"


# ==========================================================
# GENERATE TASK 2 ANALYSIS
# ==========================================================

def main():

    if not PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"Task prompt missing: {PROMPT_FILE}"
        )

    task_prompt = PROMPT_FILE.read_text(
        encoding="utf-8"
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S_%f")

    run_dir = (
        RUNS / "gemini" / "task2_agent" / timestamp
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False
    )

    instructions = f"""
You are an AI computational biologist performing
a metagenomics benchmark.

SCIENTIFIC TASK:

{task_prompt}

AVAILABLE DATASETS:

/workspace/Task2_input/TPM_clr_batch_corrected_v2.csv

/workspace/Task2_input/metadata_final_matched.csv

The abundance matrix is already CLR-transformed
and batch-corrected.

Do not repeat batch correction or CLR transformation.

AVAILABLE PYTHON PACKAGES:

numpy
pandas
scipy
scikit-learn
econml

REQUIREMENTS:

1. Load the provided datasets.
2. Align sample identifiers correctly.
3. Handle missing sample identifiers appropriately.
4. Select Healthy and Cancer samples only.
5. Encode the binary outcome correctly.
6. Perform the requested DML analyses separately
   for both taxa.
7. Use the specified random seed and model settings.
8. Calculate the estimates and confidence intervals.
9. Print the final answer as a valid JSON object.
10. Do not invent numerical results.

Use the JSON field names and structure specified
in the benchmark task prompt.

The script must be self-contained and executable
inside the provided Docker environment.

Do not access the internet, reference answers,
other host files or environment secrets.

Only read the specified datasets.

Write generated files only to /workspace/output.

Return ONLY a complete Python script inside
a fenced Python code block.
"""

    client = get_client()

    print("\n================================")
    print("METABENCH-AI TASK 2")
    print("================================")

    print("Provider: Gemini")
    print("Model:", MODEL)
    print("Task: DML Negative-Control Evaluation")

    print("\nRequesting Python script from Gemini...")

    response = client.interactions.create(
        model=MODEL,
        input=instructions
    )

    text = response.output_text or ""

    (run_dir / "generation_response.txt").write_text(
        text,
        encoding="utf-8"
    )

    code = extract_python_code(text)

    script_name = f"gemini_task2_{timestamp}.py"

    script_path = WORKSPACE / script_name

    script_path.write_text(
        code,
        encoding="utf-8"
    )

    metadata = {
        "provider": "gemini",
        "model": MODEL,
        "task": "mgx_crc_dml_negative_control",
        "timestamp_utc": timestamp,
        "script_name": script_name,
        "execution_status": "awaiting_human_review",
        "reference_access": False,
        "execution_enabled": False
    }

    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8"
    )

    print("\n===== GENERATION COMPLETED =====")
    print("Script saved:", script_path)
    print("Run directory:", run_dir)

    print("\nReview the generated Python script.")
    print("No AI-generated code has been executed.")


if __name__ == "__main__":
    main()
