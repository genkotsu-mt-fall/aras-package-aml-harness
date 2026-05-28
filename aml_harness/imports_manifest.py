from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic

_DOT_PATH_VALUES = {".\\", "./", "."}


def check_imports_manifest(path: Path, root: ET.Element) -> list[Diagnostic]:
    """Check an imports.mf file for structural validity."""
    diagnostics: list[Diagnostic] = []

    # IMPORTS001: root must be <imports>
    if root.tag != "imports":
        return [
            Diagnostic(
                file_path=str(path),
                rule_id="IMPORTS001",
                message="Root element must be <imports>",
            )
        ]

    children = list(root)

    # IMPORTS002: at least one <package>
    if not any(child.tag == "package" for child in children):
        diagnostics.append(
            Diagnostic(
                file_path=str(path),
                rule_id="IMPORTS002",
                message="<imports> must contain at least one <package>",
            )
        )

    # IMPORTS003: all direct children must be <package>
    for child in children:
        if child.tag != "package":
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="IMPORTS003",
                    message=f"<imports> child must be <package>, but found <{child.tag}>",
                )
            )

    if diagnostics:
        return diagnostics

    manifest_dir = path.parent

    for package in children:
        # IMPORTS004: <package> must have name attribute
        name = package.attrib.get("name")
        if not name:
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="IMPORTS004",
                    message="<package> must have name attribute",
                )
            )

        # IMPORTS005: <package> must have path attribute
        pkg_path = package.attrib.get("path")
        if pkg_path is None:
            diagnostics.append(
                Diagnostic(
                    file_path=str(path),
                    rule_id="IMPORTS005",
                    message="<package> must have path attribute",
                )
            )
        elif pkg_path not in _DOT_PATH_VALUES:
            # IMPORTS006: path (non-dot) must exist relative to imports.mf
            resolved = manifest_dir / pkg_path.replace("\\", "/")
            if not resolved.exists():
                diagnostics.append(
                    Diagnostic(
                        file_path=str(path),
                        rule_id="IMPORTS006",
                        message=f"<package> path does not exist: {pkg_path}",
                    )
                )

        # IMPORTS007: direct <dependson> must have name attribute
        for child in package:
            if child.tag == "dependson":
                if not child.attrib.get("name"):
                    diagnostics.append(
                        Diagnostic(
                            file_path=str(path),
                            rule_id="IMPORTS007",
                            message="<dependson> must have name attribute",
                        )
                    )

    return diagnostics
