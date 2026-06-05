from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic


BEHAVIOR_VALUES = ("float", "fixed", "hard_fixed", "hard_float")


def check_optional_list(
    path: Path,
    diagnostics: list[Diagnostic],
    item: ET.Element,
    child_name: str,
    allowed_values: tuple[str, ...],
    rule_id: str,
    message: str,
) -> None:
    value = child_text(item, child_name)
    if value and value not in allowed_values:
        subject = message.split(" has ")[0].split(" must ")[0]
        diagnostics.append(diagnostic(path, rule_id, invalid_list_message(subject, value, allowed_values)))


def invalid_list_message(subject: str, value: str, allowed_values: tuple[str, ...]) -> str:
    return (
        f'{subject} has invalid value "{value}". '
        f"Replace it with one of: {', '.join(allowed_values)}."
    )


def missing_child_message(subject: str, child_name: str) -> str:
    return (
        f"{subject} is missing or empty. "
        f"Add a non-empty <{child_name}> child."
    )


def has_non_empty_child(item: ET.Element, child_name: str) -> bool:
    return bool(child_text(item, child_name))


def child_text(item: ET.Element, child_name: str) -> str:
    child = item.find(child_name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def diagnostic(path: Path, rule_id: str, message: str) -> Diagnostic:
    return Diagnostic(file_path=str(path), rule_id=rule_id, message=message)
