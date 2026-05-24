from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from harness.validators import ValidationReport


RUNS_DIR = Path("runs")
ITERATION_DIR_PATTERN = re.compile(r"^iteration-(\d+)$")


@dataclass(frozen=True)
class IterationRecord:
    iteration: int
    task_path: str
    validation: ValidationReport
    created_at: str
    next_prompt: str | None = None

    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "task_path": self.task_path,
            "validation": self.validation.to_dict(),
            "created_at": self.created_at,
            "next_prompt": self.next_prompt,
        }


def get_next_iteration() -> int:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    numbers: list[int] = []

    for path in RUNS_DIR.iterdir():
        if not path.is_dir():
            continue

        match = ITERATION_DIR_PATTERN.match(path.name)
        if match:
            numbers.append(int(match.group(1)))

    if not numbers:
        return 1

    return max(numbers) + 1


def save_record(record: IterationRecord) -> tuple[Path, Path | None]:
    iteration_dir = RUNS_DIR / f"iteration-{record.iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    record_path = iteration_dir / "record.json"
    record_path.write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    prompt_path: Path | None = None
    if record.next_prompt:
        prompt_path = iteration_dir / "prompt.md"
        prompt_path.write_text(record.next_prompt + "\n", encoding="utf-8")

    return record_path, prompt_path
