from pathlib import Path
import xml.etree.ElementTree as ET

from aml_harness.base import Diagnostic


def check_package_items(path: Path, root: ET.Element) -> list[Diagnostic]:
    if path.suffix.lower() != ".xml":
        return []
    if "samples" in path.parts:
        return []

    parent_name = path.parent.name

    if parent_name == "ItemType":
        from aml_harness.itemtype import check_itemtype_package

        return check_itemtype_package(path, root)
    if parent_name == "Form":
        from aml_harness.form import check_form_package

        return check_form_package(path, root)
    if parent_name == "Method":
        from aml_harness.method import check_method_package

        return check_method_package(path, root)
    if parent_name == "RelationshipType":
        from aml_harness.relationshiptype import check_relationshiptype_package

        return check_relationshiptype_package(path, root)
    if parent_name == "List":
        from aml_harness.list import check_list_package

        return check_list_package(path, root)
    if parent_name == "Variable":
        from aml_harness.variable import check_variable_package

        return check_variable_package(path, root)
    if parent_name == "UserMessage":
        from aml_harness.usermessage import check_usermessage_package

        return check_usermessage_package(path, root)
    if parent_name == "Life Cycle Map":
        from aml_harness.lifecycle import check_lifecycle_package

        return check_lifecycle_package(path, root)

    return []
