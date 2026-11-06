
"""
MetaBench-AI | Multi-Model Evaluation Controller
Version: 0.2

Supported providers:
    - Google Gemini
    - OpenAI

Features:
    - Load benchmark prompts
    - Send API requests
    - Retry temporary API failures
    - Save responses and metadata
    - Record failures

IMPORTANT:
This version does not provide the models with datasets
or allow execution of R/Python code.

It is an API connectivity and prompt-delivery test,
NOT a valid scientific benchmark evaluation.
"""

import argparse
import json
import os
import random
import time

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from openai import OpenAI


# ==========================================================
# 1. PROJECT CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

PROMPTS = ROOT / "Task_prompts"
OUTPUT = ROOT / "evaluation_runs"

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)

load_dotenv(ROOT / ".env")

MODELS = {
    "gemini": "gemini-3.8-flash",
    "openai": "gpt-6"
}

MAX_ATTEMPTS = 4
MAX_BACKOFF = 30


# ==========================================================
# 2. LOAD TASK PROMPTS
# ==========================================================

def find_prompt(task):

    files = list(
        PROMPTS.rglob("*.md")
    )

    if not files:
        raise FileNotFoundError(
            "No Markdown task prompts found."
        )

    keywords = {
        "task1": ["task1", "batch"],
        "task2": ["task2", "dml"]
    }

    for keyword in keywords[task]:

        matches = [
            path for path in files
            if keyword in path.name.lower()
        ]

        if len(matches) == 1:
            return matches[0]

    raise FileNotFoundError(
        f"Could not uniquely identify {task}. "
        f"Available prompts: {[p.name for p in files]}"
    )


def load_task(task):

    prompt_path = find_prompt(task)

    prompt = prompt_path.read_text(
        encoding="utf-8"
    )

    return prompt, prompt_path


# ==========================================================
# 3. RETRY HELPER
# ==========================================================

def is_retryable_error(error):

    message = str(error).lower()

    retry_indicators = [
        "503",
        "502",
        "500",
        "504",
        "429",
        "service_unavailable",
        "high demand",
        "resource_exhausted",
        "rate limit",
        "temporarily unavailable",
        "timeout"
    ]

    return any(
        indicator in message
        for indicator in retry_indicators
    )


def execute_with_retry(request_function, provider):

    for attempt in range(
        1,
        MAX_ATTEMPTS + 1
    ):

        try:

            print(
                f"{provider} request "
                f"attempt {attempt}/{MAX_ATTEMPTS}"
            )

            return request_function()

        except Exception as error:

            if not is_retryable_error(error):
                raise

            if attempt == MAX_ATTEMPTS:
                raise RuntimeError(
                    f"{provider} request failed after "
                    f"{MAX_ATTEMPTS} attempts: {error}"
                ) from error

            delay = min(
                MAX_BACKOFF,
                2 ** attempt
                + random.uniform(0, 1)
            )

            print(
                f"Temporary {provider} API error."
            )

            print(
                f"Retrying in {delay:.1f} seconds..."
            )

            time.sleep(delay)


# ==========================================================
# 4. GEMINI API
# ==========================================================

def run_gemini(prompt):

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    client = genai.Client(
        api_key=api_key
    )

    def request():

        response = client.interactions.create(
            model=MODELS["gemini"],
            input=prompt
        )

        return response.output_text or ""

    return execute_with_retry(
        request,
        "Gemini"
    )


# ==========================================================
# 5. OPENAI API
# ==========================================================

def run_openai(prompt):

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing from .env"
        )

    client = OpenAI(
        api_key=api_key,
        max_retries=0
    )

    def request():

        response = client.responses.create(
            model=MODELS["openai"],
            input=prompt
        )

        return response.output_text or ""

    return execute_with_retry(
        request,
        "OpenAI"
    )


# ==========================================================
# 6. SELECT MODEL
# ==========================================================

def run_model(provider, prompt):

    if provider == "gemini":
        return run_gemini(prompt)

    if provider == "openai":
        return run_openai(prompt)

    raise ValueError(
        f"Unsupported provider: {provider}"
    )


# ==========================================================
# 7. SAVE RESPONSE AND METADATA
# ==========================================================

def save_result(
    provider,
    task,
    prompt_path,
    response,
    status,
    error_message=None
):

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    run_dir = (
        OUTPUT
        / provider
        / task
        / timestamp
    )

    run_dir.mkdir(
        parents=True,
        exist_ok=False
    )

    metadata = {
        "provider": provider,
        "model": MODELS[provider],
        "task": task,
        "timestamp_utc": timestamp,
        "prompt_file": str(
            prompt_path.relative_to(ROOT)
        ),
        "status": status,
        "execution_enabled": False,
        "dataset_access": False,
        "benchmark_valid": False,
        "error": error_message
    }

    (run_dir / "metadata.json").write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    (run_dir / "response.txt").write_text(
        response or "",
        encoding="utf-8"
    )

    return run_dir


# ==========================================================
# 8. COMMAND-LINE INTERFACE
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "MetaBench-AI multi-model "
            "evaluation controller"
        )
    )

    parser.add_argument(
        "--provider",
        choices=[
            "gemini",
            "openai"
        ],
        required=True
    )

    parser.add_argument(
        "--task",
        choices=[
            "task1",
            "task2"
        ],
        required=True
    )

    args = parser.parse_args()

    prompt, prompt_path = load_task(
        args.task
    )

    print("\n================================")
    print("METABENCH-AI")
    print("================================")

    print("Provider:", args.provider)
    print("Model:", MODELS[args.provider])
    print("Task:", args.task)
    print("Prompt:", prompt_path.name)

    print("\nSending API request...\n")

    status = "success"
    error_message = None
    response = ""

    try:

        response = run_model(
            args.provider,
            prompt
        )

        print("\n===== MODEL RESPONSE =====\n")
        print(response)

    except Exception as error:

        status = "failed"
        error_message = (
            f"{type(error).__name__}: {error}"
        )

        print("\n===== API ERROR =====\n")
        print(error_message)

    # Save successful and failed runs
    run_dir = save_result(
        provider=args.provider,
        task=args.task,
        prompt_path=prompt_path,
        response=response,
        status=status,
        error_message=error_message
    )

    print("\n===== RUN INFORMATION =====")
    print("Status:", status)
    print("Saved to:", run_dir)

    print(
        "\nNOTE: This is a prompt-delivery test. "
        "No datasets or execution tools were "
        "provided to the model."
    )

    if status == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
