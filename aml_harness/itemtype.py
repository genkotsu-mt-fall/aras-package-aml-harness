from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic
from aml_harness.package_common import (
    BEHAVIOR_VALUES,
    check_optional_list,
    diagnostic,
    has_non_empty_child,
    missing_child_message,
)


STANDARD_PROPERTY_EDIT_NAMES = {
    "classification",
    "created_by_id",
    "created_on",
    "current_state",
    "generation",
    "locked_by_id",
    "major_rev",
    "managed_by_id",
    "modified_by_id",
    "modified_on",
    "owned_by_id",
    "state",
    "superseded_date",
}


def check_itemtype_property_placement(path: Path, root: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    check_standard_property_placement = (
        path.parent.name == "ItemType" and path.suffix.lower() == ".xml"
    )
    skip_required_sequence_check = (
        path.parent.name == "ItemType" and path.name == "mpo_MassPromotion.xml"
    )

    for itemtype in root.iter("Item"):
        if itemtype.attrib.get("type") != "ItemType":
            continue
        if itemtype.attrib.get("action") not in {"add", "edit"}:
            continue

        for prop in itemtype.findall("Relationships/Item"):
            if prop.attrib.get("type") != "Property":
                continue
            if prop.attrib.get("action") != "add":
                continue

            property_name = _child_text(prop, "name")
            if (
                check_standard_property_placement
                and property_name in STANDARD_PROPERTY_EDIT_NAMES
            ):
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="ITEMTYPE001",
                        message=(
                            f"Standard property {property_name} uses action=\"add\". Change it to use "
                            'Property action="edit"'
                        ),
                    )
                )

            if (
                not skip_required_sequence_check
                and _child_text(prop, "data_type") == "sequence"
                and _child_text(prop, "is_required") == "1"
            ):
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="ITYPE_SEQUENCE001",
                        message=(
                            'Property with data_type="sequence" must not have '
                            "<is_required>1</is_required>. Remove <is_required> or set it to 0."
                        ),
                    )
                )

    return diagnostics


def check_itemtype_package(path: Path, root: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for itemtype in root.findall("Item"):
        if itemtype.attrib.get("type") != "ItemType":
            continue
        for relationship in itemtype.findall("Relationships/Item"):
            diagnostics.extend(check_itemtype_relationship(path, relationship))

    return diagnostics


def check_itemtype_relationship(path: Path, item: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    item_type = item.attrib.get("type")

    if item_type == "Server Event":
        if item.attrib.get("action") == "add":
            for name in ("event_version", "source_id"):
                if not has_non_empty_child(item, name):
                    diagnostics.append(
                        diagnostic(
                            path,
                            "ITEMTYPE_SERVER_EVENT_REQUIRED001",
                            missing_child_message(f"Server Event.{name}", name),
                        )
                    )
        check_optional_list(
            path,
            diagnostics,
            item,
            "behavior",
            BEHAVIOR_VALUES,
            "ITEMTYPE_SERVER_EVENT_LIST001",
            "Server Event.behavior has an invalid value",
        )
    elif item_type == "Item Action":
        if item.attrib.get("action") == "add" and not has_non_empty_child(item, "source_id"):
            diagnostics.append(
                diagnostic(
                    path,
                    "ITEMTYPE_ITEM_ACTION_REQUIRED001",
                    missing_child_message("Item Action.source_id", "source_id"),
                )
            )
        check_optional_list(
            path,
            diagnostics,
            item,
            "behavior",
            BEHAVIOR_VALUES,
            "ITEMTYPE_ITEM_ACTION_LIST001",
            "Item Action.behavior has an invalid value",
        )

    return diagnostics


def _child_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()
