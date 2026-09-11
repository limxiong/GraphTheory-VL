---
pretty_name: GraphTheory-VL
language:
  - en
license: cc-by-4.0
task_categories:
  - visual-question-answering
tags:
  - mathematics
  - graph-theory
  - multimodal
  - benchmark
size_categories:
  - n<1K
---

# GraphTheory-VL

GraphTheory-VL contains 62 team-created visual mathematics questions connecting diagrams to exact graph-theoretic, algebraic and topological targets. Hard20 is a nested 20-question subset. Tasks include integer counts, tuples, finitely generated abelian groups and symbolic polynomials. The question texts and diagrams were created by the GraphTheory-VL research team.

## Composition and intended use

The 62 retained questions were selected from a 623-question source pool using model-screening results followed by reference examination and quality filtering. Challenge62 and Hard20 are evaluation subsets, not disjoint training and test splits. They are selected difficult instances rather than a random sample of all visual mathematics.

Use the collection to evaluate diagram interpretation, exact mathematical targets, repeated success and the effect of removing visual inputs. Reference answers and explanations are included for evaluation and inspection. The `difficulty` field preserves original metadata; the `hard` field identifies the actual Hard20 membership.

## Data and evaluation

The core download provides one JSONL table and local PNG files. See [SCHEMA.md](SCHEMA.md) for fields and [README.md](README.md) for loading instructions. Images are original bytes; question, accepted answer and explanation strings are preserved. The export replaces image-delivery URLs with local paths.

The recorded evaluation contains 984 unique scoring positions: 744 Original and 240 Text-only. The separate response archive provides 983 complete outputs and the explicit status of the one user-reported score without a complete local answer. Prompt text, recorded configurations and effective labels accompany the release.

Reference checking combines recorded model-assisted inspection and exact computation; full independent human validation is not supplied. Some selected failures recover on later attempts. Target agreement alone does not establish correct structural interpretation or a valid derivation. Text-only target scores require particular care because the diagram can specify information absent from the text.

GT-0560 retains the input wording used in the reported experiment, including its documented directional conflict. This release preserves the evaluated data and supplies the recorded results rather than silently rewriting that case.

## License and attribution

The 62 team-created questions, accompanying images and team-owned dataset documentation use [CC BY 4.0](licenses/LICENSE_DATA.md). Team-owned software uses [MIT](licenses/LICENSE_CODE.txt). Archived model-service outputs and other third-party materials retain their applicable terms. The original 623-question source-pool workbooks are outside the core download.

Attribution: **GraphTheory-VL research team, GraphTheory-VL v1.0**. [Homepage](https://limxiong.github.io/GraphTheory-VL/) · [Hugging Face dataset](https://huggingface.co/datasets/zixiong02/GraphTheory-VL) · [Release v1.0](https://github.com/limxiong/GraphTheory-VL/releases/tag/v1.0). Released September 11, 2026. The paper's arXiv identifier will be added when available.
