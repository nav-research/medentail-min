# medentail-min

A minimal, dependency-light implementation of MedEntail — a worst-case, entailment-based faithfulness metric for medical text simplification. See the [docs](../docs/00_index.md) for the design rationale; this README covers installation and usage.

> Manuscript under review. This library is released independently of the paper's adaptation methods, for anyone evaluating faithfulness in text simplification or summarization.

## What it does

For a (source, prediction) pair, MedEntail splits the prediction into sentences and checks each one against the source using a natural-language-inference model. Each sentence gets the score of its best-supporting evidence in the source; the result is reported as both the **mean** (average grounding) and the **min** (worst-case — is there any unsupported sentence at all). An empty prediction scores 0 on both.

## Installation


```bash
pip install git+https://github.com/nav-research/medentail-min.git#subdirectory=medentail_min
```

Requires `torch`, `transformers`, and `nltk` (`punkt`/`punkt_tab` are downloaded automatically on first use if missing). The NLI model (`pritamdeka/PubMedBERT-MNLI-MedNLI` by default) is also loaded lazily on first use, not at construction.

## Quickstart

```python
from medentail_min import MedEntail

scorer = MedEntail()  # nothing loads yet

result = scorer.score_one(
    source="Patients received either the study drug or placebo for eight weeks...",
    prediction="Patients took the drug or a placebo for eight weeks and were checked for symptom changes. The drug cured the underlying condition in most patients.",
)

print(result.min)   # worst-case score, e.g. 0.03
print(result.mean)  # average score, e.g. 0.49
```

### Choosing the premise variant

The source-segmentation strategy is set when you construct the scorer, not per call — long sources should use overlapping token-window chunking, short sources can be split into sentences directly:

```python
scorer = MedEntail(method="chunk")     # default; for long sources (chunk_tokens=400, overlap=50)
scorer = MedEntail(method="sentence")  # for short sources
```

`chunk_tokens` and `overlap` are also constructor arguments (only used when `method="chunk"`), along with `max_length` (NLI input cap, default 512) and `hyp_max_tokens` (per-sentence truncation, default 400).

### Scoring a corpus

```python
result = scorer.score(sources, predictions)  # equal-length sequences

result.min           # corpus-level ME_min (mean of per-example worst-case scores)
result.mean          # corpus-level ME_mean
result.per_example   # list[ExampleScore], one per (source, prediction) pair
```

## API reference

| | |
|---|---|
| `MedEntail(nli_model="pritamdeka/PubMedBERT-MNLI-MedNLI", entailment_idx=1, method="chunk", chunk_tokens=400, overlap=50, max_length=512, hyp_max_tokens=400, batch_size=64, device=None)` | Constructor. Cheap — nothing is loaded until the first scoring call. All settings default to the values used in the paper; changing them changes the metric. Pass `entailment_idx=None` to auto-detect it from the model's `config.id2label` (needed if you swap in a different NLI checkpoint). `device` defaults to `"cuda"` if available, else `"cpu"`. |
| `.score_one(source, prediction) -> ExampleScore` | Scores a single pair. `.min` / `.mean`. |
| `.score(sources, predictions, progress=True) -> CorpusScore` | Scores a corpus. `.min` / `.mean` are corpus-level aggregates; `.per_example` is the full list of per-pair `ExampleScore`s. `progress=True` shows a `tqdm` bar if installed. Raises `ValueError` if `sources` and `predictions` have different lengths. |

## Model

Entailment scoring uses [`pritamdeka/PubMedBERT-MNLI-MedNLI`](https://huggingface.co/pritamdeka/PubMedBERT-MNLI-MedNLI) by default, with `entailment_idx=1`. If you use a different NLI model, either pass the correct index explicitly or pass `entailment_idx=None` to have it auto-detected by searching the model's `config.id2label` for a label containing "entail" — construction raises `ValueError` if that lookup fails, so a misconfigured model fails loudly rather than scoring the wrong class silently.

## License

MIT — see [`LICENSE`](../LICENSE) at the repository root.

## Citation

A citation entry will be added once the associated manuscript is published.
