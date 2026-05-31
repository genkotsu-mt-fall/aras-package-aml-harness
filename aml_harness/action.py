from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic


ACTION_LIST_PROPERTIES = (
    (
        "location",
        "ACTION_LIST001",
        ("client", "server"),
        "Action.location must be one of: client, server",
    ),
    (
        "target",
        "ACTION_LIST002",
        ("main", "window", "one window", "none"),
        "Action.target must be one of: main, window, one window, none",
    ),
    (
        "type",
        "ACTION_LIST003",
        ("generic", "item", "itemtype", "url"),
        "Action.type must be one of: generic, item, itemtype, url",
    ),
)


def check_action_list_values(path: Path, root: ET.Element) -> list[Diagnostic]:
    if path.parent.name != "Action" or path.suffix.lower() != ".xml":
        return []

    diagnostics: list[Diagnostic] = []

    for action in root.iter("Item"):
        if action.attrib.get("type") != "Action":
            continue

        for element_name, rule_id, allowed_values, message in ACTION_LIST_PROPERTIES:
            value = _child_text(action, element_name)
            if value not in allowed_values:
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id=rule_id,
                        message=message,
                    )
                )

    return diagnostics


def _child_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()
