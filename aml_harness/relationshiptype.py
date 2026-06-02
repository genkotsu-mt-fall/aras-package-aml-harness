from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic
from aml_harness.field import (
    check_body,
    check_field,
    check_field_event,
    check_form_event,
)
from aml_harness.itemtype import check_itemtype_relationship


def check_relationshiptype_package(path: Path, root: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for reltype in root.findall("Item"):
        if reltype.attrib.get("type") != "RelationshipType":
            continue
        for itemtype in reltype.findall("relationship_id/Item"):
            if itemtype.attrib.get("type") != "ItemType":
                continue
            for relationship in itemtype.findall("Relationships/Item"):
                diagnostics.extend(check_relationshiptype_relationship(path, relationship))

    return diagnostics


def check_relationshiptype_relationship(path: Path, item: ET.Element) -> list[Diagnostic]:
    item_type = item.attrib.get("type")

    if item_type in {"Server Event", "Item Action"}:
        diagnostics = check_itemtype_relationship(path, item)
        return [_rewrite_rule_id(diagnostic) for diagnostic in diagnostics]
    if item_type == "Body":
        return _check_body_with_nested_fields(path, item)
    if item_type == "Field":
        return check_field(path, item, "RELTYPE_FIELD_REQUIRED001", "RELTYPE_FIELD_LIST001")
    if item_type == "Field Event":
        return check_field_event(path, item, "RELTYPE_FIELD_EVENT_REQUIRED001", "RELTYPE_FIELD_EVENT_LIST001")
    if item_type == "Form Event":
        return check_form_event(path, item, "RELTYPE_FORM_EVENT_REQUIRED001", "RELTYPE_FORM_EVENT_LIST001")

    return []


def _check_body_with_nested_fields(path: Path, body: ET.Element) -> list[Diagnostic]:
    diagnostics = check_body(path, body, "RELTYPE_BODY_REQUIRED001", "RELTYPE_BODY_LIST001")

    for field in body.findall("Relationships/Item"):
        if field.attrib.get("type") != "Field":
            continue
        diagnostics.extend(check_field(path, field, "RELTYPE_FIELD_REQUIRED001", "RELTYPE_FIELD_LIST001"))
        for event in field.findall("Relationships/Item"):
            diagnostics.extend(
                check_field_event(
                    path,
                    event,
                    "RELTYPE_FIELD_EVENT_REQUIRED001",
                    "RELTYPE_FIELD_EVENT_LIST001",
                )
            )

    return diagnostics


def _rewrite_rule_id(diagnostic: Diagnostic) -> Diagnostic:
    return Diagnostic(
        file_path=diagnostic.file_path,
        rule_id=diagnostic.rule_id.replace("ITEMTYPE_", "RELTYPE_"),
        message=diagnostic.message,
        line=diagnostic.line,
        column=diagnostic.column,
        severity=diagnostic.severity,
    )
