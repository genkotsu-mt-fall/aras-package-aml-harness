from pathlib import Path
import glob
import sys

from aml_harness.base import Diagnostic, check_file


def expand_paths(args: list[str]) -> list[Path]:
    paths: list[Path] = []

    for arg in args:
        matches = glob.glob(arg, recursive=True)

        if matches:
            paths.extend(Path(match) for match in matches)
        else:
            paths.append(Path(arg))

    return paths


def format_diagnostic(diagnostic: Diagnostic) -> str:
    return (
        f"{diagnostic.file_path}:{diagnostic.line}:{diagnostic.column} "
        f"{diagnostic.severity} {diagnostic.rule_id} {diagnostic.message}"
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print("Usage: aml-harness <xml-file-or-glob> [...]", file=sys.stderr)
        return 2

    paths = expand_paths(args)
    diagnostics: list[Diagnostic] = []

    for path in paths:
        diagnostics.extend(check_file(path))

    for diagnostic in diagnostics:
        print(format_diagnostic(diagnostic))

    if diagnostics:
        print(f"AML base check failed. {len(diagnostics)} error(s).")
        return 1

    print(f"AML base check passed. {len(paths)} file(s) checked.")
    return 0
