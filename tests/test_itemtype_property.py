from pathlib import Path
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]


class ItemTypePropertyPlacementCheckTests(unittest.TestCase):
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

    def test_no_001_standard_state_property_edit_passes(self):
        self.assert_sample_passes("samples/good/ItemType/aml-01-standard-state-edit.xml")

    def test_no_002_custom_property_add_under_itemtype_add_passes(self):
        self.assert_sample_passes("samples/good/ItemType/aml-02-custom-property-add.xml")

    def test_no_003_custom_property_add_under_itemtype_edit_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-03-custom-property-add-under-edit.xml"
        )

    def test_no_004_standard_state_property_add_reports_itemtype001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-04-standard-state-add.xml",
            ["ITEMTYPE001"],
        )

    def test_no_005_standard_created_on_property_add_reports_itemtype001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-05-standard-created-on-add.xml",
            ["ITEMTYPE001"],
        )

    def test_no_006_release_date_property_add_passes(self):
        self.assert_sample_passes("samples/good/ItemType/aml-06-release-date-add.xml")

    def test_no_007_non_itemtype_path_skips_itemtype_property_check(self):
        self.assert_sample_passes(
            "samples/good/Other/aml-07-standard-state-add-outside-itemtype-path.xml"
        )

    def test_no_008_nested_relationship_property_skips_itemtype_property_check(self):
        self.assert_sample_passes("samples/good/ItemType/aml-08-nested-property-add.xml")

    def test_no_009_form_path_skips_itemtype_property_check(self):
        self.assert_sample_passes("samples/good/Form/aml-09-form-field-regression.xml")

    def test_no_010_relationshiptype_path_skips_itemtype_property_check(self):
        self.assert_sample_passes(
            "samples/good/RelationshipType/aml-10-embedded-itemtype-property.xml"
        )

    def test_no_011_standard_classification_property_add_reports_itemtype001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-11-standard-classification-add.xml",
            ["ITEMTYPE001"],
        )

    def test_no_012_multiple_top_level_itemtypes_valid_placement_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-12-multiple-itemtypes-valid.xml"
        )

    def test_no_013_later_top_level_itemtype_standard_state_add_reports_itemtype001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-13-multiple-itemtypes-later-state-add.xml",
            ["ITEMTYPE001"],
        )


if __name__ == "__main__":
    unittest.main()
