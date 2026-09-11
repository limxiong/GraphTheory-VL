#!/usr/bin/env python3
"""Read question examples without printing reference answers or explanations."""

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from evaluate import load_dataset


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Package root (default: this script's package)")
    parser.add_argument("--split", choices=("challenge", "hard"), default="challenge")
    parser.add_argument("--limit", type=int, default=2, help="Maximum number of JSONL examples (default: 2)")
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    try:
        questions, memberships = load_dataset(args.root)
        subset = "Hard20" if args.split == "hard" else "Challenge62"
        hard_ids = set(memberships["Hard20"])
        for problem_id in memberships[subset][:args.limit]:
            source = questions[problem_id]
            row = {"problem_id": problem_id, "question": source["question"],
                   "image_path": str((args.root / source["image_path"]).resolve()),
                   "hard": problem_id in hard_ids}
            if source.get("options"):
                row["options"] = source["options"]
            print(json.dumps(row, ensure_ascii=False))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, "error: {}\n".format(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
