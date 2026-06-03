from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aml_harness.base import Diagnostic, check_file


ACTION_ID = "11111111111111111111111111111111"
FORM_ID = "22222222222222222222222222222222"
BODY_ID = "33333333333333333333333333333333"
FIELD_ID = "44444444444444444444444444444444"


class Task026RequiredPropertyTests(unittest.TestCase):
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

    def valid_action_children(self) -> str:
        return """<name>PE_ChooseCMOptions</name>
    <location>client</location>
    <method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>
    <target>main</target>
    <type>item</type>"""

    def action(self, children: str, action: str = "add") -> str:
        return f"""<AML>
  <Item type="Action" id="{ACTION_ID}" action="{action}">
    {children}
  </Item>
</AML>"""

    def form(self, children: str) -> str:
        return f"""<AML>
  <Item type="Form" id="{FORM_ID}" action="add">
    {children}
  </Item>
</AML>"""

    def test_task_026_no_001_action_required_fields_pass(self):
        self.assert_xml_passes("Action", self.action(self.valid_action_children()))

    def test_task_026_no_002_action_missing_method_reports_required(self):
        self.assert_xml_reports_rules(
            "Action",
            self.action("""<name>PE_ChooseCMOptions</name>
    <location>client</location>
    <target>main</target>
    <type>item</type>"""),
            ["ACTION_REQUIRED001"],
        )

    def test_task_026_no_003_action_empty_method_reports_required(self):
        self.assert_xml_reports_rules(
            "Action",
            self.action("""<name>PE_ChooseCMOptions</name>
    <location>client</location>
    <method />
    <target>main</target>
    <type>item</type>"""),
            ["ACTION_REQUIRED001"],
        )

    def test_task_026_no_004_to_007_action_method_inline_get_shape(self):
        invalid_methods = (
            """<method keyed_name="PE_ChooseCMOptions" type="Method">PE_ChooseCMOptions</method>""",
            """<method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="add" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>""",
            """<method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>""",
            """<method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id" />
    </method>""",
        )
        for method_xml in invalid_methods:
            with self.subTest(method_xml=method_xml):
                self.assert_xml_reports_rules(
                    "Action",
                    self.action(f"""<name>PE_ChooseCMOptions</name>
    <location>client</location>
    {method_xml}
    <target>main</target>
    <type>item</type>"""),
                    ["ACTION_REQUIRED001"],
                )

    def test_task_026_no_008_to_011_action_missing_required_fields(self):
        cases = (
            """<location>client</location>
    <method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>
    <target>main</target>
    <type>item</type>""",
            """<name>PE_ChooseCMOptions</name>
    <method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>
    <target>main</target>
    <type>item</type>""",
            """<name>PE_ChooseCMOptions</name>
    <location>client</location>
    <method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>
    <type>item</type>""",
            """<name>PE_ChooseCMOptions</name>
    <location>client</location>
    <method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>
    <target>main</target>""",
        )
        for children in cases:
            with self.subTest(children=children):
                self.assert_xml_reports_rules("Action", self.action(children), ["ACTION_REQUIRED001"])

    def test_task_026_no_012_action_list_value_check_still_runs(self):
        self.assert_xml_reports_rules(
            "Action",
            self.action("""<name>PE_ChooseCMOptions</name>
    <location>desktop</location>
    <method keyed_name="PE_ChooseCMOptions" type="Method">
      <Item type="Method" action="get" select="id">
        <name>PE_ChooseCMOptions</name>
      </Item>
    </method>
    <target>main</target>
    <type>item</type>"""),
            ["ACTION_LIST001"],
        )

    def test_task_026_no_013_action_edit_missing_required_passes(self):
        self.assert_xml_passes(
            "Action",
            self.action("""<location>client</location>
    <target>window</target>
    <type>item</type>""", action="edit"),
        )

    def test_task_026_no_014_to_018_existing_name_required_checks(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form("<height>234</height><width>699</width>"),
            ["FORM_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="55555555555555555555555555555555" action="add">
    <execution_allowed_to keyed_name="World" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
  </Item>
</AML>""",
            ["METHOD_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "List",
            """<AML>
  <Item type="List" id="66666666666666666666666666666666" action="add" />
</AML>""",
            ["LIST_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "Life Cycle Map",
            """<AML>
  <Item type="Life Cycle Map" id="77777777777777777777777777777777" action="add" />
</AML>""",
            ["LIFECYCLE_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "UserMessage",
            """<AML>
  <Item type="UserMessage" id="88888888888888888888888888888888" action="add">
    <text>Sample message.</text>
  </Item>
</AML>""",
            ["USERMESSAGE_REQUIRED001"],
        )

    def test_task_026_no_019_field_source_id_required_check(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form(f"""<name>Sample Form</name>
    <height>234</height>
    <width>699</width>
    <Relationships>
      <Item type="Body" id="{BODY_ID}" action="add">
        <source_id keyed_name="Sample Form" type="Form">{FORM_ID}</source_id>
        <Relationships>
          <Item type="Field" id="{FIELD_ID}" action="add">
            <name>sample_field</name>
            <show_help>1</show_help>
          </Item>
        </Relationships>
      </Item>
    </Relationships>"""),
            ["FORM_FIELD_REQUIRED001"],
        )

    def test_task_026_no_020_form_height_width_required_checks(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form("<name>Default Sized Form</name>"),
            ["FORM_REQUIRED001", "FORM_REQUIRED001"],
        )

    def test_task_026_no_021_standard_properties_are_not_required(self):
        self.assert_xml_passes("Action", self.action(self.valid_action_children()))

    def test_task_026_no_022_child_id_is_not_required(self):
        self.assert_xml_passes(
            "UserMessage",
            """<AML>
  <Item type="UserMessage" id="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" action="add">
    <name>Sample_Message</name>
    <text>Sample message.</text>
  </Item>
</AML>""",
        )

    def test_task_026_no_023_field_show_help_required_check(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form(f"""<name>Sample Form</name>
    <height>234</height>
    <width>699</width>
    <Relationships>
      <Item type="Body" id="{BODY_ID}" action="add">
        <source_id keyed_name="Sample Form" type="Form">{FORM_ID}</source_id>
        <Relationships>
          <Item type="Field" id="{FIELD_ID}" action="add">
            <name>sample_field</name>
            <source_id keyed_name="Sample Body" type="Body">{BODY_ID}</source_id>
          </Item>
        </Relationships>
      </Item>
    </Relationships>"""),
            ["FORM_FIELD_REQUIRED001"],
        )

    def test_task_026_no_024_method_execution_allowed_to_required_check(self):
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC" action="add">
    <name>SampleMethod</name>
  </Item>
</AML>""",
            ["METHOD_REQUIRED001"],
        )

    def test_task_026_no_025_itemtype_structure_view_is_not_new_required_check(self):
        self.assert_xml_passes(
            "ItemType",
            """<AML>
  <Item type="ItemType" id="DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD" action="add">
    <name>Sample ItemType</name>
  </Item>
</AML>""",
        )


if __name__ == "__main__":
    unittest.main()
