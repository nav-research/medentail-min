# medentail-min

A minimal, dependency-light implementation of MedEntail — a worst-case, entailment-based faithfulness metric for medical text simplification. See the [docs](../docs/00_index.md) for the design rationale; this README covers installation and usage.

> Manuscript under review. This library is released independently of the paper's adaptation methods, for anyone evaluating faithfulness in text simplification or summarization.

## What it does

For a (source, prediction) pair, MedEntail splits the prediction into sentences and checks each one against the source using a natural-language-inference model. Each sentence gets the score of its best-supporting evidence in the source; the per-example result is reported as both the **mean** (average grounding) and the **min** (worst-case — is there any unsupported sentence at all).

## Installation

```bash
pip install git+https://github.com/nav-research/medentail-min.git#subdirectory=medentail_min
```

Requires `torch` and `transformers`; the NLI model (`pritamdeka/PubMedBERT-MNLI-MedNLI`) is downloaded on first use, not at import time.

## Quickstart

```python
from medentail_min import MedEntail

scorer = MedEntail()  # model loads lazily on first .score() call

result = scorer.score(
    source="Patients received either the study drug or placebo for eight weeks...",
    prediction="Patients took the drug or a placebo for eight weeks and were checked for symptom changes. The drug cured the underlying condition in most patients.",
)

print(result.me_min)   # worst-case score, e.g. 0.03
print(result.me_mean)  # average score, e.g. 0.49
```

### Choosing the premise variant

Long sources (full articles) should use overlapping token-window chunking; short sources can be split into sentences directly:

```python
result = scorer.score(source=full_article, prediction=summary, method="chunk")     # long sources
result = scorer.score(source=short_abstract, prediction=summary, method="sentence") # short sources
```

`method="chunk"` accepts `chunk_tokens` (default 400) and `overlap` (default 50) to control the window size.

### Scoring a corpus

```python
mins, means = scorer.score_corpus(sources, predictions, method="chunk")
```

Returns one score per example; average these across your test set to get the corpus-level `ME_min` / `ME_mean` reported in the paper.

## API reference

| | |
|---|---|
| `MedEntail(model_name=..., entailment_idx=None, device=None)` | Constructor. `entailment_idx` is auto-detected from the model's label config if not provided. Nothing is loaded from disk until the first `.score()` call. |
| `.score(source, prediction, method="chunk", chunk_tokens=400, overlap=50)` | Scores a single pair. Returns an object with `.me_min` and `.me_mean`. |
| `.score_corpus(sources, predictions, **kwargs)` | Scores a list of pairs. Returns `(mins, means)` as arrays. |

## Model

Entailment scoring uses [`pritamdeka/PubMedBERT-MNLI-MedNLI`](https://huggingface.co/pritamdeka/PubMedBERT-MNLI-MedNLI). The entailment class index is auto-detected from the model config rather than hard-coded, so swapping in a different NLI checkpoint with a different label ordering shouldn't silently break scoring — check `scorer.entailment_idx` after construction if you're using a non-default model.

## License

MIT — see [`LICENSE`](../LICENSE) at the repository root. No commercial-use restriction.

## Citation

A citation entry will be added once the associated manuscript is published.
