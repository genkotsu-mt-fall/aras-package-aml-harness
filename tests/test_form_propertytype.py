from pathlib import Path
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]


class FormPropertyTypeCheckTests(unittest.TestCase):
    def check_sample(self, relative_path: str) -> list[Diagnostic]:
        return check_file(ROOT_DIR / relative_path)

    def assert_sample_passes(self, relative_path: str):
        diagnostics = self.check_sample(relative_path)
        self.assertEqual([], diagnostics, f"{relative_path}: {diagnostics}")

    def assert_sample_reports_rules(self, relative_path: str, expected_rule_ids: list[str]):
        diagnostics = self.check_sample(relative_path)
        actual_rule_ids = [diagnostic.rule_id for diagnostic in diagnostics]
        self.assertEqual(
            expected_rule_ids,
            actual_rule_ids,
            f"{relative_path}: {diagnostics}",
        )

    def test_no_001_itemtype_property_direct_guid_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-01-itemtype-property-guid.xml")

    def test_no_002_standard_property_edit_completion_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-02-standard-property-edit.xml")

    def test_no_003_html_state_display_field_without_edit_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-03-html-state-field.xml")

    def test_no_004_standard_field_name_non_standard_keyed_name_passes(self):
        self.assert_sample_passes(
            "samples/good/Form/aml-04-standard-field-name-non-standard-keyed-name.xml"
        )

    def test_no_005_standard_keyed_name_direct_guid_reports_form002(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-05-standard-property-direct-guid.xml",
            ["FORM002"],
        )

    def test_no_006_direct_propertytype_id_must_be_guid(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-06-invalid-propertytype-guid.xml",
            ["FORM001"],
        )

    def test_no_007_standard_property_edit_requires_matching_add_field(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-07-standard-property-edit-without-add-field.xml",
            ["FORM003"],
        )

    def test_no_008_standard_property_edit_property_must_use_action_get_select_id(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-08-standard-property-not-get-select-id.xml",
            ["FORM004"],
        )

        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-08-standard-property-missing-select-id.xml",
            ["FORM004"],
        )

    def test_no_009_standard_property_edit_name_must_match_field_name(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-09-standard-property-name-mismatch.xml",
            ["FORM005"],
        )

    def test_no_010_standard_property_edit_source_must_be_itemtype(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-10-standard-property-source-not-itemtype.xml",
            ["FORM006"],
        )

    def test_no_011_direct_propertytype_id_rejects_31_chars(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-11-propertytype-guid-31-chars.xml",
            ["FORM001"],
        )

    def test_no_012_direct_propertytype_id_rejects_33_chars(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-12-propertytype-guid-33-chars.xml",
            ["FORM001"],
        )

    def test_no_013_standard_add_field_name_without_edit_passes(self):
        self.assert_sample_passes(
            "samples/good/Form/aml-13-standard-add-field-name-without-edit.xml"
        )

    def test_no_014_non_standard_edit_completion_like_field_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-14-non-standard-edit-completion.xml")

    def test_no_015_non_form_path_skips_form_specific_checks(self):
        self.assert_sample_passes("samples/good/ItemType/aml-15-form-like-field-outside-form-path.xml")


if __name__ == "__main__":
    unittest.main()
