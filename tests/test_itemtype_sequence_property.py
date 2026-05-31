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

    def check_public_files_with_known_sequence_exception(
        self, root_dir: Path
    ) -> tuple[list[Diagnostic], list[Diagnostic]]:
        known_sequence_exceptions = []
        unexpected_diagnostics = []
        for path in sorted((root_dir / "public").glob("**/*.xml")):
            relative_path = path.relative_to(root_dir).as_posix()
            for diagnostic in check_file(path):
                if (
                    diagnostic.rule_id == "ITYPE_SEQUENCE001"
                    and relative_path == KNOWN_PUBLIC_SEQUENCE_EXCEPTION
                ):
                    known_sequence_exceptions.append(diagnostic)
                else:
                    unexpected_diagnostics.append(diagnostic)
        return known_sequence_exceptions, unexpected_diagnostics

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

    def test_no_002_sequence_property_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-14-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_003_non_sequence_property_required_one_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-18-non-sequence-required-one.xml"
        )

    def test_no_004_top_level_property_sequence_required_one_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-23-top-level-property-sequence-required-one.xml"
        )

    def test_no_005_relationshiptype_direct_property_passes(self):
        self.assert_sample_passes(
            "samples/good/RelationshipType/aml-11-relationshiptype-sequence-property.xml"
        )

    def test_no_006_sequence_property_missing_is_required_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-20-sequence-missing-is-required.xml"
        )

    def test_no_007_sequence_property_empty_is_required_passes(self):
        self.assert_sample_passes(
            "samples/good/ItemType/aml-21-sequence-empty-is-required.xml"
        )

    def test_no_008_public_path_direct_check_reports_itype_sequence001(self):
        path = self.write_temp_public_itemtype_sample(
            "public/Custom/Import/ItemType/aml-08-public-path-sequence-required-one.xml",
            PUBLIC_PATH_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual(
            ["ITYPE_SEQUENCE001"],
            [diagnostic.rule_id for diagnostic in diagnostics],
            f"{path}: {diagnostics}",
        )

    def test_no_009_known_public_exception_direct_check_reports_itype_sequence001(self):
        path = self.write_temp_public_itemtype_sample(
            "public/com/aras/innovator/masspromote/ItemType/mpo_MassPromotion.xml",
            MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML,
        )
        diagnostics = check_file(path)
        self.assertEqual(
            ["ITYPE_SEQUENCE001"],
            [diagnostic.rule_id for diagnostic in diagnostics],
            f"{path}: {diagnostics}",
        )

    def test_no_010_public_batch_allows_only_known_sequence_exception(self):
        root_dir = self.write_temp_public_samples(
            {
                KNOWN_PUBLIC_SEQUENCE_EXCEPTION: (
                    MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML
                )
            }
        )
        known_sequence_exceptions, unexpected_diagnostics = (
            self.check_public_files_with_known_sequence_exception(root_dir)
        )
        self.assertEqual(
            [],
            unexpected_diagnostics,
            f"{root_dir}: {unexpected_diagnostics}",
        )
        self.assertEqual(
            [KNOWN_PUBLIC_SEQUENCE_EXCEPTION],
            [
                Path(diagnostic.file_path).relative_to(root_dir).as_posix()
                for diagnostic in known_sequence_exceptions
            ],
        )

    def test_no_011_other_public_file_is_unexpected_in_public_batch(self):
        other_public_path = (
            "public/com/aras/innovator/other/ItemType/"
            "aml-10-public-other-sequence-required-one.xml"
        )
        root_dir = self.write_temp_public_samples(
            {
                KNOWN_PUBLIC_SEQUENCE_EXCEPTION: (
                    MPO_MASS_PROMOTION_SEQUENCE_REQUIRED_ONE_XML
                ),
                other_public_path: PUBLIC_OTHER_SEQUENCE_REQUIRED_ONE_XML,
            }
        )
        known_sequence_exceptions, unexpected_diagnostics = (
            self.check_public_files_with_known_sequence_exception(root_dir)
        )
        self.assertEqual(
            [KNOWN_PUBLIC_SEQUENCE_EXCEPTION],
            [
                Path(diagnostic.file_path).relative_to(root_dir).as_posix()
                for diagnostic in known_sequence_exceptions
            ],
        )
        self.assertEqual(
            [("ITYPE_SEQUENCE001", other_public_path)],
            [
                (
                    diagnostic.rule_id,
                    Path(diagnostic.file_path).relative_to(root_dir).as_posix(),
                )
                for diagnostic in unexpected_diagnostics
            ],
            f"{root_dir}: {unexpected_diagnostics}",
        )

    def test_no_012_later_top_level_itemtype_reports_itype_sequence001(
        self,
    ):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-17-later-itemtype-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_no_013_relationshiptype_nested_itemtype_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/RelationshipType/aml-12-relationshiptype-nested-itemtype-sequence-required-one.xml",
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

    def test_parent_itemtype_edit_sequence_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-16-sequence-required-one-parent-edit.xml",
            ["ITYPE_SEQUENCE001"],
        )

    def test_only_sequence_required_one_reports_itype_sequence001(self):
        self.assert_sample_reports_rules(
            "samples/bad/ItemType/aml-15-multiple-properties-sequence-required-one.xml",
            ["ITYPE_SEQUENCE001"],
        )


PUBLIC_PATH_SEQUENCE_REQUIRED_ONE_XML = """
<AML>
  <Item type="ItemType" id="11111111111111111111111111111111" action="add">
    <name>Public Custom Type</name>
    <Relationships>
      <Item type="Property" id="22222222222222222222222222222222" action="add">
        <name>item_number</name>
        <data_type>sequence</data_type>
        <is_required>1</is_required>
      </Item>
    </Relationships>
  </Item>
</AML>
""".strip()


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
