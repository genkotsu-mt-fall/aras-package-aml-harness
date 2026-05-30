from pathlib import Path
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]


class ItemTypeSequencePropertyCheckTests(unittest.TestCase):
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

    def test_no_001_sequence_property_required_zero_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-17-sequence-required-zero.xml"
        )

    def test_no_002_non_sequence_property_required_one_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-18-non-sequence-required-one.xml"
        )

    def test_no_003_parent_itemtype_edit_sequence_required_zero_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-19-sequence-required-zero-parent-edit.xml"
        )

    def test_no_004_sequence_property_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-14-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_005_only_sequence_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-15-multiple-properties-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_006_sequence_property_missing_is_required_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-20-sequence-missing-is-required.xml"
        )

    def test_no_007_sequence_property_empty_is_required_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-21-sequence-empty-is-required.xml"
        )

    def test_no_008_sequence_property_missing_data_source_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-22-sequence-missing-data-source.xml"
        )

    def test_no_009_top_level_property_sequence_required_one_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-23-top-level-property-sequence-required-one.xml"
        )

    def test_no_010_relationshiptype_relationship_itemtype_property_passes(self):
        self.assert_sample_passes(
            "samples/good/RelationshipType/aml-11-relationshiptype-sequence-property.xml"
        )

    def test_no_011_sequence_definition_passes(self):
        self.assert_sample_passes("samples/good/ItemType/aml-24-sequence-definition.xml")

    def test_no_012_sequence_property_unresolved_references_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-25-sequence-unresolved-references.xml"
        )

    def test_no_013_parent_itemtype_edit_sequence_required_one_reports_itype_sequence001(
        self,
    ):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-16-sequence-required-one-parent-edit.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_014_later_top_level_itemtype_sequence_required_one_reports_itype_sequence001(
        self,
    ):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-17-later-itemtype-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )


if __name__ == "__main__":
    unittest.main()
