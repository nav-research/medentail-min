# data/

This folder contains the derived data referenced from the [docs](../docs/00_index.md), specifically [Qualitative examples](../docs/08_qualitative_examples.md). These are **derived outputs** (model predictions and per-row MedEntail scores) from the paper's experiments — not raw corpus data. Source text for PLOS and eLife rows is reproduced under their CC-BY license; no raw Cochrane source text is included anywhere in this repository.

## `worst_case_examples_AB.csv`

The worst-scoring and best-scoring prediction (by `ME_chunk_row` or `ME_min_row`) for every zero-shot, in-domain, cross-domain, self-training, and parameter-merging configuration reported in the paper, on both PLOS and eLife. 40 rows total: 20 configurations × {worst, best}.

| Configurations | PLOS | eLife |
|---|---:|---:|
| ZS (5 models) | 5 | 5 |
| In-domain | 1 | 1 |
| Cross-domain | 1 | 1 |
| Self-training | 1 | 1 |
| Param-merging (2 variants each) | 2 | 2 |

**Columns**

| Column | Meaning |
|---|---|
| `category` | Adaptation stage: `ZS`, `In-domain`, `Cross-domain`, `Self-training`, `Param-merging` |
| `system` | Model or configuration name within the category |
| `target_corpus` | `PLOS` or `eLife` |
| `example_type` | `worst` (lowest score) or `best` (highest score) for that configuration |
| `source_file` | Original prediction file this row was drawn from |
| `source` | Truncated source text (~907 tokens) |
| `metric_source` | Full source article (~10,377 tokens) — this is what MedEntail actually scores against, not `source` |
| `target` / `reference` | Human reference simplification |
| `prediction` | The model's generated simplification |
| `ME_chunk_row` | Per-row MedEntail worst-case score, chunk premise variant (used for ZS / In-domain / Cross-domain / Param-merging) |
| `ME_min_row`, `ME_mean_row` | Per-row worst-case / average score for Self-training rows (computed the same way, different column name — see the [Method A notebook](../docs/01_medentail_walkthrough.md) note) |
| `model_tag`, `adapter_name`, `source_dataset`, `source_variant`, `target_dataset`, `target_variant`, `split` | Experiment metadata; not all populated for every category |

## `worst_case_examples_judging.csv`

The worst- and best-scoring Output Judging selection for PLOS (best-of-5) and eLife (best-of-3). 4 rows: 2 targets × {worst, best}.

**Columns**

| Column | Meaning |
|---|---|
| `category`, `system`, `target_corpus`, `example_type` | Same meaning as above (`system` here is `best5` / `best3`) |
| `source` | Full source article |
| `reference` | Human reference simplification |
| `selected_prediction` | The text the judge actually selected |
| `winner_index`, `winner_model`, `match_status` | Placeholder columns in the original per-row export — not yet populated (see open item below) |
| `best_adapter` | The underlying adapter that produced the selected candidate (populated, from the separate judge log) |
| `score` | The judge's 1–5 confidence rating for the selected candidate |

**Known gap:** `winner_index` / `winner_model` are placeholders inherited from the original `methodC_*.csv` export and are not populated in this file either. `best_adapter` and `score` (merged in from `judge_PLOS_best5.csv` / `judge_eLife_best3.csv`) are the reliable source of winner attribution until that export is backfilled.

