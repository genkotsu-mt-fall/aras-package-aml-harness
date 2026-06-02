from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aml_harness.base import Diagnostic, check_file


class PackageItemRequiredCheckTests(unittest.TestCase):
    def check_xml(self, parent_dir: str, xml: str, file_name: str = "sample.xml") -> list[Diagnostic]:
        with TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir) / parent_dir
            directory.mkdir(parents=True)
            path = directory / file_name
            path.write_text(xml, encoding="utf-8")
            return check_file(path)

    def assert_xml_passes(self, parent_dir: str, xml: str):
        diagnostics = self.check_xml(parent_dir, xml)
        self.assertEqual([], diagnostics, diagnostics)

    def assert_xml_reports_rules(self, parent_dir: str, xml: str, expected_rule_ids: list[str]):
        diagnostics = self.check_xml(parent_dir, xml)
        self.assertEqual(expected_rule_ids, [diagnostic.rule_id for diagnostic in diagnostics], diagnostics)

    def test_task_020_no_001_method_required_fields_pass(self):
        self.assert_xml_passes(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <method_type>JavaScript</method_type>
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
        )

    def test_task_020_no_002_method_missing_execution_allowed_to_reports_required(self):
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <method_type>JavaScript</method_type>
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
            ["METHOD_REQUIRED001"],
        )

    def test_task_020_no_003_method_missing_name_reports_required(self):
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <method_type>JavaScript</method_type>
  </Item>
</AML>""",
            ["METHOD_REQUIRED001"],
        )

    def test_task_020_no_004_005_method_locations_pass(self):
        for method_location in ("client", "server"):
            with self.subTest(method_location=method_location):
                self.assert_xml_passes(
                    "Method",
                    f"""<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <method_location>{method_location}</method_location>
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
                )

    def test_task_020_no_006_invalid_method_location_reports_list(self):
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <method_location>both</method_location>
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
            ["METHOD_LIST001"],
        )

    def test_task_020_no_008_edit_missing_required_passes(self):
        self.assert_xml_passes(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="edit">
    <method_type>JavaScript</method_type>
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
        )

    def test_task_020_no_009_edit_invalid_method_location_reports_list(self):
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="edit">
    <method_location>none</method_location>
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
            ["METHOD_LIST001"],
        )

    def test_task_020_no_010_get_is_ignored(self):
        self.assert_xml_passes(
            "Method",
            """<AML>
  <Item type="Method" action="get" select="id">
    <name>PE_AddToChange</name>
  </Item>
</AML>""",
        )

    def test_task_020_no_011_multiple_methods_pass(self):
        self.assert_xml_passes(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <name>Method_A</name>
  </Item>
  <Item type="Method" id="9999FC3E4D42B8B51BCD7F4194E52799" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <name>Method_B</name>
  </Item>
</AML>""",
        )

    def test_task_020_no_012_later_method_missing_required_reports_required(self):
        self.assert_xml_reports_rules(
            "Method",
            """<AML>
  <Item type="Method" id="83FB72FC3E4D42B8B51BCD7F4194E527" action="add">
    <execution_allowed_to keyed_name="Innovator" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <name>Method_A</name>
  </Item>
  <Item type="Method" id="9999FC3E4D42B8B51BCD7F4194E52799" action="add">
    <name>Method_B</name>
  </Item>
</AML>""",
            ["METHOD_REQUIRED001"],
        )

    def test_task_021_list_required_name_and_values(self):
        self.assert_xml_passes(
            "List",
            """<AML>
  <Item type="List" id="FC8EA0C99C22437DB895E4C61ED56D5C" action="add">
    <name>AccessSharingModes</name>
    <Relationships>
      <Item type="Value" id="27F3BD2E8E1941C7A71BA26C9FC22D33" action="add">
        <value>private</value>
      </Item>
      <Item type="Value" id="3E5B2D1A1234567890ABCDEF12345678" action="add">
        <value>public</value>
      </Item>
    </Relationships>
  </Item>
</AML>""",
        )
        self.assert_xml_reports_rules(
            "List",
            """<AML>
  <Item type="List" id="FC8EA0C99C22437DB895E4C61ED56D5C" action="add">
    <Relationships>
      <Item type="Value" id="27F3BD2E8E1941C7A71BA26C9FC22D33" action="add">
        <value>private</value>
      </Item>
    </Relationships>
  </Item>
</AML>""",
            ["LIST_REQUIRED001"],
        )

    def test_task_021_no_004_list_without_values_passes(self):
        self.assert_xml_passes(
            "List",
            """<AML>
  <Item type="List" id="FC8EA0C99C22437DB895E4C61ED56D5C" action="add">
    <name>AccessSharingModes</name>
  </Item>
</AML>""",
        )

    def test_task_021_no_005_list_edit_missing_name_passes(self):
        self.assert_xml_passes(
            "List",
            """<AML>
  <Item type="List" id="FC8EA0C99C22437DB895E4C61ED56D5C" action="edit">
    <Relationships>
      <Item type="Value" id="27F3BD2E8E1941C7A71BA26C9FC22D33" action="add">
        <value>private</value>
      </Item>
    </Relationships>
  </Item>
</AML>""",
        )

    def test_task_021_no_006_outside_list_path_skips_list_required_check(self):
        self.assert_xml_passes(
            "Method",
            """<AML>
  <Item type="List" id="FC8EA0C99C22437DB895E4C61ED56D5C" action="add">
    <Relationships>
      <Item type="Value" id="27F3BD2E8E1941C7A71BA26C9FC22D33" action="add">
        <value>private</value>
      </Item>
    </Relationships>
  </Item>
</AML>""",
        )

    def test_task_022_variable_required_name(self):
        self.assert_xml_passes(
            "Variable",
            """<AML>
  <Item type="Variable" id="A3B4C5D6E7F8012345678901234ABCDE" action="add">
    <name>AccountLockoutDuration_minutes</name>
    <value>30</value>
  </Item>
</AML>""",
        )
        self.assert_xml_reports_rules(
            "Variable",
            """<AML>
  <Item type="Variable" id="A3B4C5D6E7F8012345678901234ABCDE" action="add">
    <value>30</value>
  </Item>
</AML>""",
            ["VARIABLE_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "Variable",
            """<AML>
  <Item type="Variable" id="A3B4C5D6E7F8012345678901234ABCDE" action="add">
    <name>   </name>
    <value>30</value>
  </Item>
</AML>""",
            ["VARIABLE_REQUIRED001"],
        )

    def test_task_022_no_003_variable_edit_missing_name_passes(self):
        self.assert_xml_passes(
            "Variable",
            """<AML>
  <Item type="Variable" id="A3B4C5D6E7F8012345678901234ABCDE" action="edit">
    <value>60</value>
  </Item>
</AML>""",
        )

    def test_task_022_no_005_outside_variable_path_skips_variable_required_check(self):
        self.assert_xml_passes(
            "List",
            """<AML>
  <Item type="Variable" id="A3B4C5D6E7F8012345678901234ABCDE" action="add">
    <value>30</value>
  </Item>
</AML>""",
        )

    def test_task_023_usermessage_required_name(self):
        self.assert_xml_passes(
            "UserMessage",
            """<AML>
  <Item type="UserMessage" id="B1C2D3E4F5067890ABCDEF0123456789" action="add">
    <name>ac_AttrDefinitionDrQueryDepthExceeds</name>
    <message>Query depth exceeded.</message>
  </Item>
</AML>""",
        )
        self.assert_xml_reports_rules(
            "UserMessage",
            """<AML>
  <Item type="UserMessage" id="B1C2D3E4F5067890ABCDEF0123456789" action="add">
    <message>Query depth exceeded.</message>
  </Item>
</AML>""",
            ["USERMESSAGE_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "UserMessage",
            """<AML>
  <Item type="UserMessage" id="B1C2D3E4F5067890ABCDEF0123456789" action="add">
    <name>  </name>
    <message>Query depth exceeded.</message>
  </Item>
</AML>""",
            ["USERMESSAGE_REQUIRED001"],
        )

    def test_task_023_no_003_usermessage_edit_missing_name_passes(self):
        self.assert_xml_passes(
            "UserMessage",
            """<AML>
  <Item type="UserMessage" id="B1C2D3E4F5067890ABCDEF0123456789" action="edit">
    <message>Updated message.</message>
  </Item>
</AML>""",
        )

    def test_task_023_no_005_outside_usermessage_path_skips_usermessage_required_check(self):
        self.assert_xml_passes(
            "Variable",
            """<AML>
  <Item type="UserMessage" id="B1C2D3E4F5067890ABCDEF0123456789" action="add">
    <message>Query depth exceeded.</message>
  </Item>
</AML>""",
        )

    def test_task_024_life_cycle_map_required_name_and_relationships(self):
        self.assert_xml_passes(
            "Life Cycle Map",
            """<AML>
  <Item type="Life Cycle Map" id="C1D2E3F4A5B6789012345678901ABCDE" action="add">
    <name>Default</name>
    <label>Default</label>
    <Relationships>
      <Item type="Life Cycle State" id="D2E3F4A5B6C7890123456789012BCDEF" action="add">
        <name>Preliminary</name>
        <source_id keyed_name="Default" type="Life Cycle Map">C1D2E3F4A5B6789012345678901ABCDE</source_id>
      </Item>
    </Relationships>
  </Item>
</AML>""",
        )
        self.assert_xml_reports_rules(
            "Life Cycle Map",
            """<AML>
  <Item type="Life Cycle Map" id="C1D2E3F4A5B6789012345678901ABCDE" action="add">
    <label>Default</label>
  </Item>
</AML>""",
            ["LIFECYCLE_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "Life Cycle Map",
            """<AML>
  <Item type="Life Cycle Map" id="C1D2E3F4A5B6789012345678901ABCDE" action="add">
    <name>   </name>
    <label>Default</label>
  </Item>
</AML>""",
            ["LIFECYCLE_REQUIRED001"],
        )

    def test_task_024_no_003_life_cycle_map_edit_missing_name_passes(self):
        self.assert_xml_passes(
            "Life Cycle Map",
            """<AML>
  <Item type="Life Cycle Map" id="C1D2E3F4A5B6789012345678901ABCDE" action="edit">
    <label>Updated</label>
  </Item>
</AML>""",
        )

    def test_task_024_no_006_outside_life_cycle_map_path_skips_required_check(self):
        self.assert_xml_passes(
            "UserMessage",
            """<AML>
  <Item type="Life Cycle Map" id="C1D2E3F4A5B6789012345678901ABCDE" action="add">
    <label>Default</label>
  </Item>
</AML>""",
        )


if __name__ == "__main__":
    unittest.main()
