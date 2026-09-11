#!/usr/bin/env python3
"""Prepare predictions for review or summarize supplied four-roll labels offline.

No model calls or semantic judgments are made. An exact string match is a hint;
every prepared prediction remains Pending until a separate review supplies a label.
Python 3.9+ and the standard library are sufficient.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
VERDICTS = ("Correct", "Incorrect", "Pending", "Missing")
SCOREABLE = ("Correct", "Incorrect")
METRICS = ("acc_at_1", "mean_acc_4", "pass_at_4", "stable_at_4")


def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError("{}:{}: invalid JSON: {}".format(path, number, error.msg)) from error
            if not isinstance(row, dict):
                raise ValueError("{}:{}: expected a JSON object".format(path, number))
            rows.append(row)
    return rows


def load_dataset(root):
    """Load references and the two memberships from a package directory."""
    root = Path(root)
    questions = {}
    for row in read_jsonl(root / "data/questions.jsonl"):
        problem_id = row.get("problem_id")
        if not isinstance(problem_id, str) or not problem_id:
            raise ValueError("Dataset question has no problem_id")
        if problem_id in questions:
            raise ValueError("Duplicate dataset problem_id: " + problem_id)
        if not isinstance(row.get("answer"), str) or not row["answer"].strip():
            raise ValueError("Dataset question has no reference answer: " + problem_id)
        questions[problem_id] = row
    memberships = {}
    for name, filename in (("Challenge62", "challenge_ids.txt"), ("Hard20", "hard_ids.txt")):
        ids = [line.strip() for line in (root / "data" / filename).read_text(encoding="utf-8").splitlines()
               if line.strip()]
        if len(ids) != len(set(ids)) or not set(ids).issubset(questions):
            raise ValueError("Duplicate or unknown dataset IDs in " + filename)
        memberships[name] = ids
    if set(memberships["Challenge62"]) != set(questions):
        raise ValueError("Challenge membership does not match dataset questions")
    if not set(memberships["Hard20"]).issubset(memberships["Challenge62"]):
        raise ValueError("Hard membership is not contained in Challenge")
    return questions, memberships


def validate_identity(row, questions, hard_ids, seen):
    provider = row.get("provider")
    condition = row.get("condition")
    problem_id = row.get("problem_id")
    roll = row.get("roll")
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("provider must be a nonempty string")
    if condition not in ("original", "text_only"):
        raise ValueError("condition must be original or text_only")
    if not isinstance(problem_id, str) or problem_id not in questions:
        raise ValueError("Unknown problem_id: {!r}".format(problem_id))
    if type(roll) is not int or roll not in range(1, 5):
        raise ValueError("roll must be an integer from 1 to 4")
    if condition == "text_only" and problem_id not in hard_ids:
        raise ValueError("text_only accepts Hard20 questions only: " + problem_id)
    key = (provider, condition, problem_id, roll)
    if key in seen:
        raise ValueError("Duplicate prediction or label position: {!r}".format(key))
    seen.add(key)
    return key


def summarize_rows(rows, questions, memberships):
    """Calculate ratios on complete four-label questions and report coverage."""
    seen = set()
    hard_ids = set(memberships["Hard20"])
    by_group = {}
    for row in rows:
        provider, condition, problem_id, roll = validate_identity(row, questions, hard_ids, seen)
        verdict = row.get("verdict")
        if verdict not in VERDICTS:
            raise ValueError("verdict must be Correct, Incorrect, Pending or Missing")
        by_group.setdefault((provider, condition), {})[(problem_id, roll)] = verdict
    groups = []
    for (provider, condition), slots in sorted(by_group.items()):
        subsets = ("Challenge62", "Hard20") if condition == "original" else ("Hard20",)
        for subset in subsets:
            ids = memberships[subset]
            selected = {key: value for key, value in slots.items() if key[0] in ids}
            complete = [q for q in ids if all(selected.get((q, roll)) in SCOREABLE for roll in range(1, 5))]
            counts = [sum(selected[q, roll] == "Correct" for roll in range(1, 5)) for q in complete]
            n = len(complete)
            distribution = Counter(counts)
            verdict_counts = Counter(selected.values())
            metrics = {key: None for key in METRICS}
            if n:
                metrics = {
                    "acc_at_1": sum(selected[q, 1] == "Correct" for q in complete) / n,
                    "mean_acc_4": sum(counts) / (4 * n),
                    "pass_at_4": sum(count > 0 for count in counts) / n,
                    "stable_at_4": sum(count == 4 for count in counts) / n,
                }
            groups.append({
                "subset": subset, "provider": provider, "condition": condition,
                "planned_questions": len(ids), "complete_questions": n,
                "planned_positions": len(ids) * 4, "reported_positions": len(selected),
                "scoreable_positions": sum(value in SCOREABLE for value in selected.values()),
                "unreported_positions": len(ids) * 4 - len(selected),
                "verdict_counts": {value: verdict_counts[value] for value in VERDICTS},
                "four_roll_correct_distribution": {str(count): distribution[count] for count in range(5)},
                **metrics,
            })
    return {
        "unique_positions": len(rows),
        "scoreable_positions": sum(row["verdict"] in SCOREABLE for row in rows),
        "metric_scope": "questions with four Correct/Incorrect labels; Missing/Pending are not Incorrect",
        "groups": groups,
    }


def extract_answer(response):
    """Extract an Answer field, stopping before a separate Reasoning field."""
    match = re.search(r"^\s*answer\s*:\s*", response, flags=re.IGNORECASE | re.MULTILINE)
    text = response[match.end():] if match else response
    return re.split(r"^\s*reasoning\s*:", text, maxsplit=1,
                    flags=re.IGNORECASE | re.MULTILINE)[0].strip()


def normalize_exact(value):
    """Normalize formatting only; this does not establish target equivalence."""
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"^\s*answer\s*:\s*", "", value, flags=re.IGNORECASE).strip()
    wrappers = ((r"\(", r"\)"), (r"\[", r"\]"), ("$", "$"))
    changed = True
    while changed and value:
        changed = False
        for start, end in wrappers:
            if value.startswith(start) and value.endswith(end) and len(value) >= len(start) + len(end):
                value = value[len(start):-len(end)].strip()
                changed = True
                break
    return re.sub(r"\s+", " ", value).strip()


def prepare_rows(rows, questions, memberships):
    """Preserve predictions and add review fields; never generate a verdict."""
    seen = set()
    output = []
    hard_ids = set(memberships["Hard20"])
    for row in rows:
        provider, condition, problem_id, roll = validate_identity(row, questions, hard_ids, seen)
        response = row.get("response", "")
        answer = row.get("answer", "")
        if not isinstance(response, str) or not isinstance(answer, str):
            raise ValueError("response and answer must be strings when supplied")
        if not response.strip() and not answer.strip():
            raise ValueError("At least one of response or answer must be nonempty")
        answer = answer.strip() if answer.strip() else extract_answer(response)
        reference = questions[problem_id]["answer"]
        normalized = normalize_exact(answer)
        output.append({
            "provider": provider, "condition": condition, "problem_id": problem_id,
            "roll": roll, "response": response, "answer": answer,
            "reference_answer": reference,
            "exact_match": bool(normalized) and normalized == normalize_exact(reference),
            "verdict": "Pending", "judgment_method": "unreviewed",
        })
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    summarize = commands.add_parser("summarize", help="Aggregate already reviewed labels")
    summarize.add_argument("--root", type=Path, default=ROOT, help="Package root (default: this script's package)")
    summarize.add_argument("--labels", type=Path, help="JSONL labels (default: ROOT/results/labels.jsonl)")
    summarize.add_argument("--output", type=Path, help="Write JSON here; otherwise print JSON")
    prepare = commands.add_parser("prepare", help="Create Pending review records from new predictions")
    prepare.add_argument("--root", type=Path, default=ROOT, help="Package root (default: this script's package)")
    prepare.add_argument("--predictions", type=Path, required=True, help="Prediction JSONL")
    prepare.add_argument("--output", type=Path, required=True, help="Pending review JSONL to write")
    args = parser.parse_args(argv)
    try:
        questions, memberships = load_dataset(args.root)
        if args.command == "summarize":
            rows = read_jsonl(args.labels if args.labels is not None else args.root / "results/labels.jsonl")
            result = summarize_rows(rows, questions, memberships)
            text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        else:
            result = prepare_rows(read_jsonl(args.predictions), questions, memberships)
            text = "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in result)
        if args.output is None:
            print(text, end="")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
            print("Wrote {}".format(args.output))
    except (OSError, ValueError) as error:
        parser.exit(2, "error: {}\n".format(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
