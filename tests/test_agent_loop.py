from pathlib import Path
import tempfile
import unittest

from harness.agent_loop import build_repair_prompt
from harness.records import IterationRecord, get_next_iteration, save_record
from harness.shell import CommandResult
from harness.validators import ValidationReport


class AgentLoopTests(unittest.TestCase):
    def test_build_repair_prompt_contains_failure_context(self):
        prompt = build_repair_prompt(
            task="Fix the AML checker.",
            iteration=2,
            validation_summary="python -m unittest failed.",
            stdout="test output",
            stderr="traceback output",
        )

        self.assertIn("Fix the AML checker.", prompt)
        self.assertIn("Iteration", prompt)
        self.assertIn("2", prompt)
        self.assertIn("python -m unittest failed.", prompt)
        self.assertIn("traceback output", prompt)
        self.assertIn("python -m aml_harness .\\samples\\good\\base.xml", prompt)

    def test_records_use_next_iteration_directory(self):
        validation = ValidationReport(
            passed=True,
            results=[
                CommandResult(
                    command=["python", "-m", "unittest"],
                    exit_code=0,
                    stdout="",
                    stderr="",
                    duration_ms=1,
                    timed_out=False,
                )
            ],
            summary="ok",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            import harness.records as records

            original_runs_dir = records.RUNS_DIR
            records.RUNS_DIR = Path(temp_dir) / "runs"

            try:
                self.assertEqual(1, get_next_iteration())
                record_path, prompt_path = save_record(
                    IterationRecord(
                        iteration=1,
                        task_path="tasks/task-001.md",
                        validation=validation,
                        created_at="2026-05-24T00:00:00+00:00",
                    )
                )

                self.assertTrue(record_path.exists())
                self.assertIsNone(prompt_path)
                self.assertEqual(2, get_next_iteration())
            finally:
                records.RUNS_DIR = original_runs_dir


if __name__ == "__main__":
    unittest.main()
