from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aml_harness.base import Diagnostic, check_file


FORM_ID = "CAF99D0A8E6E44E9A681C38015FACE91"
BODY_ID = "83907DEF8B3044A08BDCBB77B1C0517E"
FIELD_ID = "FD36E7C8554E49098C55D72307BF1639"


class FormPackageCheckTests(unittest.TestCase):
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

    def form(self, body_xml: str = "", fields: str = "<height>300</height><width>784</width><name>Part</name>") -> str:
        relationships = f"<Relationships>{body_xml}</Relationships>" if body_xml else ""
        return f"""<AML>
  <Item type="Form" id="{FORM_ID}" action="add">
    {fields}
    {relationships}
  </Item>
</AML>"""

    def body(self, content: str = "", relationships: str = "") -> str:
        nested = f"<Relationships>{relationships}</Relationships>" if relationships else ""
        return f"""<Item type="Body" id="{BODY_ID}" action="add">
      {content}
      {nested}
    </Item>"""

    def field(self, content: str = "", relationships: str = "", action: str = "add") -> str:
        nested = f"<Relationships>{relationships}</Relationships>" if relationships else ""
        return f"""<Item type="Field" id="{FIELD_ID}" action="{action}">
      {content}
      {nested}
    </Item>"""

    def valid_body_content(self) -> str:
        return f"""<source_id keyed_name="Part" type="Form">{FORM_ID}</source_id>"""

    def valid_field_content(self) -> str:
        return f"""<show_help>1</show_help>
      <source_id keyed_name="{BODY_ID}" type="Body">{BODY_ID}</source_id>
      <name>description</name>"""

    def test_task_019_no_001_form_body_field_required_fields_pass(self):
        self.assert_xml_passes(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field(self.valid_field_content()))),
        )

    def test_task_019_no_002_to_004_form_required_fields(self):
        for fields in (
            "<width>784</width><name>Part</name>",
            "<height>300</height><name>Part</name>",
            "<height>300</height><width>784</width>",
        ):
            with self.subTest(fields=fields):
                self.assert_xml_reports_rules(
                    "Form",
                    self.form(fields=fields),
                    ["FORM_REQUIRED001"],
                )

    def test_task_019_no_006_body_missing_source_reports_required(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body("<sort_order>128</sort_order>")),
            ["FORM_BODY_REQUIRED001"],
        )

    def test_task_019_no_007_to_010_body_list_values(self):
        self.assert_xml_passes(
            "Form",
            self.form(self.body(f"<bg_attach>scroll</bg_attach>{self.valid_body_content()}")),
        )
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(f"<bg_attach>absolute</bg_attach>{self.valid_body_content()}")),
            ["FORM_BODY_LIST001"],
        )
        self.assert_xml_passes(
            "Form",
            self.form(self.body(f"<bg_repeat>no-repeat</bg_repeat>{self.valid_body_content()}")),
        )
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(f"<bg_repeat>none</bg_repeat>{self.valid_body_content()}")),
            ["FORM_BODY_LIST001"],
        )

    def test_task_019_no_012_013_field_missing_required_fields(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field(f"""<source_id keyed_name="{BODY_ID}" type="Body">{BODY_ID}</source_id><name>description</name>"""))),
            ["FORM_FIELD_REQUIRED001"],
        )
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field("<show_help>1</show_help><name>description</name>"))),
            ["FORM_FIELD_REQUIRED001"],
        )

    def test_task_019_no_014_to_025_field_list_values(self):
        valid_cases = {
            "field_type": "textarea",
            "font_weight": "bold",
            "label_position": "top",
            "display_length_unit": "px",
            "clip_overflow": "hidden",
            "orientation": "vertical",
            "positioning": "relative",
            "text_align": "center",
        }
        for name, value in valid_cases.items():
            with self.subTest(name=name):
                self.assert_xml_passes(
                    "Form",
                    self.form(
                        self.body(
                            self.valid_body_content(),
                            self.field(f"<{name}>{value}</{name}>{self.valid_field_content()}"),
                        )
                    ),
                )

        invalid_cases = {
            "field_type": "invalid_type",
            "font_weight": "bolder",
            "label_position": "middle",
            "display_length_unit": "vw",
            "clip_overflow": "clip",
            "orientation": "diagonal",
            "positioning": "sticky",
            "text_align": "justify",
            "behavior": "inherit",
        }
        for name, value in invalid_cases.items():
            with self.subTest(name=name):
                self.assert_xml_reports_rules(
                    "Form",
                    self.form(
                        self.body(
                            self.valid_body_content(),
                            self.field(f"<{name}>{value}</{name}>{self.valid_field_content()}"),
                        )
                    ),
                    ["FORM_FIELD_LIST001"],
                )

    def test_task_019_no_018_019_field_edit_required_skip_but_list_check_runs(self):
        self.assert_xml_passes(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field("<name>description</name>", action="edit"))),
        )
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field("<field_type>bad_type</field_type><name>description</name>", action="edit"))),
            ["FORM_FIELD_LIST001"],
        )

    def test_task_019_no_026_to_029_field_event_checks(self):
        valid_field_event = f"""<Item type="Field Event" id="B23EB5707693445DBC77E46887D505E4" action="add">
        <field_event>onchange</field_event>
        <source_id keyed_name="description" type="Field">{FIELD_ID}</source_id>
      </Item>"""
        self.assert_xml_passes(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field(self.valid_field_content(), valid_field_event))),
        )

        missing_source = """<Item type="Field Event" id="B23EB5707693445DBC77E46887D505E4" action="add">
        <field_event>onchange</field_event>
      </Item>"""
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field(self.valid_field_content(), missing_source))),
            ["FORM_FIELD_EVENT_REQUIRED001"],
        )

        invalid_event = f"""<Item type="Field Event" id="B23EB5707693445DBC77E46887D505E4" action="add">
        <field_event>onhover</field_event>
        <source_id keyed_name="description" type="Field">{FIELD_ID}</source_id>
      </Item>"""
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field(self.valid_field_content(), invalid_event))),
            ["FORM_FIELD_EVENT_LIST001"],
        )

    def test_task_019_no_030_to_033_form_event_checks(self):
        valid_form_event = f"""<Item type="Form Event" id="05F15EA49BA74DA2B82934315EA71F88" action="add">
      <form_event>onformpopulated</form_event>
      <source_id keyed_name="Part" type="Form">{FORM_ID}</source_id>
    </Item>"""
        self.assert_xml_passes("Form", self.form(self.body(self.valid_body_content()) + valid_form_event))

        missing_source = """<Item type="Form Event" id="05F15EA49BA74DA2B82934315EA71F88" action="add">
      <form_event>onformpopulated</form_event>
    </Item>"""
        self.assert_xml_reports_rules(
            "Form",
            self.form(missing_source),
            ["FORM_FORM_EVENT_REQUIRED001"],
        )

        invalid_event = f"""<Item type="Form Event" id="05F15EA49BA74DA2B82934315EA71F88" action="add">
      <form_event>onsubmit</form_event>
      <source_id keyed_name="Part" type="Form">{FORM_ID}</source_id>
    </Item>"""
        self.assert_xml_reports_rules(
            "Form",
            self.form(invalid_event),
            ["FORM_FORM_EVENT_LIST001"],
        )

    def test_task_019_no_043_to_050_behavior_presence_checks(self):
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(f"<behavior>inherit</behavior>{self.valid_body_content()}")),
            ["FORM_BODY_LIST001"],
        )

        field_event_invalid_behavior = f"""<Item type="Field Event" id="B23EB5707693445DBC77E46887D505E4" action="add">
        <behavior>inherit</behavior>
        <field_event>onchange</field_event>
        <source_id keyed_name="description" type="Field">{FIELD_ID}</source_id>
      </Item>"""
        self.assert_xml_reports_rules(
            "Form",
            self.form(self.body(self.valid_body_content(), self.field(self.valid_field_content(), field_event_invalid_behavior))),
            ["FORM_FIELD_EVENT_LIST001"],
        )

        form_event_invalid_behavior = f"""<Item type="Form Event" id="05F15EA49BA74DA2B82934315EA71F88" action="add">
      <behavior>inherit</behavior>
      <form_event>onformpopulated</form_event>
      <source_id keyed_name="Part" type="Form">{FORM_ID}</source_id>
    </Item>"""
        self.assert_xml_reports_rules(
            "Form",
            self.form(form_event_invalid_behavior),
            ["FORM_FORM_EVENT_LIST001"],
        )

    def test_task_019_no_051_outside_form_path_skips_form_checks(self):
        self.assert_xml_passes(
            "ItemType",
            self.form(fields="<width>784</width><name>Part</name>"),
        )


if __name__ == "__main__":
    unittest.main()
