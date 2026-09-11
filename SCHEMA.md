# Data schema

Text files use UTF-8. Each nonempty line of a JSONL file is one JSON object. The question text, reference answer and explanation retain their original strings, including TeX notation. All active image paths are relative to this package's root.

## Questions: `data/questions.jsonl`

| Field | Type | Meaning |
| --- | --- | --- |
| `problem_id` | string | Stable identifier such as `GT-0004` |
| `question` | string | Exact evaluated problem text |
| `image_path` | string | Local PNG path, such as `data/images/GT-0004.png` |
| `options` | string or null | Original answer options, when present |
| `answer` | string | Current accepted target answer |
| `explanation` | string | Current reference explanation |
| `category` | string | Original broad subject label |
| `subcategory` | string | Original narrower subject label |
| `difficulty` | string | Original metadata label; not the Hard20 membership rule |
| `hard` | boolean | Whether this question is in Hard20 |

All 62 rows belong to Challenge62, including the 20 rows with `hard=true`. There are no train/validation/test partitions implied by these two nested subsets. The historical image-delivery URL is omitted from this portable export.

## Released labels: `results/labels.jsonl`

The unique identity is `(provider, condition, problem_id, roll)`.

| Field | Meaning |
| --- | --- |
| `provider` | Archived model-family key: `gpt`, `gemini` or `claude` |
| `condition` | `original` or `text_only` |
| `problem_id` | A current question ID |
| `roll` | Integer 1–4 |
| `verdict` | Recorded `Correct` or `Incorrect` |
| `audit_id` | Stable joined identity, matching the response archive |
| `complete_answer_available` | Whether a complete response body is archived |
| `label_kind` | Source category for the effective label |

There are 984 rows. `claude::text_only::GT-0560::2` is the sole row with no complete archived response body; its explicit user-reported Incorrect decision remains in the released scores.

## Prompts and configurations

`protocol/prompts/{problem_id}.json` stores `system` and `user` exactly as used in the recorded runs. `conditions.original.image_path` points to the local image and `conditions.text_only.image_path` is null. Although the common template describes both conditions, the reported Text-only experiment covers Hard20 only.

`protocol/configuration_index.json` maps each archived scoring position to a file in `protocol/configurations/`. Configuration files are historical request settings and recovery-stage records. Their `source_locator` and line fields describe the original archive; they are not additional required local files. Endpoint addresses record where the historical requests ran, rather than a promise of present-day service availability.

## Saved results

`results/paper_metrics.json` retains the nine current groups and their saved confidence intervals, plus paired comparisons and method descriptions. `results/expected_basic_metrics.json` contains a separate saved basic-metric reference used during package checks. `results/RESULTS.md` is a readable rendering of the saved main point estimates.
