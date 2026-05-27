from pathlib import Path
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]


class BaseDeleteCheckTests(unittest.TestCase):
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

    def assert_does_not_report_rules(self, relative_path: str, unexpected_rule_ids: set[str]):
        diagnostics = self.check_sample(relative_path)
        actual_rule_ids = {diagnostic.rule_id for diagnostic in diagnostics}
        reported_unexpected = actual_rule_ids & unexpected_rule_ids
        self.assertEqual(
            set(),
            reported_unexpected,
            f"{relative_path}: {diagnostics}",
        )

    def test_no_001_top_level_view_delete_with_source_id_where_passes(self):
        self.assert_sample_passes(
            "samples/good/Base/aml-01-view-delete-where-source-id.xml"
        )

    def test_no_002_top_level_form_delete_with_name_where_passes(self):
        self.assert_sample_passes("samples/good/Base/aml-02-form-delete-where-name.xml")

    def test_no_003_itemtype_add_with_view_and_form_delete_passes(self):
        self.assert_sample_passes(
            "samples/good/Base/aml-03-itemtype-add-with-view-form-delete.xml"
        )

    def test_no_004_delete_without_id_or_where_reports_only_aml006(self):
        self.assert_sample_reports_rules(
            "samples/bad/Base/aml-04-delete-without-id-or-where.xml",
            ["AML006"],
        )

    def test_no_005_delete_with_empty_where_reports_only_aml006(self):
        self.assert_sample_reports_rules(
            "samples/bad/Base/aml-05-delete-empty-where.xml",
            ["AML006"],
        )

    def test_no_006_delete_with_blank_where_reports_only_aml006(self):
        self.assert_sample_reports_rules(
            "samples/bad/Base/aml-06-delete-blank-where.xml",
            ["AML006"],
        )

    def test_no_007_unsupported_action_still_reports_aml005(self):
        self.assert_sample_reports_rules(
            "samples/bad/Base/aml-07-unsupported-action.xml",
            ["AML005"],
        )

    def test_no_008_add_without_id_still_reports_aml006(self):
        self.assert_sample_reports_rules(
            "samples/bad/Base/aml-08-add-without-id.xml",
            ["AML006"],
        )

    def test_no_009_edit_without_id_still_reports_aml006(self):
        self.assert_sample_reports_rules(
            "samples/bad/Base/aml-09-edit-without-id.xml",
            ["AML006"],
        )

    def test_no_010_add_with_id_still_passes(self):
        self.assert_sample_passes("samples/good/Base/aml-10-add-with-id.xml")

    def test_no_011_edit_with_id_still_passes(self):
        self.assert_sample_passes("samples/good/Base/aml-11-edit-with-id.xml")

    def test_no_012_public_check_failed_itemtype_files_pass(self):
        public_files = [
            "public/PLM/Import/ItemType/Design To Goal.xml",
            "public/PLM/Import/ItemType/Engineering Efficiency.xml",
            "public/PLM/Import/ItemType/Engineering Optimization.xml",
            "public/PLM/Import/ItemType/PE_ReverseItemsFedCAD.xml",
            "public/PLM/Import/ItemType/PE_ReverseItemsFedPart.xml",
            "public/PLM/Import/ItemType/Product Innovation.xml",
            "public/PLM/Import/ItemType/Time To Manufacturing.xml",
        ]

        for relative_path in public_files:
            with self.subTest(relative_path=relative_path):
                self.assert_sample_passes(relative_path)

    def test_no_013_all_public_itemtype_files_do_not_report_aml005_or_aml006(self):
        itemtype_dir = ROOT_DIR / "public" / "PLM" / "Import" / "ItemType"
        public_files = sorted(itemtype_dir.glob("*.xml"))
        self.assertEqual(30, len(public_files), f"Unexpected public file count: {public_files}")

        for path in public_files:
            relative_path = str(path.relative_to(ROOT_DIR))
            with self.subTest(relative_path=relative_path):
                self.assert_sample_passes(relative_path)
                self.assert_does_not_report_rules(relative_path, {"AML005", "AML006"})


if __name__ == "__main__":
    unittest.main()
