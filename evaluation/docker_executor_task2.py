
"""
MetaBench-AI | Task 2 Docker Executor

Executes Gemini-generated Python analysis code
inside the restricted metabench-task2 container.
"""

import argparse
import json
import subprocess
import uuid

from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "Task2_input"
WORKSPACE = ROOT / "evaluation" / "agent_workspace"
OUTPUT = ROOT / "evaluation" / "agent_outputs"

IMAGE = "metabench-task2"
TIMEOUT_SECONDS = 1800

WORKSPACE.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)


def execute_python(script_name):

    script_path = (WORKSPACE / script_name).resolve()

    if not script_path.is_file():
        raise FileNotFoundError(
            f"Script not found: {script_path}"
        )

    if script_path.parent != WORKSPACE.resolve():
        raise ValueError("Invalid script path")

    run_id = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    run_id += "_" + uuid.uuid4().hex[:8]

    run_dir = OUTPUT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    container_name = "metabench-task2-" + uuid.uuid4().hex[:12]

    command = [
        "docker", "run",
        "--name", container_name,
        "--rm",
        "--network", "none",
        "--cpus", "2",
        "--memory", "4g",
        "--pids-limit", "128",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--tmpfs", "/tmp:rw,nosuid,size=512m",
        "-v", f"{INPUT}:/workspace/Task2_input:ro",
        "-v", f"{WORKSPACE}:/workspace/scripts:ro",
        "-v", f"{run_dir}:/workspace/output:rw",
        "-w", "/workspace",
        IMAGE,
        "python",
        f"/workspace/scripts/{script_name}"
    ]

    print("Starting Task 2 Docker execution...")
    print("Container:", container_name)
    print("Timeout:", TIMEOUT_SECONDS, "seconds")

    timed_out = False

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False
        )

        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode

    except subprocess.TimeoutExpired as error:

        timed_out = True
        exit_code = 124

        stdout = (
            error.stdout.decode(errors="replace")
            if isinstance(error.stdout, bytes)
            else (error.stdout or "")
        )

        stderr = (
            error.stderr.decode(errors="replace")
            if isinstance(error.stderr, bytes)
            else (error.stderr or "")
        )

        stderr += "\nExecution timeout exceeded."

        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

    # Save logs
    (run_dir / "stdout.txt").write_text(
        stdout,
        encoding="utf-8"
    )

    (run_dir / "stderr.txt").write_text(
        stderr,
        encoding="utf-8"
    )

    metadata = {
        "script": script_name,
        "container": container_name,
        "image": IMAGE,
        "timeout_seconds": TIMEOUT_SECONDS,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "timestamp_utc": run_id
    }

    (run_dir / "execution_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8"
    )

    print("\n===== STDOUT =====")
    print(stdout)

    print("\n===== STDERR =====")
    print(stderr)

    print("\nExit code:", exit_code)
    print("Logs saved:", run_dir)

    return exit_code


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--script",
        required=True
    )

    args = parser.parse_args()

    exit_code = execute_python(args.script)

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
