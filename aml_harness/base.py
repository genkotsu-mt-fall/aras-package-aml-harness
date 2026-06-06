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


ALLOWED_ACTIONS = {"add", "edit", "delete", "get"}


def check_file(path: Path) -> list[Diagnostic]:
    if not path.exists():
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="FILE001",
                message=f"File does not exist: {path}. Create the file or check the path.",
            )
        ]

    if not path.is_file():
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="FILE002",
                message=f"Path is not a file: {path}. Specify an AML XML file path.",
            )
        ]

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="FILE003",
                message=f"Failed to read file {path}: {error}. Check permissions or fix the path.",
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

    if path.suffix.lower() == ".mf":
        from aml_harness.imports_manifest import check_imports_manifest

        return check_imports_manifest(path, root)

    diagnostics = check_base_aml(path, root)

    if root.tag == "AML" and path.parent.name == "Form" and path.suffix.lower() == ".xml":
        from aml_harness.form import check_form_propertytype

        diagnostics.extend(check_form_propertytype(path, root))

    if root.tag == "AML" and path.parent.name == "Action" and path.suffix.lower() == ".xml":
        from aml_harness.action import check_action_list_values

        diagnostics.extend(check_action_list_values(path, root))

    if root.tag == "AML" and path.suffix.lower() == ".xml":
        from aml_harness.itemtype import check_itemtype_property_placement

        diagnostics.extend(check_itemtype_property_placement(path, root))

        from aml_harness.package_checks import check_package_items

        diagnostics.extend(check_package_items(path, root))

    return diagnostics


def check_base_aml(path: Path, root: ET.Element) -> list[Diagnostic]:
    if root.tag != "AML":
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="AML001",
                message=f"Root element is <{root.tag}>. Replace it with <AML>.",
            )
        ]

    children = list(root)

    if not children:
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="AML002",
                message="<AML> has no <Item> children. Add at least one <Item type=\"...\" action=\"...\"> child.",
            )
        ]

    diagnostics: list[Diagnostic] = []

    for child in children:
        if child.tag != "Item":
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="AML003",
                    message=(
                        f"<AML> child is <{child.tag}>. Expected <Item>. "
                        "Replace it with <Item> or move into <Item>."
                    ),
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
    where = item.attrib.get("where")

    if not item_type:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML004",
                message='<Item> type attribute is missing. Add type="...".',
            )
        )

    if not action:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML005",
                message=(
                    '<Item> is missing the action attribute. Add action="add", '
                    'action="edit", action="delete", or action="get".'
                ),
            )
        )
    elif action not in ALLOWED_ACTIONS:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML005",
                message=(
                    f'<Item action> has invalid value "{action}". '
                    'Replace it with one of: add, edit, delete, get.'
                ),
            )
        )

    if action in {"add", "edit"} and not item_id:
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML006",
                message=f'<Item action="{action}"> id attribute is missing. Add id="...".',
            )
        )

    if action == "delete" and not _has_non_empty_value(where):
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="AML007",
                message='<Item action="delete"> where attribute is missing or empty. Add where="...".',
            )
        )

    return diagnostics


def _has_non_empty_value(value: str | None) -> bool:
    return value is not None and bool(value.strip())
