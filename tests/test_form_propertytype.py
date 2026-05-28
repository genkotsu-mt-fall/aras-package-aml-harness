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

    def test_no_001_direct_keyed_name_match_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-16-direct-keyed-name-match.xml")

    def test_no_002_direct_keyed_name_mismatch_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-17-direct-keyed-name-mismatch.xml")

    def test_no_003_standard_property_edit_name_match_passes(self):
        self.assert_sample_passes(
            "samples/good/Form/aml-18-standard-property-edit-name-match.xml"
        )

    def test_no_004_standard_property_edit_name_mismatch_passes(self):
        self.assert_sample_passes(
            "samples/good/Form/aml-19-standard-property-edit-name-mismatch.xml"
        )

    def test_no_005_non_standard_property_edit_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-20-non-standard-property-edit.xml")

    def test_no_006_direct_propertytype_id_must_be_guid(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-13-direct-propertytype-id-not-guid.xml",
            ["FORM001"],
        )

    def test_no_007_standard_property_direct_keyed_name_reports_form002(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-14-standard-property-direct-keyed-name.xml",
            ["FORM002"],
        )

    def test_no_008_standard_property_edit_requires_matching_add_field(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-15-standard-property-edit-without-add-field.xml",
            ["FORM003"],
        )

    def test_no_009_standard_property_edit_property_must_use_action_get(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-16-standard-property-action-not-get.xml",
            ["FORM004"],
        )

    def test_no_010_standard_property_edit_property_must_select_id(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-17-standard-property-missing-select.xml",
            ["FORM004"],
        )

    def test_no_011_standard_property_edit_source_must_be_itemtype(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-18-standard-property-source-not-itemtype.xml",
            ["FORM006"],
        )

    def test_no_012_direct_propertytype_id_rejects_31_chars(self):
        self.assert_sample_reports_rules(
            "samples/bad/Form/aml-19-direct-propertytype-id-guid-31-chars.xml",
            ["FORM001"],
        )

    def test_no_013_empty_field_name_standard_property_edit_passes(self):
        self.assert_sample_passes(
            "samples/good/Form/aml-21-empty-field-name-standard-property-edit.xml"
        )

    def test_no_014_non_form_path_skips_form_specific_checks(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-16-form-like-field-outside-form-path.xml"
        )

    def test_no_015_old_form005_bad_sample_now_passes(self):
        self.assert_sample_passes("samples/good/Form/aml-22-form005-old-bad-sample-now-valid.xml")

    def test_no_016_savedsearch_save_dialog_public_file_passes(self):
        path = ROOT_DIR / "public/com/aras/innovator/search/Form/SavedSearch Save Dialog.xml"
        if not path.exists():
            self.skipTest(f"{path} is not available")

        diagnostics = check_file(path)
        self.assertEqual([], diagnostics, f"{path}: {diagnostics}")

    def test_no_017_public_xml_files_pass(self):
        public_dir = ROOT_DIR / "public"
        if not public_dir.exists():
            self.skipTest(f"{public_dir} is not available")

        paths = sorted(public_dir.glob("**/*.xml"))
        if not paths:
            self.skipTest(f"{public_dir} does not contain XML files")

        diagnostics = []
        for path in paths:
            diagnostics.extend(check_file(path))

        self.assertEqual([], diagnostics)


if __name__ == "__main__":
    unittest.main()
