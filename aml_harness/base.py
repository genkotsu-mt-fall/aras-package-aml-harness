from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Diagnostic:
    file_path: str
    rule_id: str
    message: str
    line: int = 1
    column: int = 1
    severity: str = "error"


ALLOWED_ACTIONS = {"add", "edit"}


def check_file(path: Path) -> list[Diagnostic]:
    if not path.exists():
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="FILE001",
                message="File does not exist",
            )
        ]

    if not path.is_file():
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="FILE002",
                message="Path is not a file",
            )
        ]

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="FILE003",
                message=f"Failed to read file: {error}",
            )
        ]

    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        line, column = error.position
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="AML000",
                message=f"Invalid XML: {error}",
                line=line,
                column=column,
            )
        ]

    return check_base_aml(path, root)


def check_base_aml(path: Path, root: ET.Element) -> list[Diagnostic]:
    if root.tag != "AML":
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="AML001",
                message="Root element must be <AML>",
            )
        ]

    children = list(root)

    if not children:
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="AML002",
                message="<AML> must contain at least one <Item>",
            )
        ]

    diagnostics: list[Diagnostic] = []

    for child in children:
        if child.tag != "Item":
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="AML003",
                    message=f"<AML> child must be <Item>, but found <{child.tag}>",
                )
            )
            continue

        diagnostics.extend(check_item(path, child))

    return diagnostics


def check_item(path: Path, item: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    item_type = item.attrib.get("type")
    action = item.attrib.get("action")
    item_id = item.attrib.get("id")

    if not item_type:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML004",
                message="<Item> must have type attribute",
            )
        )

    if not action:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML005",
                message="<Item> must have action attribute",
            )
        )
    elif action not in ALLOWED_ACTIONS:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML005",
                message="<Item> action must be add or edit",
            )
        )

    if not item_id:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML006",
                message="<Item> must have id attribute",
            )
        )

    return diagnostics
