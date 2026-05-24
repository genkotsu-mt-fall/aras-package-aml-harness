from __future__ import annotations

import os
import subprocess
import time
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool

    def to_dict(self) -> dict:
        return asdict(self)


def run_command(
    command: list[str],
    cwd: str | None = None,
    timeout_seconds: int = 120,
) -> CommandResult:
    started_at = time.monotonic()
    env = {
        **os.environ,
        "CI": "true",
        "PYTHONUNBUFFERED": "1",
    }

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )

        return CommandResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=int((time.monotonic() - started_at) * 1000),
            timed_out=False,
        )
    except subprocess.TimeoutExpired as error:
        return CommandResult(
            command=command,
            exit_code=None,
            stdout=error.stdout or "",
            stderr=(error.stderr or "") + f"\nTimed out after {timeout_seconds} seconds.",
            duration_ms=int((time.monotonic() - started_at) * 1000),
            timed_out=True,
        )
    except OSError as error:
        return CommandResult(
            command=command,
            exit_code=1,
            stdout="",
            stderr=str(error),
            duration_ms=int((time.monotonic() - started_at) * 1000),
            timed_out=False,
        )
