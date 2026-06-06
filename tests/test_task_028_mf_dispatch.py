from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aml_harness.base import Diagnostic, check_file
from aml_harness.cli import main


ROOT_DIR = Path(__file__).resolve().parents[1]
PUBLIC_SINGLE_IMPORTS = "public/imports_単数版.mf"
PUBLIC_MULTIPLE_IMPORTS = "public/imports_複数版.mf"
IMPORTS_RULE_IDS = {
    "IMPORTS001",
    "IMPORTS002",
    "IMPORTS003",
    "IMPORTS004",
    "IMPORTS005",
    "IMPORTS006",
    "IMPORTS007",
}


class Task028MfDispatchTests(unittest.TestCase):
    """AML-01 through AML-15 map to test-cases.md."""

    def check_temp_file(self, filename: str, text: str) -> list[Diagnostic]:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / filename
            path.write_text(text.strip(), encoding="utf-8")
            return check_file(path)

    def check_sample(self, relative_path: str) -> list[Diagnostic]:
        return check_file(ROOT_DIR / relative_path)

    def rule_ids(self, diagnostics: list[Diagnostic]) -> list[str]:
        return [diagnostic.rule_id for diagnostic in diagnostics]

    def assert_rule_ids(self, diagnostics: list[Diagnostic], expected_rule_ids: list[str]):
        self.assertEqual(expected_rule_ids, self.rule_ids(diagnostics), diagnostics)

    def assert_no_aml001_or_imports_rules(self, diagnostics: list[Diagnostic]):
        actual_rule_ids = set(self.rule_ids(diagnostics))
        self.assertNotIn("AML001", actual_rule_ids, diagnostics)
        self.assertEqual(set(), actual_rule_ids & IMPORTS_RULE_IDS, diagnostics)

    def run_cli(self, args: list[str]) -> tuple[int, str]:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(args)
        return exit_code, stdout.getvalue()

    def test_no_001_imports_mf_is_checked_as_imports_manifest(self):
        diagnostics = self.check_temp_file(
            "imports.mf",
            """
<imports>
  <package name="com.aras.innovator.synthetic" path='.\\' />
</imports>
""",
        )

        self.assertEqual([], diagnostics)
        self.assert_no_aml001_or_imports_rules(diagnostics)

    def test_no_002_custom_named_mf_is_checked_as_imports_manifest(self):
        diagnostics = self.check_temp_file(
            "custom_imports.mf",
            """
<imports>
  <package name="com.aras.innovator.synthetic" path='.\\' />
</imports>
""",
        )

        self.assertEqual([], diagnostics)
        self.assert_no_aml001_or_imports_rules(diagnostics)

    def test_no_003_custom_named_mf_with_multiple_packages_passes(self):
        diagnostics = self.check_temp_file(
            "multiple_packages.mf",
            """
<imports>
  <package name="com.aras.innovator.admin" path='.\\' />
  <package name="com.aras.innovator.dashboard" path='.\\'>
    <dependson name="com.aras.innovator.i18n" />
  </package>
  <package name="com.aras.innovator.core" path='.\\'>
    <dependson name="com.aras.innovator.admin" />
  </package>
</imports>
""",
        )

        self.assertEqual([], diagnostics)
        self.assertNotIn("AML001", self.rule_ids(diagnostics), diagnostics)

    def test_no_004_mf_with_aml_root_reports_imports001(self):
        diagnostics = self.check_temp_file(
            "aml_root.mf",
            """
<AML>
  <Item type="Method" id="11111111111111111111111111111111" action="add">
    <name>SampleMethod</name>
  </Item>
</AML>
""",
        )

        self.assert_rule_ids(diagnostics, ["IMPORTS001"])

    def test_no_005_mf_with_non_imports_root_reports_imports001(self):
        diagnostics = self.check_temp_file(
            "manifest_root.mf",
            """
<manifest>
  <package name="com.aras.innovator.solution.PLM" path="PLM\\Import" />
</manifest>
""",
        )

        self.assert_rule_ids(diagnostics, ["IMPORTS001"])

    def test_no_006_mf_parse_error_reports_aml000(self):
        diagnostics = self.check_temp_file(
            "invalid_xml.mf",
            """
<imports>
  <package name="com.aras.innovator.solution.PLM" path="PLM\\Import">
</imports>
""",
        )

        self.assert_rule_ids(diagnostics, ["AML000"])

    def test_no_007_xml_with_imports_root_reports_aml001(self):
        diagnostics = self.check_temp_file(
            "imports_root.xml",
            """
<imports>
  <package name="com.aras.innovator.solution.PLM" path="PLM\\Import" />
</imports>
""",
        )

        self.assert_rule_ids(diagnostics, ["AML001"])

    def test_no_008_xml_with_aml_root_passes(self):
        diagnostics = self.check_temp_file(
            "valid_aml.xml",
            """
<AML>
  <Item type="Method" id="11111111111111111111111111111111" action="add" />
</AML>
""",
        )

        self.assertEqual([], diagnostics)

    def test_no_009_mf_without_package_reports_imports002(self):
        diagnostics = self.check_temp_file("no_package.mf", "<imports />")

        self.assert_rule_ids(diagnostics, ["IMPORTS002"])

    def test_no_010_mf_package_without_name_reports_imports004(self):
        diagnostics = self.check_temp_file(
            "package_without_name.mf",
            """
<imports>
  <package path='.\\' />
</imports>
""",
        )

        self.assert_rule_ids(diagnostics, ["IMPORTS004"])
        self.assertNotIn("AML001", self.rule_ids(diagnostics), diagnostics)

    def test_no_011_mf_package_without_path_reports_imports005(self):
        diagnostics = self.check_temp_file(
            "package_without_path.mf",
            """
<imports>
  <package name="com.aras.innovator.solution.PLM" />
</imports>
""",
        )

        self.assert_rule_ids(diagnostics, ["IMPORTS005"])
        self.assertNotIn("AML001", self.rule_ids(diagnostics), diagnostics)

    def test_no_012_mixed_all_files_glob_passes_without_mf_aml001(self):
        exit_code, output = self.run_cli(["./public/**/*.*"])

        self.assertEqual(0, exit_code, output)
        self.assertNotIn(f"{PUBLIC_SINGLE_IMPORTS}:1:1 error AML001", output)
        self.assertNotIn(f"{PUBLIC_MULTIPLE_IMPORTS}:1:1 error AML001", output)

    def test_no_013_xml_only_glob_passes(self):
        exit_code, output = self.run_cli(["./public/**/*.xml"])

        self.assertEqual(0, exit_code, output)

    def test_no_014_public_single_imports_manifest_passes(self):
        diagnostics = self.check_sample(PUBLIC_SINGLE_IMPORTS)

        self.assertEqual([], diagnostics)
        self.assertNotIn("AML001", self.rule_ids(diagnostics), diagnostics)

    def test_no_015_public_multiple_imports_manifest_passes(self):
        diagnostics = self.check_sample(PUBLIC_MULTIPLE_IMPORTS)

        self.assertEqual([], diagnostics)
        self.assertNotIn("AML001", self.rule_ids(diagnostics), diagnostics)


if __name__ == "__main__":
    unittest.main()
