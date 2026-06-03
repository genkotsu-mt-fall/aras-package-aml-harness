from pathlib import Path
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]


class ActionListValueCheckTests(unittest.TestCase):
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

    def test_no_001_location_client_target_main_type_generic_passes(self):
        self.assert_sample_passes(
            "samples/good/Action/aml-01-valid-client-main-generic.xml"
        )

    def test_no_002_location_server_target_window_type_url_passes(self):
        self.assert_sample_passes(
            "samples/good/Action/aml-02-valid-server-window-url.xml"
        )

    def test_no_003_target_one_window_type_item_passes(self):
        self.assert_sample_passes("samples/good/Action/aml-03-valid-one-window-item.xml")

    def test_no_004_target_none_type_itemtype_passes(self):
        self.assert_sample_passes(
            "samples/good/Action/aml-04-valid-server-none-itemtype.xml"
        )

    def test_no_005_missing_location_reports_action_required001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-05-missing-location.xml",
            ["ACTION_REQUIRED001"],
        )

    def test_no_006_empty_location_reports_action_required001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-06-empty-location.xml",
            ["ACTION_REQUIRED001"],
        )

    def test_no_007_invalid_location_reports_action_list001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-07-invalid-location.xml",
            ["ACTION_LIST001"],
        )

    def test_no_008_missing_target_reports_action_required001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-08-missing-target.xml",
            ["ACTION_REQUIRED001"],
        )

    def test_no_009_empty_target_reports_action_required001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-09-empty-target.xml",
            ["ACTION_REQUIRED001"],
        )

    def test_no_010_invalid_target_reports_action_list002(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-10-invalid-target.xml",
            ["ACTION_LIST002"],
        )

    def test_no_011_missing_type_reports_action_required001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-11-missing-type.xml",
            ["ACTION_REQUIRED001"],
        )

    def test_no_012_empty_type_reports_action_required001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-12-empty-type.xml",
            ["ACTION_REQUIRED001"],
        )

    def test_no_013_invalid_type_reports_action_list003(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-13-invalid-type.xml",
            ["ACTION_LIST003"],
        )

    def test_no_014_multiple_invalid_values_report_all_action_list_rules(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-14-multiple-invalid-values.xml",
            ["ACTION_LIST001", "ACTION_LIST002", "ACTION_LIST003"],
        )

    def test_no_015_trimmed_values_pass(self):
        self.assert_sample_passes("samples/good/Action/aml-15-trimmed-values.xml")

    def test_no_016_case_sensitive_values_report_all_action_list_rules(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-16-case-sensitive-values.xml",
            ["ACTION_LIST001", "ACTION_LIST002", "ACTION_LIST003"],
        )

    def test_no_017_outside_action_directory_skips_action_list_check(self):
        self.assert_sample_passes(
            "samples/good/Method/aml-17-action-values-outside-action-path.xml"
        )

    def test_no_018_non_action_item_skips_action_list_check(self):
        self.assert_sample_passes("samples/good/Action/aml-18-non-action-item-ignored.xml")

    def test_no_019_method_reference_passes(self):
        self.assert_sample_passes("samples/good/Action/aml-19-method-reference.xml")

    def test_no_020_non_aml_root_reports_only_aml001(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-20-non-aml-root.xml",
            ["AML001"],
        )

    def test_no_021_multiple_action_items_reports_invalid_second_target(self):
        self.assert_sample_reports_rules(
            "samples/bad/Action/aml-21-multiple-action-items.xml",
            ["ACTION_LIST002"],
        )


if __name__ == "__main__":
    unittest.main()
