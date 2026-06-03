from pathlib import Path
import tempfile
import unittest

from aml_harness.base import Diagnostic, check_file


ROOT_DIR = Path(__file__).resolve().parents[1]
KNOWN_PUBLIC_SEQUENCE_EXCEPTION = (
    "public/com/aras/innovator/masspromote/ItemType/mpo_MassPromotion.xml"
)


class ItemTypeSequencePropertyCheckTests(unittest.TestCase):
    def check_sample(self, relative_path: str) -> list[Diagnostic]:
        return check_file(ROOT_DIR / relative_path)

    def write_temp_public_itemtype_sample(self, relative_path: str, text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_temp_public_samples(self, samples: dict[str, str]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root_dir = Path(temp_dir.name)
        for relative_path, text in samples.items():
            path = root_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root_dir

    def check_public_files(self, root_dir: Path) -> list[Diagnostic]:
        diagnostics = []
        for path in sorted((root_dir / "public").glob("**/*.xml")):
            diagnostics.extend(check_file(path))
        return diagnostics

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

    def test_no_001_known_public_exception_direct_check_passes(self):
        path = self.write_temp_public_itemtype_sample(
            KNOWN_PUBLIC_SEQUENCE_EXCEPTION,
            MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual([], diagnostics, f"{path}: {diagnostics}")

    def test_no_002_sequence_property_required_zero_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-17-sequence-required-zero.xml"
        )

    def test_no_003_non_sequence_property_required_one_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-18-non-sequence-required-one.xml"
        )

    def test_no_004_top_level_property_sequence_required_one_passes(self):
        self.assert_sample_passes(
            "samples/good/Property/top-level-sequence-required-one.xml"
        )

    def test_no_005_sequence_property_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-14-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_006_public_other_file_reports_itype_sequence001(self):
        path = self.write_temp_public_itemtype_sample(
            "public/com/aras/innovator/masspromote/ItemType/Other.xml",
            PUBLIC_OTHER_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual(
            ["ITYPE_SEQUENCE001"],
            [diagnostic.rule_id for diagnostic in diagnostics],
            f"{path}: {diagnostics}",
        )

    def test_no_007_exception_filename_outside_itemtype_reports_itype_sequence001(self):
        path = self.write_temp_public_itemtype_sample(
            "public/com/aras/innovator/masspromote/Other/mpo_MassPromotion.xml",
            MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual(
            ["ITYPE_SEQUENCE001"],
            [diagnostic.rule_id for diagnostic in diagnostics],
            f"{path}: {diagnostics}",
        )

    def test_no_008_masspromote_other_folder_reports_itype_sequence001(self):
        path = self.write_temp_public_itemtype_sample(
            "public/com/aras/innovator/masspromote/Other/Other.xml",
            PUBLIC_OTHER_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual(
            ["ITYPE_SEQUENCE001"],
            [diagnostic.rule_id for diagnostic in diagnostics],
            f"{path}: {diagnostics}",
        )

    def test_no_009_relationshiptype_nested_itemtype_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/RelationshipType/aml-12-relationshiptype-nested-itemtype-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_010_sequence_property_missing_is_required_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-20-sequence-missing-is-required.xml"
        )

    def test_no_011_sequence_property_empty_is_required_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-21-sequence-empty-is-required.xml"
        )

    def test_no_012_parent_itemtype_edit_sequence_required_one_reports_itype_sequence001(
        self,
    ):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-16-sequence-required-one-parent-edit.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_013_other_package_itemtype_exception_filename_passes(self):
        path = self.write_temp_public_itemtype_sample(
            "public/com/aras/innovator/other/ItemType/mpo_MassPromotion.xml",
            MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual([], diagnostics, f"{path}: {diagnostics}")

    def test_no_014_real_public_exception_file_direct_check_passes(self):
        self.assert_sample_passes(KNOWN_PUBLIC_SEQUENCE_EXCEPTION)

    def test_no_015_public_batch_does_not_classify_known_exception(self):
        root_dir = self.write_temp_public_samples(
            {
                KNOWN_PUBLIC_SEQUENCE_EXCEPTION: (
                    MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML
                )
            }
        )
        diagnostics = self.check_public_files(root_dir)
        self.assertEqual([], diagnostics, f"{root_dir}: {diagnostics}")

    def test_no_016_sequence_definition_passes(self):
        self.assert_sample_passes(
            "public/com/aras/innovator/masspromote/Sequence/mpo_Number.xml"
        )

    def test_relationshiptype_direct_property_passes(self):
        self.assert_sample_passes(
            "samples/good/RelationshipType/aml-11-relationshiptype-sequence-property.xml"
        )

    def test_later_top_level_itemtype_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-17-later-itemtype-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_sequence_property_missing_data_source_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-22-sequence-missing-data-source.xml"
        )

    def test_sequence_definition_passes(self):
        self.assert_sample_passes("samples/good/ItemType/aml-24-sequence-definition.xml")

    def test_sequence_property_unresolved_references_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-25-sequence-unresolved-references.xml"
        )

    def test_parent_itemtype_edit_sequence_required_zero_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-19-sequence-required-zero-parent-edit.xml"
        )

    def test_only_sequence_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-15-multiple-properties-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )


MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML = """
<AML>
  <Item type="ItemType" id="5A549B2EDD3C4CBB9F8797902EE2EBE2" action="add">
    <name>mpo_MassPromotion</name>
    <Relationships>
      <Item type="Property" id="1737B093CFF0421E89BC303F884D201D" action="add">
        <name>item_number</name>
        <label xml:lang="en">Number</label>
        <data_source keyed_name="mpo_Number">3A3FADE77BAF4DD9A090145885F06CE7</data_source>
        <data_type>sequence</data_type>
        <is_required>1</is_required>
        <source_id keyed_name="mpo_MassPromotion" type="ItemType" name="mpo_MassPromotion">5A549B2EDD3C4CBB9F8797902EE2EBE2</source_id>
      </Item>
    </Relationships>
  </Item>
</AML>
""".strip()


PUBLIC_OTHER_SEQUENCE_REQUIRED_ONE_XML = """
<AML>
  <Item type="ItemType" id="33333333333333333333333333333333" action="add">
    <name>Public Other Type</name>
    <Relationships>
      <Item type="Property" id="44444444444444444444444444444444" action="add">
        <name>item_number</name>
        <data_type>sequence</data_type>
        <is_required>1</is_required>
      </Item>
    </Relationships>
  </Item>
</AML>
""".strip()


if __name__ == "__main__":
    unittest.main()
