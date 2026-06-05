from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import unittest
from unittest.mock import patch

from aml_harness.base import Diagnostic, check_file
from aml_harness.cli import main


ROOT_DIR = Path(__file__).resolve().parents[1]
FIELD_TYPE_VALUES = (
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
)


class Task027DiagnosticMessageTests(unittest.TestCase):
    def check_sample(self, relative_path: str) -> list[Diagnostic]:
        return check_file(ROOT_DIR / relative_path)

    def assert_sample_passes(self, relative_path: str):
        diagnostics = self.check_sample(relative_path)
        self.assertEqual([], diagnostics, f"{relative_path}: {diagnostics}")

    def assert_sample_rule_message_contains(
        self,
        relative_path: str,
        rule_id: str,
        snippets: tuple[str, ...],
    ):
        diagnostics = self.check_sample(relative_path)
        self.assert_rule_message_contains(diagnostics, rule_id, snippets)

    def assert_rule_message_contains(
        self,
        diagnostics: list[Diagnostic],
        rule_id: str,
        snippets: tuple[str, ...],
    ):
        messages = [diagnostic.message for diagnostic in diagnostics if diagnostic.rule_id == rule_id]
        self.assertTrue(messages, f"Expected {rule_id}, got {diagnostics}")
        message = messages[0]
        for snippet in snippets:
            with self.subTest(rule_id=rule_id, snippet=snippet, message=message):
                self.assertIn(snippet, message)

    def assert_rule_message_contains_one_of(
        self,
        diagnostics: list[Diagnostic],
        rule_id: str,
        snippets: tuple[str, ...],
    ):
        messages = [diagnostic.message for diagnostic in diagnostics if diagnostic.rule_id == rule_id]
        self.assertTrue(messages, f"Expected {rule_id}, got {diagnostics}")
        message = messages[0]
        self.assertTrue(
            any(snippet in message for snippet in snippets),
            f"Expected one of {snippets!r} in {message!r}",
        )

    def assert_rule_message_tells_list_replacement(self, diagnostics: list[Diagnostic], rule_id: str):
        self.assert_rule_message_contains_one_of(
            diagnostics,
            rule_id,
            ("Replace", "Set", "Use one of"),
        )

    def check_temp_xml(self, parent_dir: str, file_name: str, xml: str) -> list[Diagnostic]:
        with TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir) / parent_dir
            directory.mkdir(parents=True)
            path = directory / file_name
            path.write_text(xml, encoding="utf-8")
            return check_file(path)

    def test_no_001_valid_action_reports_no_action_rules(self):
        self.assert_sample_passes("samples/good/Action/aml-01-valid-action.xml")

    def test_no_002_action_name_missing_message_tells_child_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/Action/aml-02-action-name-missing.xml",
            "ACTION_REQUIRED001",
            ("Action.name", "missing or empty", "<name>", "non-empty"),
        )

    def test_no_003_action_method_empty_message_includes_inline_get_example_parts(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/Action/aml-03-action-method-empty.xml",
            "ACTION_REQUIRED001",
            ("Action.method", "inline Method reference", 'action="get"', 'select="id"', "<name>"),
        )

    def test_no_004_action_target_invalid_message_includes_current_and_allowed_values(self):
        diagnostics = self.check_sample("samples/bad/Action/aml-04-action-target-invalid.xml")
        self.assert_rule_message_contains(
            diagnostics,
            "ACTION_LIST002",
            ("popup", "main", "window", "one window", "none"),
        )
        self.assert_rule_message_tells_list_replacement(diagnostics, "ACTION_LIST002")

    def test_no_005_item_action_missing_message_tells_attribute_candidates(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/Method/aml-05-item-action-missing.xml",
            "AML005",
            ("action attribute", "Add", "add", "edit", "delete", "get"),
        )

    def test_no_006_item_action_invalid_message_includes_current_and_allowed_values(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/Method/aml-06-item-action-invalid.xml",
            "AML005",
            ("merge", "add", "edit", "delete", "get"),
        )

    def test_no_007_form_width_missing_message_tells_child_to_add(self):
        diagnostics = self.check_temp_xml(
            "Form",
            "aml-07-form-width-missing.xml",
            """
<AML>
  <Item type="Form" id="77777777777777777777777777777777" action="add">
    <name>Sample Form</name>
    <height>234</height>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "FORM_REQUIRED001",
            ("Form.width", "missing or empty", "<width>", "non-empty"),
        )

    def test_no_008_field_type_invalid_message_includes_current_and_all_allowed_values(self):
        diagnostics = self.check_temp_xml(
            "Form",
            "aml-08-field-field-type-invalid.xml",
            self.form_with_body(
                """
          <Item type="Field" id="8888888888888888888888888888888A" action="add">
            <show_help>1</show_help>
            <source_id keyed_name="Sample Body" type="Body">88888888888888888888888888888889</source_id>
            <field_type>grid</field_type>
          </Item>
""".rstrip(),
                form_id="88888888888888888888888888888888",
                body_id="88888888888888888888888888888889",
            ),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "FORM_FIELD_LIST001",
            ("grid",) + FIELD_TYPE_VALUES,
        )
        self.assert_rule_message_tells_list_replacement(diagnostics, "FORM_FIELD_LIST001")

    def test_no_009_body_behavior_invalid_message_includes_current_and_allowed_values(self):
        diagnostics = self.check_temp_xml(
            "Form",
            "aml-09-body-behavior-invalid.xml",
            self.form_with_body(
                "",
                body_extra="<behavior>floating</behavior>",
                form_id="99999999999999999999999999999999",
                body_id="9999999999999999999999999999999A",
            ),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "FORM_BODY_LIST001",
            ("floating", "float", "fixed", "hard_fixed", "hard_float"),
        )
        self.assert_rule_message_tells_list_replacement(diagnostics, "FORM_BODY_LIST001")

    def test_no_010_sequence_required_message_tells_remove_or_set_zero(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/ItemType/aml-10-sequence-required.xml",
            "ITYPE_SEQUENCE001",
            ('data_type="sequence"', "<is_required>1</is_required>", "Remove", "set it to 0"),
        )

    def test_no_011_standard_property_add_message_tells_use_edit(self):
        diagnostics = self.check_sample("samples/bad/ItemType/aml-11-standard-property-add.xml")
        self.assert_rule_message_contains(
            diagnostics,
            "ITEMTYPE001",
            ("state", 'Property action="edit"'),
        )
        self.assert_rule_message_contains_one_of(diagnostics, "ITEMTYPE001", ("Change", "Use"))

    def test_no_012_form_standard_property_without_field_add_message_tells_matching_id(self):
        diagnostics = self.check_sample(
            "samples/bad/Form/aml-12-standard-property-edit-without-add-field.xml"
        )
        self.assert_rule_message_contains(
            diagnostics,
            "FORM003",
            ("state", 'matching Field action="add"'),
        )
        self.assert_rule_message_contains_one_of(
            diagnostics,
            "FORM003",
            ("same id", 'Add Field action="add"'),
        )

    def test_no_013_method_location_invalid_message_includes_current_and_allowed_values(self):
        diagnostics = self.check_temp_xml(
            "Method",
            "aml-13-method-location-invalid.xml",
            """
<AML>
  <Item type="Method" id="EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE" action="add">
    <name>SampleMethod</name>
    <execution_allowed_to keyed_name="World" type="Identity">2618D6F5A90949BAA7E920D1B04C7EE1</execution_allowed_to>
    <method_location>browser</method_location>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "METHOD_LIST001",
            ("browser", "client", "server"),
        )
        self.assert_rule_message_tells_list_replacement(diagnostics, "METHOD_LIST001")

    def test_no_014_imports_root_invalid_message_tells_expected_root(self):
        diagnostics = self.check_sample("samples/bad/imports-root-invalid/imports.mf")
        self.assert_rule_message_contains(
            diagnostics,
            "IMPORTS001",
            ("<AML>", "<imports>"),
        )
        self.assert_rule_message_contains_one_of(diagnostics, "IMPORTS001", ("Replace", "Use"))

    def test_no_015_imports_missing_path_message_tells_path_and_action(self):
        diagnostics = self.check_sample("samples/bad/imports-missing-path/imports.mf")
        self.assert_rule_message_contains(diagnostics, "IMPORTS006", ("missing-package",))
        self.assert_rule_message_contains_one_of(
            diagnostics,
            "IMPORTS006",
            ("Create", "fix path", "set path"),
        )

    def test_no_016_missing_file_message_tells_path_and_action(self):
        path = ROOT_DIR / "samples/missing/does-not-exist.xml"
        diagnostics = check_file(path)
        self.assert_rule_message_contains(diagnostics, "FILE001", (str(path),))
        self.assert_rule_message_contains_one_of(
            diagnostics,
            "FILE001",
            ("Create the file", "check the path"),
        )

    def test_no_017_cli_output_keeps_severity_rule_id_message_format(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["samples/bad/Action/aml-04-action-target-invalid.xml"])
        self.assertEqual(1, exit_code)
        first_line = output.getvalue().splitlines()[0]
        self.assertRegex(
            first_line,
            re.compile(
                r"^samples[\\/]bad[\\/]Action[\\/]aml-04-action-target-invalid\.xml:"
                r"\d+:\d+ error ACTION_LIST002 .+"
            ),
        )
        for snippet in ("popup", "main", "window", "one window", "none"):
            with self.subTest(snippet=snippet, line=first_line):
                self.assertIn(snippet, first_line)

    def test_no_018_field_type_invalid_keeps_existing_rule_id(self):
        diagnostics = self.check_temp_xml(
            "Form",
            "aml-08-field-field-type-invalid.xml",
            self.form_with_body(
                """
          <Item type="Field" id="8888888888888888888888888888888A" action="add">
            <show_help>1</show_help>
            <source_id keyed_name="Sample Body" type="Body">88888888888888888888888888888889</source_id>
            <field_type>grid</field_type>
          </Item>
""".rstrip(),
                form_id="88888888888888888888888888888888",
                body_id="88888888888888888888888888888889",
            ),
        )
        self.assertEqual(["FORM_FIELD_LIST001"], [diagnostic.rule_id for diagnostic in diagnostics])

    def test_no_019_relationshiptype_field_type_invalid_message_includes_values(self):
        diagnostics = self.check_temp_xml(
            "RelationshipType",
            "aml-19-reltype-field-type-invalid.xml",
            """
<AML>
  <Item type="RelationshipType" id="19191919191919191919191919191919" action="add">
    <name>Sample Relationship</name>
    <related_id keyed_name="Part" type="ItemType">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA</related_id>
    <relationship_id keyed_name="Part BOM" type="ItemType">
      <Item type="ItemType" id="BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB" action="add">
        <name>Part BOM</name>
        <Relationships>
          <Item type="Body" id="1919191919191919191919191919191A" action="add">
            <source_id keyed_name="Part BOM" type="ItemType">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB</source_id>
            <Relationships>
              <Item type="Field" id="1919191919191919191919191919191B" action="add">
                <show_help>1</show_help>
                <source_id keyed_name="Sample Body" type="Body">1919191919191919191919191919191A</source_id>
                <field_type>bad_type</field_type>
              </Item>
            </Relationships>
          </Item>
        </Relationships>
      </Item>
    </relationship_id>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "RELTYPE_FIELD_LIST001",
            ("bad_type",) + FIELD_TYPE_VALUES,
        )
        self.assert_rule_message_tells_list_replacement(diagnostics, "RELTYPE_FIELD_LIST001")

    def test_no_020_list_name_missing_message_tells_child_to_add(self):
        diagnostics = self.check_temp_xml(
            "List",
            "aml-20-list-name-missing.xml",
            """
<AML>
  <Item type="List" id="20202020202020202020202020202020" action="add">
    <Relationships>
      <Item type="Value" id="20202020202020202020202020202021" action="add">
        <value>private</value>
      </Item>
    </Relationships>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "LIST_REQUIRED001",
            ("List.name", "missing or empty", "<name>", "non-empty"),
        )

    def test_no_021_variable_name_missing_message_tells_child_to_add(self):
        diagnostics = self.check_temp_xml(
            "Variable",
            "aml-21-variable-name-missing.xml",
            """
<AML>
  <Item type="Variable" id="21212121212121212121212121212121" action="add">
    <value>30</value>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "VARIABLE_REQUIRED001",
            ("Variable.name", "missing or empty", "<name>", "non-empty"),
        )

    def test_no_022_usermessage_name_missing_message_tells_child_to_add(self):
        diagnostics = self.check_temp_xml(
            "UserMessage",
            "aml-22-usermessage-name-missing.xml",
            """
<AML>
  <Item type="UserMessage" id="22222222222222222222222222222223" action="add">
    <message>Query depth exceeded.</message>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "USERMESSAGE_REQUIRED001",
            ("UserMessage.name", "missing or empty", "<name>", "non-empty"),
        )

    def test_no_023_lifecycle_name_missing_message_tells_child_to_add(self):
        diagnostics = self.check_temp_xml(
            "Life Cycle Map",
            "aml-23-lifecycle-name-missing.xml",
            """
<AML>
  <Item type="Life Cycle Map" id="23232323232323232323232323232323" action="add">
    <label>Default</label>
  </Item>
</AML>
""".strip(),
        )
        self.assert_rule_message_contains(
            diagnostics,
            "LIFECYCLE_REQUIRED001",
            ("Life Cycle Map.name", "missing or empty", "<name>", "non-empty"),
        )

    def test_no_024_aml_root_invalid_message_tells_replace_with_aml(self):
        diagnostics = self.check_sample("samples/bad/base/aml-24-root-invalid.xml")
        self.assert_rule_message_contains(diagnostics, "AML001", ("<Package>", "<AML>"))
        self.assert_rule_message_contains_one_of(diagnostics, "AML001", ("Replace", "Use"))

    def test_no_025_empty_aml_message_tells_add_item(self):
        diagnostics = self.check_sample("samples/bad/base/aml-25-empty-aml.xml")
        self.assert_rule_message_contains(diagnostics, "AML002", ("<AML>", "Add", "<Item"))
        self.assert_rule_message_contains_one_of(diagnostics, "AML002", ("no <Item>", "empty"))

    def test_no_026_non_item_child_message_tells_expected_item_and_fix(self):
        diagnostics = self.check_sample("samples/bad/base/aml-26-non-item-child.xml")
        self.assert_rule_message_contains(diagnostics, "AML003", ("<Method>", "<Item>"))
        self.assert_rule_message_contains_one_of(
            diagnostics,
            "AML003",
            ("Replace", "wrap", "move into <Item>"),
        )

    def test_no_027_item_type_missing_message_tells_attribute_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/base/aml-27-item-type-missing.xml",
            "AML004",
            ("<Item>", "type attribute", "missing", 'Add type="..."'),
        )

    def test_no_028_item_id_missing_message_tells_attribute_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/base/aml-28-item-id-missing.xml",
            "AML006",
            ('action="add"', "id attribute", "missing", 'Add id="..."'),
        )

    def test_no_029_delete_where_missing_message_tells_condition_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/base/aml-29-delete-where-missing.xml",
            "AML007",
            ('action="delete"', "where attribute", "missing or empty", 'Add where="..."'),
        )

    def test_no_030_directory_input_message_tells_use_file_path(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "not-a-file-dir"
            path.mkdir()
            diagnostics = check_file(path)
            self.assert_rule_message_contains(diagnostics, "FILE002", (str(path), "not a file"))
            self.assert_rule_message_contains_one_of(
                diagnostics,
                "FILE002",
                ("Specify", "Use a file path"),
            )

    def test_no_031_read_failure_message_tells_file_and_check_action(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "unreadable.xml"
            path.write_text("<AML />", encoding="utf-8")

            original_read_text = Path.read_text

            def failing_read_text(self_path, *args, **kwargs):
                if self_path == path:
                    raise OSError("permission denied")
                return original_read_text(self_path, *args, **kwargs)

            with patch.object(Path, "read_text", failing_read_text):
                diagnostics = check_file(path)

        self.assert_rule_message_contains(
            diagnostics,
            "FILE003",
            (str(path), "permission denied"),
        )
        self.assert_rule_message_contains_one_of(
            diagnostics,
            "FILE003",
            ("Check permissions", "fix the path"),
        )

    def test_no_032_valid_imports_with_multiple_packages_and_dependson_passes(self):
        with TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir) / "imports-valid"
            (directory / "PackageA").mkdir(parents=True)
            (directory / "PackageB").mkdir()
            path = directory / "imports.mf"
            path.write_text(
                """
<imports>
  <package name="PackageA" path="PackageA">
    <dependson name="Core" />
  </package>
  <package name="PackageB" path="PackageB">
    <dependson name="PackageA" />
  </package>
</imports>
""".strip(),
                encoding="utf-8",
            )
            diagnostics = check_file(path)
        self.assertEqual([], diagnostics, diagnostics)

    def test_no_033_imports_no_package_message_tells_package_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/imports-no-package/imports.mf",
            "IMPORTS002",
            ("<imports>", "missing", "<package>", "Add"),
        )

    def test_no_034_imports_non_package_child_message_tells_replace_or_nest(self):
        diagnostics = self.check_sample("samples/bad/imports-non-package-child/imports.mf")
        self.assert_rule_message_contains(diagnostics, "IMPORTS003", ("<dependson>", "<package>"))
        self.assert_rule_message_contains_one_of(
            diagnostics,
            "IMPORTS003",
            ("Move", "Replace", "nest under <package>"),
        )

    def test_no_035_imports_package_name_missing_message_tells_attribute_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/imports-package-name-missing/imports.mf",
            "IMPORTS004",
            ("<package>", "name attribute", "missing", 'Add name="..."'),
        )

    def test_no_036_imports_package_path_missing_message_tells_attribute_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/imports-package-path-missing/imports.mf",
            "IMPORTS005",
            ("<package>", "path attribute", "missing", 'Add path="..."'),
        )

    def test_no_037_imports_dependson_name_missing_message_tells_attribute_to_add(self):
        self.assert_sample_rule_message_contains(
            "samples/bad/imports-dependson-name-missing/imports.mf",
            "IMPORTS007",
            ("<dependson>", "name attribute", "missing", 'Add name="..."'),
        )

    def test_no_038_form_standard_property_edit_with_matching_field_add_passes(self):
        diagnostics = self.check_temp_xml(
            "Form",
            "aml-38-form-standard-property-matching-field.xml",
            """
<AML>
  <Item type="Form" id="38383838383838383838383838383838" action="add">
    <name>Sample Form</name>
    <height>234</height>
    <width>699</width>
    <Relationships>
      <Item type="Body" id="38383838383838383838383838383839" action="add">
        <source_id keyed_name="Sample Form" type="Form">38383838383838383838383838383838</source_id>
        <Relationships>
          <Item type="Field" id="3838383838383838383838383838383A" action="add">
            <show_help>1</show_help>
            <source_id keyed_name="Sample Body" type="Body">38383838383838383838383838383839</source_id>
            <field_type>text</field_type>
          </Item>
        </Relationships>
      </Item>
    </Relationships>
  </Item>
  <Item type="Field" id="3838383838383838383838383838383A" action="edit">
    <propertytype_id>
      <Item type="Property" action="get" select="id">
        <name>state</name>
        <source_id type="ItemType">39393939393939393939393939393939</source_id>
      </Item>
    </propertytype_id>
  </Item>
</AML>
""".strip(),
        )
        self.assertEqual([], diagnostics, diagnostics)

    def form_with_body(
        self,
        nested_field_xml: str,
        form_id: str,
        body_id: str,
        body_extra: str = "",
    ) -> str:
        nested = f"""
        <Relationships>
{nested_field_xml}
        </Relationships>""" if nested_field_xml else ""
        return f"""<AML>
  <Item type="Form" id="{form_id}" action="add">
    <name>Sample Form</name>
    <height>234</height>
    <width>699</width>
    <Relationships>
      <Item type="Body" id="{body_id}" action="add">
        <source_id keyed_name="Sample Form" type="Form">{form_id}</source_id>
        {body_extra}
        {nested}
      </Item>
    </Relationships>
  </Item>
</AML>"""


if __name__ == "__main__":
    unittest.main()
