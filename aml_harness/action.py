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

ACTION_REQUIRED_PROPERTIES = ("location", "target", "type", "name")


def check_action_list_values(path: Path, root: ET.Element) -> list[Diagnostic]:
    if path.parent.name != "Action" or path.suffix.lower() != ".xml":
        return []

    diagnostics: list[Diagnostic] = []

    for action in root.iter("Item"):
        if action.attrib.get("type") != "Action":
            continue

        if action.attrib.get("action") == "add":
            for element_name in ACTION_REQUIRED_PROPERTIES:
                if not _child_text(action, element_name):
                    diagnostics.append(
                        Diagnostic(
                            file_path=str(path),
                            rule_id="ACTION_REQUIRED001",
                            message=f"Action.{element_name} is required",
                        )
                    )

            if not _has_valid_method_reference(action):
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="ACTION_REQUIRED001",
                        message='Action.method must contain Method action="get" select="id" with name',
                    )
                )

        for element_name, rule_id, allowed_values, message in ACTION_LIST_PROPERTIES:
            value = _child_text(action, element_name)
            if value and value not in allowed_values:
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id=rule_id,
                        message=message,
                    )
                )

    return diagnostics


def _has_valid_method_reference(action: ET.Element) -> bool:
    method = action.find("method")
    if method is None:
        return False

    for item in method.findall("Item"):
        if (
            item.attrib.get("type") == "Method"
            and item.attrib.get("action") == "get"
            and item.attrib.get("select") == "id"
            and _child_text(item, "name")
        ):
            return True

    return False


def _child_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()
