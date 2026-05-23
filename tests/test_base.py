from pathlib import Path
import tempfile
import unittest

from aml_harness.base import Diagnostic, check_file


class BaseAmlCheckTests(unittest.TestCase):
    def check_text(self, text: str) -> list[Diagnostic]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.xml"
            path.write_text(text, encoding="utf-8")
            return check_file(path)

    def assert_has_rule(self, diagnostics: list[Diagnostic], rule_id: str):
        self.assertTrue(
            any(d.rule_id == rule_id for d in diagnostics),
            f"Expected {rule_id}, got {[d.rule_id for d in diagnostics]}",
        )

    def test_valid_base_aml(self):
        diagnostics = self.check_text(
            """
<AML>
  <Item type="ItemType" action="add" id="1234567890ABCDEF1234567890ABCDEF" />
</AML>
""".strip()
        )

        self.assertEqual([], diagnostics)

    def test_root_must_be_aml(self):
        diagnostics = self.check_text(
            """
<Package>
  <Item type="ItemType" action="add" id="1234567890ABCDEF1234567890ABCDEF" />
</Package>
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML001")

    def test_aml_must_contain_item(self):
        diagnostics = self.check_text("<AML></AML>")

        self.assert_has_rule(diagnostics, "AML002")

    def test_aml_child_must_be_item(self):
        diagnostics = self.check_text(
            """
<AML>
  <Foo />
</AML>
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML003")

    def test_item_must_have_type(self):
        diagnostics = self.check_text(
            """
<AML>
  <Item action="add" id="1234567890ABCDEF1234567890ABCDEF" />
</AML>
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML004")

    def test_item_must_have_action(self):
        diagnostics = self.check_text(
            """
<AML>
  <Item type="ItemType" id="1234567890ABCDEF1234567890ABCDEF" />
</AML>
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML005")

    def test_item_action_must_be_add_or_edit(self):
        diagnostics = self.check_text(
            """
<AML>
  <Item type="ItemType" action="merge" id="1234567890ABCDEF1234567890ABCDEF" />
</AML>
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML005")

    def test_item_must_have_id(self):
        diagnostics = self.check_text(
            """
<AML>
  <Item type="ItemType" action="add" />
</AML>
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML006")

    def test_invalid_xml_is_reported(self):
        diagnostics = self.check_text(
            """
<AML>
  <Item type="ItemType" action="add" id="123" />
""".strip()
        )

        self.assert_has_rule(diagnostics, "AML000")

    def test_missing_file_is_reported(self):
        diagnostics = check_file(Path("this-file-does-not-exist.xml"))

        self.assert_has_rule(diagnostics, "FILE001")


if __name__ == "__main__":
    unittest.main()
