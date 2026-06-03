from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic
from aml_harness.package_common import check_optional_list, diagnostic, has_non_empty_child


METHOD_LOCATION_VALUES = ("client", "server")


def check_method_package(path: Path, root: ET.Element) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []

    for method in root.findall("Item"):
        if method.attrib.get("type") != "Method":
            continue
        if method.attrib.get("action") == "get":
            continue

        if method.attrib.get("action") == "add":
            for name in ("execution_allowed_to", "name"):
                if not has_non_empty_child(method, name):
                    diagnostics.append(diagnostic(path, "METHOD_REQUIRED001", f"Method/Method.{name} is required"))

        check_optional_list(
            path,
            diagnostics,
            method,
            "method_location",
            METHOD_LOCATION_VALUES,
            "METHOD_LIST001",
            "Method/Method.method_location must be one of: client, server",
        )

    return diagnostics
