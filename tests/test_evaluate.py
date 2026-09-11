"""Behavior checks for the public, standard-library-only evaluation tools."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parents[1]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def labels(question, verdicts, provider="model-a", condition="original"):
    return [dict(provider=provider, condition=condition, problem_id=question,
                 roll=roll, verdict=verdict)
            for roll, verdict in enumerate(verdicts, 1)]


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        entry = PACKAGE / "tools/evaluate.py"
        self.assertTrue(entry.is_file(), "Public evaluation entrypoint has not been implemented")
        spec = importlib.util.spec_from_file_location("release_evaluate", entry)
        self.tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.tool)
        self.temp = tempfile.TemporaryDirectory(prefix="graph tools ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "sample package"
        self.outside = Path(self.temp.name) / "outside"
        self.outside.mkdir()
        rows = [dict(problem_id="GT-0001", question="First?", answer="42",
                     explanation="Private reference reasoning", image_path="data/images/GT-0001.png", hard=True),
                dict(problem_id="GT-0002", question="Second?", answer="7",
                     explanation="Second reference", image_path="data/images/GT-0002.png", hard=True),
                dict(problem_id="GT-0003", question="Third?", answer="9",
                     explanation="Third reference", image_path="data/images/GT-0003.png", hard=False)]
        write_jsonl(self.root / "data/questions.jsonl", rows)
        (self.root / "data/challenge_ids.txt").write_text("GT-0001\nGT-0002\nGT-0003\n", encoding="utf-8")
        (self.root / "data/hard_ids.txt").write_text("GT-0001\nGT-0002\n", encoding="utf-8")
        self.questions, self.memberships = self.tool.load_dataset(self.root)

    def summarize(self, rows):
        return self.tool.summarize_rows(rows, self.questions, self.memberships)

    def group(self, summary, subset="Challenge62", provider="model-a", condition="original"):
        return next(g for g in summary["groups"]
                    if (g["subset"], g["provider"], g["condition"]) == (subset, provider, condition))

    def test_four_roll_metrics_and_first_response_have_distinct_meanings(self):
        rows = labels("GT-0001", ["Incorrect", "Correct", "Correct", "Incorrect"])
        rows += labels("GT-0002", ["Correct"] * 4)
        rows += labels("GT-0003", ["Incorrect"] * 4)
        result = self.summarize(rows)
        group = self.group(result)
        self.assertEqual(group["acc_at_1"], 1 / 3)
        self.assertEqual(group["mean_acc_4"], 1 / 2)
        self.assertEqual(group["pass_at_4"], 2 / 3)
        self.assertEqual(group["stable_at_4"], 1 / 3)
        self.assertEqual(group["four_roll_correct_distribution"], {"0": 1, "1": 0, "2": 1, "3": 0, "4": 1})
        self.assertEqual(result["unique_positions"], 12)
        self.assertEqual(self.group(result, "Hard20")["reported_positions"], 8)

    def test_missing_and_pending_are_coverage_not_incorrect_labels(self):
        rows = labels("GT-0001", ["Correct"] * 4)
        rows += labels("GT-0002", ["Correct", "Incorrect", "Pending", "Missing"])
        rows += labels("GT-0003", ["Correct"])
        group = self.group(self.summarize(rows))
        self.assertEqual((group["planned_questions"], group["complete_questions"]), (3, 1))
        self.assertEqual((group["planned_positions"], group["reported_positions"], group["scoreable_positions"]), (12, 9, 7))
        self.assertEqual(group["unreported_positions"], 3)
        self.assertEqual(group["verdict_counts"]["Pending"], 1)
        self.assertEqual(group["verdict_counts"]["Missing"], 1)
        self.assertEqual(group["mean_acc_4"], 1.0)

    def test_no_complete_question_has_null_metrics(self):
        group = self.group(self.summarize(labels("GT-0001", ["Correct", "Pending"])))
        self.assertEqual(group["complete_questions"], 0)
        for metric in ("acc_at_1", "mean_acc_4", "pass_at_4", "stable_at_4"):
            self.assertIsNone(group[metric])
        self.assertEqual(sum(group["four_roll_correct_distribution"].values()), 0)

    def test_models_and_input_conditions_stay_separate(self):
        rows = labels("GT-0001", ["Correct"] * 4)
        rows += labels("GT-0001", ["Incorrect"] * 4, provider="model-b")
        rows += labels("GT-0001", ["Incorrect"] * 4, condition="text_only")
        result = self.summarize(rows)
        self.assertEqual(len(result["groups"]), 5)
        self.assertEqual(self.group(result)["mean_acc_4"], 1)
        self.assertEqual(self.group(result, provider="model-b")["mean_acc_4"], 0)
        self.assertEqual(self.group(result, "Hard20", condition="text_only")["mean_acc_4"], 0)
        self.assertEqual(result["unique_positions"], 12)

    def test_duplicate_or_invalid_labels_fail_explicitly(self):
        valid = labels("GT-0001", ["Correct"])[0]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.summarize([valid, dict(valid)])
        invalid = [dict(valid, problem_id="GT-9999"), dict(valid, roll=0),
                   dict(valid, roll=5), dict(valid, roll=True), dict(valid, roll="1"),
                   dict(valid, condition="caption"), dict(valid, provider=""),
                   dict(valid, verdict="JudgeError"),
                   dict(valid, condition="text_only", problem_id="GT-0003")]
        for row in invalid:
            with self.subTest(row=row), self.assertRaises(ValueError):
                self.summarize([row])

    def test_prepare_match_is_only_a_hint_and_retains_full_response(self):
        response = "Answer: $42$\nReasoning: This complete reasoning must be preserved."
        rows = [dict(provider="new-model", condition="original", problem_id="GT-0001",
                     roll=1, response=response)]
        output = self.tool.prepare_rows(rows, self.questions, self.memberships)
        self.assertEqual(output[0]["answer"], "$42$")
        self.assertEqual(output[0]["response"], response)
        self.assertEqual(output[0]["reference_answer"], "42")
        self.assertTrue(output[0]["exact_match"])
        self.assertEqual(output[0]["verdict"], "Pending")
        self.assertEqual(output[0]["judgment_method"], "unreviewed")

    def test_prepare_nonmatch_and_proof_task_remain_pending(self):
        self.questions["GT-0001"]["question"] = "Prove the answer is 42."
        rows = [dict(provider="new-model", condition="original", problem_id="GT-0001",
                     roll=1, answer="42"),
                dict(provider="new-model", condition="original", problem_id="GT-0002",
                     roll=1, response="answer: 8\nreasoning: incomplete")]
        output = self.tool.prepare_rows(rows, self.questions, self.memberships)
        self.assertEqual([r["exact_match"] for r in output], [True, False])
        self.assertEqual([r["verdict"] for r in output], ["Pending", "Pending"])
        self.assertEqual(output[0]["response"], "")

    def test_prepare_nfkc_normalizes_fullwidth_digits_and_math_wrappers(self):
        for answer in ("＄４２＄", r"\(４２\)", "ａｎｓｗｅｒ：　＄４２＄"):
            with self.subTest(answer=answer):
                row = dict(provider="new-model", condition="original", problem_id="GT-0001",
                           roll=1, answer=answer, response="Preserved response", verdict="Correct")
                output = self.tool.prepare_rows([row], self.questions, self.memberships)[0]
                self.assertTrue(output["exact_match"])
                self.assertEqual(output["answer"], answer)
                self.assertEqual(output["response"], "Preserved response")
                self.assertEqual(output["verdict"], "Pending")
                self.assertEqual(output["judgment_method"], "unreviewed")

    def test_prepare_rejects_missing_text_duplicates_and_illegal_text_condition(self):
        row = dict(provider="new-model", condition="original", problem_id="GT-0001", roll=1, answer="42")
        invalid = [dict(row, answer=""), dict(row, answer=42),
                   dict(row, problem_id="GT-0003", condition="text_only")]
        for record in invalid:
            with self.subTest(record=record), self.assertRaises(ValueError):
                self.tool.prepare_rows([record], self.questions, self.memberships)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.tool.prepare_rows([row, row], self.questions, self.memberships)

    def install_entrypoints(self):
        for relative in ("tools/evaluate.py", "examples/read_dataset.py"):
            source = PACKAGE / relative
            self.assertTrue(source.is_file(), "Public dataset reader has not been implemented")
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(self.root / script), *map(str, args)],
                              cwd=self.outside, capture_output=True, text=True)

    def test_cli_uses_script_root_and_caller_output_directory(self):
        self.install_entrypoints()
        write_jsonl(self.root / "results/labels.jsonl", labels("GT-0001", ["Correct"] * 4))
        result = self.run_cli("tools/evaluate.py", "summarize", "--output", "summary.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.outside / "summary.json").is_file())
        summary = json.loads((self.outside / "summary.json").read_text())
        self.assertEqual(summary["unique_positions"], 4)
        prediction = dict(provider="new", condition="original", problem_id="GT-0001", roll=1, answer="42")
        write_jsonl(self.outside / "predictions.jsonl", [prediction])
        result = self.run_cli("tools/evaluate.py", "prepare", "--root", self.root,
                              "--predictions", "predictions.jsonl", "--output", "pending.jsonl")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.outside / "pending.jsonl").read_text())["verdict"], "Pending")

    def test_reader_hard_split_omits_reference_answers(self):
        self.install_entrypoints()
        result = self.run_cli("examples/read_dataset.py", "--split", "hard", "--limit", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)
        self.assertEqual(row["problem_id"], "GT-0001")
        self.assertTrue(row["hard"])
        self.assertNotIn("answer", row)
        self.assertNotIn("explanation", row)
        self.assertNotIn("Private reference reasoning", result.stdout)


if __name__ == "__main__":
    unittest.main()
