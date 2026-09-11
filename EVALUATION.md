# Evaluation workflow

## Inputs and four responses

Use `protocol/prompts/{problem_id}.json` for the exact system/user text. Original inputs pair this text with the image; Text-only inputs omit the image without rewriting the text. The reported setup evaluates three model families four times on Challenge62 Original and four times on Hard20 Text-only. Hard20 Original is a subset of Challenge62 Original.

Keep the model's complete output and its extracted final answer. Save one JSON object per prediction:

```json
{"provider":"my-model","condition":"original","problem_id":"GT-0004","roll":1,"response":"answer: <the model's final answer>\nreasoning: <the model's explanation>"}
```

This is a format illustration, not a scored model response. Replace the content with your actual output. An explicit `answer` field may also be supplied. Valid rolls are integers 1–4. Text-only rows must use Hard20 IDs for this protocol.

## Prepare judgments

```sh
python3 tools/evaluate.py prepare --predictions my_predictions.jsonl --output pending_judgments.jsonl
```

Each prepared row retains the model identity and response, adds `answer`, `reference_answer`, `exact_match`, `verdict="Pending"` and `judgment_method="unreviewed"`.

`exact_match` uses the conservative text normalization from the existing experiment helpers: Unicode normalization, removal of an answer prefix or surrounding math delimiters, and whitespace normalization. This is a comparison hint. It neither proves mathematical equivalence nor checks the reasoning. An unequal string can still represent the correct answer.

A human or a separately run semantic judge should inspect the target, the model answer and relevant explanation, set `verdict` to `Correct` or `Incorrect`, and record `judgment_method` and an optional `rationale`. Save the reviewed rows as `judged_predictions.jsonl`. The tool does not call an online judge or fabricate judgments. The original paper's saved labels came from the documented model judgments, reference overlays, deterministic matching and one user-reported decision; those effective labels are preserved in `results/labels.jsonl`.

## Aggregate labels

```sh
python3 tools/evaluate.py summarize --labels judged_predictions.jsonl --output my_metrics.json
```

Without `--labels`, the command uses the released labels. Without `--output`, it prints JSON to standard output. An explicit package root can be passed after the subcommand using `--root`.

The output contains a `groups` array. Each group identifies its subset, provider and input condition, and reports planned questions/positions, reported positions, scoreable positions and complete questions. A question contributes to the metrics only when all four rolls have a `Correct` or `Incorrect` verdict. Pending or missing positions remain visible in coverage counts. If no question is complete, the metrics are null. Compare models on matched question populations when coverage differs.

| Output key | Display name | Definition on complete questions |
| --- | --- | --- |
| `acc_at_1` | Acc@1 | Fraction correct on roll 1 |
| `mean_acc_4` | MeanAcc | Correct positions divided by four times the number of questions |
| `pass_at_4` | Pass@4 | Fraction with at least one correct response among four |
| `stable_at_4` | Stable@4 | Fraction correct in all four responses |

All values are proportions from 0 to 1. `four_roll_correct_distribution` reports how many complete questions have 0, 1, 2, 3 or 4 correct responses. The summary's total position count counts each input row once; it does not add Hard20 Original again after Challenge62 Original.

The offline summarizer computes these four point estimates. Saved paper intervals and paired comparisons are supplied in `results/paper_metrics.json`; the quick-start summarizer does not recompute those intervals or independently rejudge the archived answers.
