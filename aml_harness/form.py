from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic
from aml_harness.field import (
    check_body,
    check_field,
    check_field_event,
    check_form_event,
)
from aml_harness.package_common import diagnostic, has_non_empty_child


STANDARD_PROPERTIES = {
    "classification",
    "config_id",
    "created_by_id",
    "created_on",
    "css",
    "current_state",
    "generation",
    "id",
    "is_current",
    "is_released",
    "keyed_name",
    "locked_by_id",
    "major_rev",
    "managed_by_id",
    "minor_rev",
    "modified_by_id",
    "modified_on",
    "new_version",
    "not_lockable",
    "owned_by_id",
    "permission_id",
    "state",
    "team_id",
    "effective_date",
    "release_date",
    "superseded_date",
}


def check_form_propertytype(path: Path, root: ET.Element) -> list[Diagnostic]:
    if path.parent.name != "Form" or path.suffix.lower() != ".xml":
        return []

    add_fields = _form_add_fields_by_id(root)
    diagnostics: list[Diagnostic] = []

    for field in add_fields.values():
        propertytype_id = field.find("propertytype_id")

        if propertytype_id is not None:
            if not _is_32_char_guid(propertytype_id.text):
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="FORM001",
                        message="Field action=\"add\" propertytype_id must be a 32 character GUID",
                    )
                )

            property_name = propertytype_id.attrib.get("keyed_name", "")
            if property_name in STANDARD_PROPERTIES:
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="FORM002",
                        message=(
                            f"Standard property {property_name} Field action=\"add\" "
                            "must not contain propertytype_id"
                        ),
                    )
                )

    for field_edit in _field_edits(root):
        property_item = field_edit.find("propertytype_id/Item")
        if property_item is None:
            continue

        property_name = _child_text(property_item, "name")
        if property_name not in STANDARD_PROPERTIES:
            continue

        field_id = field_edit.attrib.get("id", "")
        add_field = add_fields.get(field_id)

        if add_field is None:
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="FORM003",
                    message=(
                        f"Standard property {property_name} requires matching "
                        "Field action=\"add\""
                    ),
                )
            )
            continue

        if (
            property_item.attrib.get("type") != "Property"
            or property_item.attrib.get("action") != "get"
            or property_item.attrib.get("select") != "id"
        ):
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="FORM004",
                    message=(
                        "Field action=\"edit\" propertytype_id must contain "
                        "Property action=\"get\" select=\"id\""
                    ),
                )
            )
            continue

        source_id = property_item.find("source_id")
        if source_id is None or source_id.attrib.get("type") != "ItemType":
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="FORM006",
                    message="Property source_id must have type=\"ItemType\"",
                )
            )

    return diagnostics


def check_form_package(path: Path, root: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for form in root.findall("Item"):
        if form.attrib.get("type") != "Form":
            continue

        if form.attrib.get("action") == "add":
            for name in ("height", "width", "name"):
                if not has_non_empty_child(form, name):
                    diagnostics.append(diagnostic(path, "FORM_REQUIRED001", f"Form/Form.{name} is required"))

        for relationship in form.findall("Relationships/Item"):
            diagnostics.extend(check_form_relationship(path, relationship))

    return diagnostics


def check_form_relationship(path: Path, item: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    item_type = item.attrib.get("type")

    if item_type == "Body":
        diagnostics.extend(check_body(path, item, "FORM_BODY_REQUIRED001", "FORM_BODY_LIST001"))
        for field in item.findall("Relationships/Item"):
            if field.attrib.get("type") == "Field":
                diagnostics.extend(check_field(path, field, "FORM_FIELD_REQUIRED001", "FORM_FIELD_LIST001"))
                for event in field.findall("Relationships/Item"):
                    diagnostics.extend(
                        check_field_event(
                            path,
                            event,
                            "FORM_FIELD_EVENT_REQUIRED001",
                            "FORM_FIELD_EVENT_LIST001",
                        )
                    )
    elif item_type == "Field":
        diagnostics.extend(check_field(path, item, "FORM_FIELD_REQUIRED001", "FORM_FIELD_LIST001"))
        for event in item.findall("Relationships/Item"):
            diagnostics.extend(
                check_field_event(
                    path,
                    event,
                    "FORM_FIELD_EVENT_REQUIRED001",
                    "FORM_FIELD_EVENT_LIST001",
                )
            )
    elif item_type == "Form Event":
        diagnostics.extend(check_form_event(path, item, "FORM_FORM_EVENT_REQUIRED001", "FORM_FORM_EVENT_LIST001"))

    return diagnostics


def _field_edits(root: ET.Element) -> list[ET.Element]:
    field_edits: list[ET.Element] = []

    for item in root.findall("Item"):
        if item.attrib.get("type") == "Field" and item.attrib.get("action") == "edit":
            field_edits.append(item)

    return field_edits


def _form_add_fields_by_id(root: ET.Element) -> dict[str, ET.Element]:
    fields: dict[str, ET.Element] = {}

    for form in root.findall("Item"):
        if form.attrib.get("type") != "Form" or form.attrib.get("action") != "add":
            continue

        for body in form.findall("Relationships/Item"):
            if body.attrib.get("type") != "Body" or body.attrib.get("action") != "add":
                continue

            for field in body.findall("Relationships/Item"):
                if field.attrib.get("type") == "Field" and field.attrib.get("action") == "add":
                    field_id = field.attrib.get("id")
                    if field_id:
                        fields[field_id] = field

    return fields


def _child_text(element: ET.Element, name: str) -> str:
    child = element.find(name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def _is_32_char_guid(value: str | None) -> bool:
    if value is None:
        return False

    text = value.strip()
    if len(text) != 32:
        return False

    for char in text:
        if char not in "0123456789abcdefABCDEF":
            return False

    return True
