from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aml_harness.base import Diagnostic, check_file


ITEMTYPE_ID = "CCF205347C814DD1AF056875E0A880AC"


class ItemTypeRelationshipCheckTests(unittest.TestCase):
    def check_xml(self, parent_dir: str, xml: str) -> list[Diagnostic]:
        with TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir) / parent_dir
            directory.mkdir(parents=True)
            path = directory / "sample.xml"
            path.write_text(xml, encoding="utf-8")
            return check_file(path)

    def assert_xml_passes(self, parent_dir: str, xml: str):
        diagnostics = self.check_xml(parent_dir, xml)
        self.assertEqual([], diagnostics, diagnostics)

    def assert_xml_reports_rules(self, parent_dir: str, xml: str, expected_rule_ids: list[str]):
        diagnostics = self.check_xml(parent_dir, xml)
        self.assertEqual(expected_rule_ids, [diagnostic.rule_id for diagnostic in diagnostics], diagnostics)

    def itemtype_with_relationship(self, relationship_xml: str) -> str:
        return f"""<AML>
  <Item type="ItemType" id="{ITEMTYPE_ID}" action="add">
    <name>CAD</name>
    <Relationships>
{relationship_xml}
    </Relationships>
  </Item>
</AML>"""

    def server_event(self, extra_xml: str = "", action: str = "add") -> str:
        return f"""      <Item type="Server Event" id="C17B14040CC54E1B8647A220C5188E3A" action="{action}">
        {extra_xml}
      </Item>"""

    def item_action(self, extra_xml: str = "") -> str:
        return f"""      <Item type="Item Action" id="81BAAD8CEBF44188B48233364D886734" action="add">
        {extra_xml}
      </Item>"""

    def test_task_018_no_001_server_event_required_fields_pass(self):
        self.assert_xml_passes(
            "ItemType",
            self.itemtype_with_relationship(
                self.server_event(
                    f"""<event_version>version_1</event_version>
        <server_event>onAfterCopy</server_event>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                )
            ),
        )

    def test_task_018_no_002_003_server_event_missing_required_fields(self):
        self.assert_xml_reports_rules(
            "ItemType",
            self.itemtype_with_relationship(
                self.server_event(
                    f"""<server_event>onAfterCopy</server_event>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                )
            ),
            ["ITEMTYPE_SERVER_EVENT_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "ItemType",
            self.itemtype_with_relationship(
                self.server_event(
                    """<event_version>version_1</event_version>
        <server_event>onAfterCopy</server_event>"""
                )
            ),
            ["ITEMTYPE_SERVER_EVENT_REQUIRED001"],
        )

    def test_task_018_no_004_005_server_event_allowed_behaviors_pass(self):
        for behavior in ("float", "hard_fixed"):
            with self.subTest(behavior=behavior):
                self.assert_xml_passes(
                    "ItemType",
                    self.itemtype_with_relationship(
                        self.server_event(
                            f"""<behavior>{behavior}</behavior>
        <event_version>version_1</event_version>
        <server_event>onAfterCopy</server_event>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                        )
                    ),
                )

    def test_task_018_no_006_server_event_invalid_behavior_reports_list(self):
        self.assert_xml_reports_rules(
            "ItemType",
            self.itemtype_with_relationship(
                self.server_event(
                    f"""<behavior>inherit</behavior>
        <event_version>version_1</event_version>
        <server_event>onAfterCopy</server_event>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                )
            ),
            ["ITEMTYPE_SERVER_EVENT_LIST001"],
        )

    def test_task_018_no_008_to_010_server_event_values_are_not_checked(self):
        for server_event in ("onAfterResetLifecycle", "onChange", "onDemand"):
            with self.subTest(server_event=server_event):
                self.assert_xml_passes(
                    "ItemType",
                    self.itemtype_with_relationship(
                        self.server_event(
                            f"""<event_version>version_1</event_version>
        <server_event>{server_event}</server_event>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                        )
                    ),
                )

    def test_task_018_no_011_server_event_edit_missing_event_version_passes(self):
        self.assert_xml_passes(
            "ItemType",
            self.itemtype_with_relationship(
                self.server_event(
                    f"""<server_event>onAfterCopy</server_event>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>""",
                    action="edit",
                )
            ),
        )

    def test_task_018_no_012_item_action_required_fields_pass(self):
        self.assert_xml_passes(
            "ItemType",
            self.itemtype_with_relationship(
                self.item_action(
                    f"""<related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                )
            ),
        )

    def test_task_018_no_013_item_action_missing_source_reports_required(self):
        self.assert_xml_reports_rules(
            "ItemType",
            self.itemtype_with_relationship(
                self.item_action(
                    """<related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>"""
                )
            ),
            ["ITEMTYPE_ITEM_ACTION_REQUIRED001"],
        )

    def test_task_018_no_014_015_item_action_behavior_values(self):
        self.assert_xml_passes(
            "ItemType",
            self.itemtype_with_relationship(
                self.item_action(
                    f"""<behavior>fixed</behavior>
        <related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                )
            ),
        )
        self.assert_xml_reports_rules(
            "ItemType",
            self.itemtype_with_relationship(
                self.item_action(
                    f"""<behavior>inherit</behavior>
        <related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>"""
                )
            ),
            ["ITEMTYPE_ITEM_ACTION_LIST001"],
        )

    def test_task_018_no_017_can_add_has_no_extra_checks(self):
        self.assert_xml_passes(
            "ItemType",
            self.itemtype_with_relationship(
                f"""      <Item type="Can Add" id="AABBCC1122334455AABBCC1122334455" action="add">
        <can_add>1</can_add>
        <source_id keyed_name="CAD" type="ItemType" name="CAD">{ITEMTYPE_ID}</source_id>
      </Item>"""
            ),
        )

    def test_task_018_no_018_outside_itemtype_path_skips_checks(self):
        self.assert_xml_passes(
            "Form",
            self.itemtype_with_relationship(
                self.server_event("""<server_event>onAfterCopy</server_event>""")
            ),
        )


if __name__ == "__main__":
    unittest.main()
