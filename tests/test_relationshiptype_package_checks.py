from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aml_harness.base import Diagnostic, check_file


RELTYPE_ID = "4FD5E0CB3A9F448A9E9F246C7D48B2B3"
REL_ITEMTYPE_ID = "11111111111111111111111111111111"
BODY_ID = "83907DEF8B3044A08BDCBB77B1C0517E"
FIELD_ID = "FD36E7C8554E49098C55D72307BF1639"


class RelationshipTypePackageCheckTests(unittest.TestCase):
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

    def relationshiptype(self, relationships: str, behavior: str = "") -> str:
        return f"""<AML>
  <Item type="RelationshipType" id="{RELTYPE_ID}" action="add">
    <name>Part BOM</name>
    {behavior}
    <relationship_id keyed_name="Part BOM" type="ItemType" name="Part BOM">
      <Item type="ItemType" id="{REL_ITEMTYPE_ID}" action="add">
        <name>Part BOM</name>
        <Relationships>
{relationships}
        </Relationships>
      </Item>
    </relationship_id>
  </Item>
</AML>"""

    def server_event(self, content: str, action: str = "add") -> str:
        return f"""          <Item type="Server Event" id="C17B14040CC54E1B8647A220C5188E3A" action="{action}">
            {content}
          </Item>"""

    def item_action(self, content: str) -> str:
        return f"""          <Item type="Item Action" id="81BAAD8CEBF44188B48233364D886734" action="add">
            {content}
          </Item>"""

    def body_with_field(self, field_content: str, field_relationships: str = "") -> str:
        nested = f"<Relationships>{field_relationships}</Relationships>" if field_relationships else ""
        return f"""          <Item type="Body" id="{BODY_ID}" action="add">
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>
            <Relationships>
              <Item type="Field" id="{FIELD_ID}" action="add">
                {field_content}
                {nested}
              </Item>
            </Relationships>
          </Item>"""

    def valid_field_content(self) -> str:
        return f"""<show_help>1</show_help>
                <source_id keyed_name="{BODY_ID}" type="Body">{BODY_ID}</source_id>
                <name>quantity</name>"""

    def test_task_025_no_001_server_event_required_fields_pass(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    f"""<event_version>version_1</event_version>
            <server_event>onAfterAdd</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                )
            ),
        )

    def test_task_025_no_002_003_server_event_required_fields(self):
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    f"""<server_event>onAfterAdd</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                )
            ),
            ["RELTYPE_SERVER_EVENT_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    """<event_version>version_1</event_version>
            <server_event>onAfterAdd</server_event>"""
                )
            ),
            ["RELTYPE_SERVER_EVENT_REQUIRED001"],
        )

    def test_task_025_no_004_005_server_event_behavior_list(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    f"""<behavior>float</behavior>
            <event_version>version_1</event_version>
            <server_event>onAfterAdd</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                )
            ),
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    f"""<behavior>inherit</behavior>
            <event_version>version_1</event_version>
            <server_event>onAfterAdd</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                )
            ),
            ["RELTYPE_SERVER_EVENT_LIST001"],
        )

    def test_task_025_no_006_server_event_edit_missing_event_version_passes(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    f"""<server_event>onAfterAdd</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>""",
                    action="edit",
                )
            ),
        )

    def test_task_025_no_007_to_009_item_action_checks(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                self.item_action(
                    f"""<related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                )
            ),
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.item_action(
                    """<related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>"""
                )
            ),
            ["RELTYPE_ITEM_ACTION_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.item_action(
                    f"""<behavior>inherit</behavior>
            <related_id keyed_name="PE_AddToChange" type="Action">83FB72FC3E4D42B8B51BCD7F4194E527</related_id>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                )
            ),
            ["RELTYPE_ITEM_ACTION_LIST001"],
        )

    def test_task_025_no_010_can_add_has_no_extra_checks(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                f"""          <Item type="Can Add" id="AABBCC1122334455AABBCC1122334455" action="add">
            <can_add>1</can_add>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>
          </Item>"""
            ),
        )

    def test_task_025_no_011_012_body_required_source(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                f"""          <Item type="Body" id="{BODY_ID}" action="add">
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>
          </Item>"""
            ),
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                f"""          <Item type="Body" id="{BODY_ID}" action="add">
            <sort_order>128</sort_order>
          </Item>"""
            ),
            ["RELTYPE_BODY_REQUIRED001"],
        )

    def test_task_025_no_013_to_015_field_checks(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(self.body_with_field(self.valid_field_content())),
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.body_with_field(
                    f"""<source_id keyed_name="{BODY_ID}" type="Body">{BODY_ID}</source_id>
                <name>quantity</name>"""
                )
            ),
            ["RELTYPE_FIELD_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                self.body_with_field(f"<field_type>bad_type</field_type>{self.valid_field_content()}")
            ),
            ["RELTYPE_FIELD_LIST001"],
        )

    def test_task_025_no_016_017_form_event_checks(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                f"""          <Item type="Form Event" id="05F15EA49BA74DA2B82934315EA71F88" action="add">
            <form_event>onformpopulated</form_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>
          </Item>"""
            ),
        )
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(
                """          <Item type="Form Event" id="05F15EA49BA74DA2B82934315EA71F88" action="add">
            <form_event>onformpopulated</form_event>
          </Item>"""
            ),
            ["RELTYPE_FORM_EVENT_REQUIRED001"],
        )

    def test_task_025_no_018_relationshiptype_behavior_is_ignored(self):
        self.assert_xml_passes(
            "RelationshipType",
            self.relationshiptype(
                self.server_event(
                    f"""<event_version>version_1</event_version>
            <server_event>onAfterAdd</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                ),
                behavior="<behavior>float</behavior>",
            ),
        )

    def test_task_025_no_019_to_021_server_event_values_are_not_checked(self):
        for server_event in ("onAfterResetLifecycle", "onChange", "onDemand"):
            with self.subTest(server_event=server_event):
                self.assert_xml_passes(
                    "RelationshipType",
                    self.relationshiptype(
                        self.server_event(
                            f"""<event_version>version_1</event_version>
            <server_event>{server_event}</server_event>
            <source_id keyed_name="Part BOM" type="ItemType">{REL_ITEMTYPE_ID}</source_id>"""
                        )
                    ),
                )

    def test_task_025_no_022_023_field_event_checks(self):
        missing_source = """<Item type="Field Event" id="B23EB5707693445DBC77E46887D505E4" action="add">
                  <field_event>onchange</field_event>
                </Item>"""
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(self.body_with_field(self.valid_field_content(), missing_source)),
            ["RELTYPE_FIELD_EVENT_REQUIRED001"],
        )

        invalid_event = f"""<Item type="Field Event" id="B23EB5707693445DBC77E46887D505E4" action="add">
                  <field_event>onhover</field_event>
                  <source_id keyed_name="quantity" type="Field">{FIELD_ID}</source_id>
                </Item>"""
        self.assert_xml_reports_rules(
            "RelationshipType",
            self.relationshiptype(self.body_with_field(self.valid_field_content(), invalid_event)),
            ["RELTYPE_FIELD_EVENT_LIST001"],
        )

    def test_task_025_no_024_outside_relationshiptype_path_skips_checks(self):
        self.assert_xml_passes(
            "ItemType",
            self.relationshiptype(
                self.server_event("""<server_event>onAfterAdd</server_event>""")
            ),
        )


if __name__ == "__main__":
    unittest.main()
