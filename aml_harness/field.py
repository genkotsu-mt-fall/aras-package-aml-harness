from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic
from aml_harness.package_common import (
    BEHAVIOR_VALUES,
    check_optional_list,
    diagnostic,
    has_non_empty_child,
)


BODY_LIST_PROPERTIES = (
    ("behavior", BEHAVIOR_VALUES),
    ("bg_attach", ("fixed", "scroll")),
    ("bg_repeat", ("no-repeat", "repeat", "repeat-x", "repeat-y")),
)

FIELD_LIST_PROPERTIES = (
    ("behavior", BEHAVIOR_VALUES),
    (
        "field_type",
        (
            "button",
            "checkbox",
            "checkbox list",
            "class structure",
            "color",
            "color list",
            "date",
            "dropdown",
            "file item",
            "formatted text",
            "groupbox",
            "html",
            "image",
            "item",
            "label",
            "listbox multi select",
            "listbox single select",
            "ml_string",
            "nested form",
            "password",
            "radio button list",
            "textarea",
            "text",
        ),
    ),
    ("font_weight", ("bold", "normal")),
    ("label_position", ("bottom", "left", "right", "top")),
    ("display_length_unit", ("%", "px")),
    ("clip_overflow", ("hidden", "visible")),
    ("orientation", ("horizontal", "vertical")),
    ("positioning", ("absolute", "relative", "static")),
    ("text_align", ("center", "left", "right")),
)

FIELD_EVENT_VALUES = ("onblur", "onfocus", "onchange", "onclick", "ondblclick", "onselect")
FORM_EVENT_VALUES = (
    "onformpopulated",
    "onload",
    "onbeforeunload",
    "onunload",
    "onresize",
    "onbeforeprint",
    "onafterprint",
    "oncontextmenu",
    "onkeydown",
    "onkeyup",
    "onmouseover",
    "onmousedown",
    "onmouseup",
    "onmousemove",
)


def check_body(path: Path, body: ET.Element, required_rule: str, list_rule: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    if body.attrib.get("action") == "add" and not has_non_empty_child(body, "source_id"):
        diagnostics.append(diagnostic(path, required_rule, "Body.source_id is required"))

    for name, values in BODY_LIST_PROPERTIES:
        check_optional_list(path, diagnostics, body, name, values, list_rule, f"Body.{name} has an invalid value")

    return diagnostics


def check_field(path: Path, field: ET.Element, required_rule: str, list_rule: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    if field.attrib.get("action") == "add":
        for name in ("show_help", "source_id"):
            if not has_non_empty_child(field, name):
                diagnostics.append(diagnostic(path, required_rule, f"Field.{name} is required"))

    for name, values in FIELD_LIST_PROPERTIES:
        check_optional_list(path, diagnostics, field, name, values, list_rule, f"Field.{name} has an invalid value")

    return diagnostics


def check_field_event(
    path: Path,
    event: ET.Element,
    required_rule: str,
    list_rule: str,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    if event.attrib.get("type") != "Field Event":
        return diagnostics
    if event.attrib.get("action") == "add" and not has_non_empty_child(event, "source_id"):
        diagnostics.append(diagnostic(path, required_rule, "Field Event.source_id is required"))

    check_optional_list(
        path,
        diagnostics,
        event,
        "field_event",
        FIELD_EVENT_VALUES,
        list_rule,
        "Field Event.field_event has an invalid value",
    )
    check_optional_list(
        path,
        diagnostics,
        event,
        "behavior",
        BEHAVIOR_VALUES,
        list_rule,
        "Field Event.behavior has an invalid value",
    )

    return diagnostics


def check_form_event(
    path: Path,
    event: ET.Element,
    required_rule: str,
    list_rule: str,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    if event.attrib.get("action") == "add" and not has_non_empty_child(event, "source_id"):
        diagnostics.append(diagnostic(path, required_rule, "Form Event.source_id is required"))

    check_optional_list(
        path,
        diagnostics,
        event,
        "form_event",
        FORM_EVENT_VALUES,
        list_rule,
        "Form Event.form_event has an invalid value",
    )
    check_optional_list(
        path,
        diagnostics,
        event,
        "behavior",
        BEHAVIOR_VALUES,
        list_rule,
        "Form Event.behavior has an invalid value",
    )

    return diagnostics
