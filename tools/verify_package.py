#!/usr/bin/env python3
"""Check local release data and reproduce the recorded point estimates."""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify(root):
    questions = read_jsonl(root / "data/questions.jsonl")
    ids = {row["problem_id"] for row in questions}
    hard = {row["problem_id"] for row in questions if row["hard"]}
    require(len(questions) == len(ids) == 62, "Expected 62 unique questions")
    require(len(hard) == 20 and hard <= ids, "Expected nested Hard20 membership")
    for name, expected in [("challenge_ids.txt", ids), ("hard_ids.txt", hard)]:
        listed = (root / "data" / name).read_text(encoding="utf-8").split()
        require(len(listed) == len(expected) and set(listed) == expected, "Membership mismatch: " + name)
    for question in questions:
        pid = question["problem_id"]
        require(bool(question["question"]) and bool(question["answer"]), "Empty question/target: " + pid)
        image_path = question["image_path"]
        require(image_path == "data/images/" + pid + ".png", "Unexpected image path: " + pid)
        image = root / image_path
        require(image.is_file(), "Missing image: " + pid)
        with image.open("rb") as handle:
            require(handle.read(8) == b"\x89PNG\r\n\x1a\n", "Invalid PNG signature: " + pid)
        prompt = json.loads((root / "protocol/prompts" / (pid + ".json")).read_text(encoding="utf-8"))
        require(prompt["conditions"]["original"]["image_path"] == image_path, "Prompt image mismatch: " + pid)
        require(prompt["conditions"]["text_only"]["image_path"] is None, "Text-only image must be absent: " + pid)
        digest = hashlib.sha256((prompt["system"] + "\n" + prompt["user"]).encode()).hexdigest()
        require(digest == prompt["prompt_sha256"], "Recorded prompt text mismatch: " + pid)

    labels = read_jsonl(root / "results/labels.jsonl")
    keys = {(r["provider"], r["condition"], r["problem_id"], r["roll"]) for r in labels}
    expected_keys = {(provider, condition, pid, roll)
                     for provider in ("gpt", "gemini", "claude")
                     for condition, members in [("original", ids), ("text_only", hard)]
                     for pid in members for roll in range(1, 5)}
    require(len(labels) == 984 and keys == expected_keys, "Current scoring grid must contain 984 unique positions")
    require(Counter(r["verdict"] for r in labels) == {"Correct": 181, "Incorrect": 803}, "Released verdict totals differ")
    unavailable = [r["audit_id"] for r in labels if not r["complete_answer_available"]]
    require(unavailable == ["claude::text_only::GT-0560::2"], "Unexpected missing-body status")
    config_index = json.loads((root / "protocol/configuration_index.json").read_text(encoding="utf-8"))
    require(len(config_index) == 984, "Configuration index must cover all positions")
    require({r["audit_id"] for r in config_index} == {r["audit_id"] for r in labels}, "Configuration index identity mismatch")
    for record in config_index:
        require(record["configuration_path"] and (root / record["configuration_path"]).is_file(), "Missing recorded configuration")

    command = [sys.executable, str(root / "tools/evaluate.py"), "summarize", "--root", str(root), "--labels", str(root / "results/labels.jsonl")]
    run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    require(run.returncode == 0, "Metric reconstruction failed: " + run.stderr.strip())
    rebuilt = json.loads(run.stdout)
    group_key = lambda group: (group["subset"], group["provider"], group["condition"])
    actual = {group_key(group): group for group in rebuilt["groups"]}
    saved = json.loads((root / "results/paper_metrics.json").read_text(encoding="utf-8"))["groups"]
    require(len(actual) == len(saved) == 9, "Expected nine model/subset/input groups")
    for group in saved:
        result = actual[group_key(group)]
        require(result["complete_questions"] == group["questions"], "Question coverage differs from saved results")
        for metric in ["acc_at_1", "mean_acc_4", "pass_at_4", "stable_at_4"]:
            require(math.isclose(result[metric], group[metric], abs_tol=1e-12), "Metric mismatch: " + repr((group_key(group), metric)))
    basic = json.loads((root / "results/expected_basic_metrics.json").read_text(encoding="utf-8"))
    require(len(basic) == 9, "Expected nine independent saved basic groups")
    for group in basic:
        result = actual[group_key(group)]
        for old, new in [("MeanAcc", "mean_acc_4"), ("Pass@4", "pass_at_4"), ("Stable@4", "stable_at_4")]:
            require(math.isclose(result[new], group[old], abs_tol=1e-12), "Basic metric mismatch")
    return {"status": "PASS", "questions": 62, "hard_questions": 20, "images": 62,
            "scored_positions": 984, "complete_answer_markers": 983,
            "user_label_without_complete_answer": 1, "matched_metric_groups": 9,
            "metrics_checked": ["Acc@1", "MeanAcc", "Pass@4", "Stable@4"], "model_api_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = verify(args.root.resolve())
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, "Package verification failed: " + str(error) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
