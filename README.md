# GraphTheory-VL

**62 visual mathematics problems, with a nested 20-problem hard subset.** The questions connect diagrams to exact graph-theoretic, algebraic and topological targets. This package contains the current questions, original images, reference answers, prompts, recorded configurations, evaluation labels and offline tools.

**Authors:** Zixiong Yang, Kuo Zhou, Ruwei Pan, Jiaran Gao, Sihan Wu, Lu Zhang.  
Peking University. Dataset version: **v1.0**.

[中文使用指南](QUICKSTART_zh.md) · [Dataset card](DATASET_CARD.md) · [Data fields](SCHEMA.md) · [Evaluation guide](EVALUATION.md) · [Recorded results](results/RESULTS.md)

## Project website

The prepared [project homepage](docs/index.html) contains four real examples, recorded results, the PDF draft and citation. For local preview and future GitHub Pages setup, see [WEBSITE.md](WEBSITE.md). The intended GitHub and Hugging Face repositories are both `limxiong/GraphTheory-VL`; public links remain pending publication.

## Quick start

Clone or download this repository, open a terminal in its root directory, and use **Python 3.9 or newer**. No pip installation is needed. The following commands use only Python's standard library and make no network or model requests.

```sh
python3 examples/read_dataset.py --split hard --limit 2
python3 tools/verify_package.py
python3 tools/evaluate.py summarize --output results/local_summary.json
```

The first command shows two Hard20 inputs and their local image paths. The verifier checks the dataset and reproduces all four point estimates in the nine saved model/subset/input groups. The last command writes a machine-readable summary from the 984 released labels. The full dataset has 62 questions; Hard20 is included in those 62.

Scripts also work from a different current directory when invoked by their full or relative path. User-supplied input/output paths are resolved from the current directory; quote paths containing spaces.

## Repository contents

| File or directory | Contents |
| --- | --- |
| `data/questions.jsonl` | 62 question records with reference answers and explanations |
| `data/images/` | 62 original PNG files |
| `data/challenge_ids.txt`, `data/hard_ids.txt` | Explicit membership lists |
| `protocol/prompts/` | Exact system/user text for every question; local image paths |
| `protocol/configurations/` | 17 recorded configurations used by the archived responses |
| `protocol/configuration_index.json` | Response-position to configuration mapping |
| `results/labels.jsonl` | 984 current scoring positions |
| `results/paper_metrics.json` | Saved point estimates, confidence intervals and paired comparisons |
| `examples/`, `tools/`, `tests/` | Reading, prediction preparation, label aggregation and tests |
| `licenses/` | Data and team-owned code license notices |
| `docs/` | Static project homepage, sample images and draft paper |

Complete answer bodies and individual judgment/reference records are in the separate **GraphTheory-VL-v1.0-responses.zip**. This core package is sufficient for loading the dataset and reproducing the main point estimates. The response archive is self-contained and can be extracted separately.

## Evaluate a new model

To try the preparation step immediately, two existing archived responses are included as a format example:

```sh
python3 tools/evaluate.py prepare --predictions examples/predictions.sample.jsonl --output pending_judgments.jsonl
```

These are copied historical outputs, not a new model run. The resulting rows remain Pending.

Use the stored prompts and the supplied image for Original inputs; for Text-only inputs on Hard20, omit the image while preserving the prompt text. Give the solver only its question, options and intended image. Reference answers and explanations are evaluation materials.

Save your predictions as described in [EVALUATION.md](EVALUATION.md), then run:

```sh
python3 tools/evaluate.py prepare --predictions my_predictions.jsonl --output pending_judgments.jsonl
```

This adds the reference answer and an exact-string-match hint. Every row remains `Pending` until a human or semantic judge assigns `Correct` or `Incorrect`. After recording those judgments:

```sh
python3 tools/evaluate.py summarize --labels judged_predictions.jsonl --output my_metrics.json
```

## Scope and attribution

Challenge62 was selected from a 623-question source pool using screening outcomes and reference-quality decisions. Hard20 is a nested subset selected for further analysis. The original source-pool workbooks and excluded question collections are not in this download.

The current evaluation has 744 Original positions and 240 Text-only positions across three models, with four indexed responses per question. There are 983 complete archived responses and one user-reported Incorrect decision without the complete local response body. Mathematical references and behavioral annotations use the recorded model-assisted and computational checks; dataset-wide independent human validation has not been supplied. GT-0560 retains the evaluated wording; its documented directional conflict is not silently corrected in this version.

The 62 question texts and images were created by the GraphTheory-VL research team. See [CC BY 4.0 data notice](licenses/LICENSE_DATA.md) and [MIT code license](licenses/LICENSE_CODE.txt). Archived third-party service outputs and dependencies retain their applicable terms.

## Citation

Use the author and dataset metadata in [CITATION.cff](CITATION.cff) to cite **GraphTheory-VL, version 1.0**. The author order follows the manuscript. A paper identifier, permanent resource links and release date will be added when available.

## Development checks

```sh
python3 -m unittest discover -s tests -v
python3 tools/verify_package.py
```

The [offline validation workflow](.github/workflows/offline-validation.yml) runs these checks on Python 3.9 and 3.13. The tests and data verification use the standard library and make no model or network requests.
