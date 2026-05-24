from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from harness.records import IterationRecord, get_next_iteration, save_record
from harness.validators import run_validators


MAX_REPAIR_PROMPTS = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_repair_prompt(
    *,
    task: str,
    iteration: int,
    validation_summary: str,
    stdout: str,
    stderr: str,
) -> str:
    output_parts: list[str] = []

    if stderr.strip():
        output_parts.append("--- stderr ---\n" + stderr.strip())

    if stdout.strip():
        output_parts.append("--- stdout ---\n" + stdout.strip())

    error_output = "\n\n".join(output_parts)
    error_output = error_output[-8000:]

    return f"""
You are working in the aras-package-aml-harness Python repository.

# Task

{task}

# Current State

Validation failed.

# Iteration

{iteration}

# Validation Summary

{validation_summary}

# Relevant Output

```text
{error_output}
```

# Repository Rules

* Use only the Python standard library.
* Fix validation failures with minimal, safe changes.
* Do not edit unrelated files.
* Do not delete tests.
* Do not skip tests.
* Do not weaken assertions.
* Do not add external dependencies.
* Keep the existing project layout.

# Done When

These commands pass:

```powershell
python -m unittest
python -m aml_harness .\\samples\\good\\base.xml
```

Recommended check:

```powershell
python -m compileall -q aml_harness harness
python -m unittest
```

# Explain After Fixing

1. What failed
2. What changed
3. Why the change is safe
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manual Agent Loop harness for this Python repository"
    )
    parser.add_argument(
        "task_path",
        nargs="?",
        default="tasks/task-001.md",
        help="Path to the Markdown task file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task_path = Path(args.task_path)

    if not task_path.exists():
        print(f"Task file not found: {task_path}", file=sys.stderr)
        return 1

    task = task_path.read_text(encoding="utf-8")
    iteration = get_next_iteration()

    print(f"Running validators. iteration: {iteration}")
    validation = run_validators()

    if validation.passed:
        record_path, _ = save_record(
            IterationRecord(
                iteration=iteration,
                task_path=str(task_path),
                validation=validation,
                created_at=utc_now_iso(),
            )
        )
        print("All validators passed.")
        print(f"Saved record: {record_path}")
        return 0

    failed_result = validation.results[-1] if validation.results else None

    if iteration > MAX_REPAIR_PROMPTS:
        record_path, _ = save_record(
            IterationRecord(
                iteration=iteration,
                task_path=str(task_path),
                validation=validation,
                created_at=utc_now_iso(),
            )
        )
        print("Validation failed. Repair prompt limit reached.")
        print(f"Repair prompt limit: {MAX_REPAIR_PROMPTS}")
        print(f"Saved record: {record_path}")
        print("Stop the loop and inspect the diff and errors manually.")
        return 1

    next_prompt = build_repair_prompt(
        task=task,
        iteration=iteration,
        validation_summary=validation.summary,
        stdout=failed_result.stdout if failed_result else "",
        stderr=failed_result.stderr if failed_result else "",
    )

    record_path, prompt_path = save_record(
        IterationRecord(
            iteration=iteration,
            task_path=str(task_path),
            validation=validation,
            next_prompt=next_prompt,
            created_at=utc_now_iso(),
        )
    )

    print("Validation failed.")
    print(f"Saved record: {record_path}")

    if prompt_path:
        print(f"Saved repair prompt: {prompt_path}")

    print("")
    print("Next steps:")
    print("1. Open the generated prompt.md")
    print("2. Give it to Codex or Copilot Agent")
    print("3. Let the agent repair the code")
    print("4. Run this harness again")
    print("")

    if prompt_path:
        print("Codex example:")
        print(
            "codex exec "
            "--cd . "
            "--sandbox workspace-write "
            "--ask-for-approval never "
            f"- < {prompt_path}"
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
