from __future__ import annotations

import sys
from dataclasses import dataclass

from harness.shell import CommandResult, run_command


@dataclass(frozen=True)
class ValidationReport:
    passed: bool
    results: list[CommandResult]
    summary: str

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "results": [result.to_dict() for result in self.results],
            "summary": self.summary,
        }


def python_command(args: list[str]) -> list[str]:
    return [sys.executable, *args]


VALIDATORS: list[list[str]] = [
    python_command(["-m", "compileall", "-q", "aml_harness", "harness"]),
    python_command(["-m", "unittest"]),
    python_command(["-m", "aml_harness", "samples/good/base.xml"]),
]


def run_validators() -> ValidationReport:
    results: list[CommandResult] = []

    for command in VALIDATORS:
        result = run_command(command)
        results.append(result)

        if result.exit_code != 0:
            return ValidationReport(
                passed=False,
                results=results,
                summary=f"{' '.join(command)} failed with exit code {result.exit_code}.",
            )

    return ValidationReport(
        passed=True,
        results=results,
        summary="All validators passed.",
    )
