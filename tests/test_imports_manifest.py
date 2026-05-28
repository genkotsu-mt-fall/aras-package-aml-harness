from pathlib import Path
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]


class ImportsManifestCheckTests(unittest.TestCase):
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

    def assert_sample_reports_one_of_rule_sequences(
        self, relative_path: str, expected_rule_id_sequences: list[list[str]]
    ):
        diagnostics = self.check_sample(relative_path)
        actual_rule_ids = [diagnostic.rule_id for diagnostic in diagnostics]
        self.assertIn(
            actual_rule_ids,
            expected_rule_id_sequences,
            f"{relative_path}: {diagnostics}",
        )

    def assert_sample_does_not_report_imports_rules(self, relative_path: str):
        diagnostics = self.check_sample(relative_path)
        actual_rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
        imports_rule_ids = {
            "IMPORTS001",
            "IMPORTS002",
            "IMPORTS003",
            "IMPORTS004",
            "IMPORTS005",
            "IMPORTS006",
            "IMPORTS007",
        }
        self.assertEqual(
            set(),
            actual_rule_ids & imports_rule_ids,
            f"{relative_path}: {diagnostics}",
        )

    def test_no_001_single_package_with_existing_explicit_path_passes(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-01-single-explicit-path/imports.mf"
        )

    def test_no_002_multiple_standard_packages_with_dot_path_pass(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-02-multiple-standard-dot-path/imports.mf"
        )

    def test_no_003_single_package_with_dot_path_passes(self):
        self.assert_sample_passes("samples/good/Imports/aml-03-single-dot-path/imports.mf")

    def test_no_004_standard_package_with_existing_explicit_path_passes(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-04-standard-explicit-path/imports.mf"
        )

    def test_no_005_invalid_root_reports_imports001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-05-invalid-root/imports.mf",
            ["IMPORTS001"],
        )

    def test_no_006_no_package_reports_imports002(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-06-no-package/imports.mf",
            ["IMPORTS002"],
        )

    def test_no_007_non_package_child_reports_imports003(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-07-non-package-child/imports.mf",
            ["IMPORTS003"],
        )

    def test_no_008_package_missing_name_reports_imports004(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-08-missing-name/imports.mf",
            ["IMPORTS004"],
        )

    def test_no_009_package_missing_path_reports_imports005(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-09-missing-path/imports.mf",
            ["IMPORTS005"],
        )

    def test_no_010_missing_explicit_path_target_reports_imports006(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-10-missing-path-target/imports.mf",
            ["IMPORTS006"],
        )

    def test_no_011_dependson_missing_name_reports_imports007(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-11-dependson-missing-name/imports.mf",
            ["IMPORTS007"],
        )

    def test_no_012_package_without_dependson_passes(self):
        self.assert_sample_passes("samples/good/Imports/aml-12-no-dependson/imports.mf")

    def test_no_013_nested_dependson_is_out_of_scope_and_passes(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-13-nested-dependson/imports.mf"
        )

    def test_no_014_short_custom_package_name_passes(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-14-short-custom-name/imports.mf"
        )

    def test_no_015_custom_package_with_dot_path_passes(self):
        self.assert_sample_passes("samples/good/Imports/aml-15-custom-dot-path/imports.mf")

    def test_no_016_custom_package_without_plm_dependson_passes(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-16-custom-no-plm-dependson/imports.mf"
        )

    def test_no_017_invalid_imports_xml_reports_parse_error(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-17-invalid-xml/imports.mf",
            ["AML000"],
        )

    def test_no_018_regular_aml_with_multiple_top_level_items_still_passes(self):
        self.assert_sample_passes("samples/good/Base/aml-18-multiple-top-level-items.xml")
        self.assert_sample_does_not_report_imports_rules(
            "samples/good/Base/aml-18-multiple-top-level-items.xml"
        )

    def test_no_019_imports_mf_with_aml_root_reports_imports001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Imports/aml-19-imports-mf-aml-root/imports.mf",
            ["IMPORTS001"],
        )

    def test_no_020_imports_path_contents_are_not_recursed_and_passes(self):
        self.assert_sample_passes(
            "samples/good/Imports/aml-20-path-contents-not-recursed/imports.mf"
        )

    def test_no_021_only_non_package_child_reports_imports_structure_error(self):
        self.assert_sample_reports_one_of_rule_sequences(
            "samples/bad/Imports/aml-21-only-non-package-child/imports.mf",
            [["IMPORTS002"], ["IMPORTS003"], ["IMPORTS002", "IMPORTS003"]],
        )


if __name__ == "__main__":
    unittest.main()
