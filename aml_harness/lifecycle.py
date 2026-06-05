from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic
from aml_harness.package_common import diagnostic, has_non_empty_child, missing_child_message


def check_lifecycle_package(path: Path, root: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for item in root.findall("Item"):
        if item.attrib.get("type") != "Life Cycle Map":
            continue
        if item.attrib.get("action") == "add" and not has_non_empty_child(item, "name"):
            diagnostics.append(
                diagnostic(
                    path,
                    "LIFECYCLE_REQUIRED001",
                    missing_child_message("Life Cycle Map.name", "name"),
                )
            )

    return diagnostics
