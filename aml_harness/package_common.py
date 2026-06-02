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
        diagnostics.append(diagnostic(path, rule_id, message))


def has_non_empty_child(item: ET.Element, child_name: str) -> bool:
    return bool(child_text(item, child_name))


def child_text(item: ET.Element, child_name: str) -> str:
    child = item.find(child_name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def diagnostic(path: Path, rule_id: str, message: str) -> Diagnostic:
    return Diagnostic(file_path=str(path), rule_id=rule_id, message=message)
