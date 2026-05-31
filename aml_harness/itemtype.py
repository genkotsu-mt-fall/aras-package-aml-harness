from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic


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
                            f"Standard property {property_name} must use "
                            'Property action="edit"'
                        ),
                    )
                )

            if (
                _child_text(prop, "data_type") == "sequence"
                and _child_text(prop, "is_required") == "1"
            ):
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="ITYPE_SEQUENCE001",
                        message="Sequence property must not be required",
                    )
                )

    return diagnostics


def _child_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()
