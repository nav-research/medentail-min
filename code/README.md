**Worst-case source-entailment for medical text simplification.**

> This repository accompanies a manuscript currently under review at IEEE J-BHI.
> A citation will be provided upon acceptance.

`medentail_min` measures whether a generated simplification is *supported by its
source*, and — unlike faithfulness metrics that report only an average — it
reports the **worst-case** support as well. A summary can be faithful on average
yet contain a single passage that contradicts or is unsupported by the source;
averaging hides this, the minimum exposes it.

## What it computes

Each sentence of the output (the *hypothesis*) is checked against the source
(the *premise*) with natural language inference. A sentence's support is the
maximum entailment it achieves over the source segments. Two document scores are
then reported:

| Score | Meaning |
|-------|---------|
| `ME_mean` | average sentence support — overall faithfulness |
| `ME_min`  | **worst** sentence support — localized unfaithfulness |

`ME_min` is the quantity this package emphasizes.

By default the source is segmented into fixed-length token **chunks** (suitable
for long documents such as full-text articles); a sentence-level variant is also
available.

## Installation

```bash
git clone https://github.com/<user>/medentail_min.git
cd medentail_min
pip install -r requirements.txt
```

The NLI model [`pritamdeka/PubMedBERT-MNLI-MedNLI`](https://huggingface.co/pritamdeka/PubMedBERT-MNLI-MedNLI)
(~400 MB) downloads automatically on first use. A GPU is recommended for corpora
of more than a few dozen documents.

## Usage

```python
from medentail import MedEntail

me = MedEntail()                          # loads the NLI model on first call

# corpus scoring
result = me.score(sources, predictions)   # sources, predictions: list[str]
print(result.min, result.mean)            # corpus ME_min and ME_mean
print(result.per_example[0].min)          # per-document worst-case

# single pair
s = me.score_one(source, prediction)
print(s.min, s.mean)
```

Run the built-in example:

```bash
python -m medentail_min.example
```

## Options

`MedEntail` exposes every numerical setting as a constructor argument; the
defaults reproduce the configuration used in the paper. Change them only for
ablation.

| Argument | Default | Meaning |
|----------|---------|---------|
| `method` | `"chunk"` | source segmentation: `"chunk"` or `"sentence"` |
| `chunk_tokens` / `overlap` | `400` / `50` | source chunk size and overlap (tokens) |
| `max_length` | `512` | maximum NLI input length |
| `hyp_max_tokens` | `400` | truncation for each output sentence |
| `batch_size` | `64` | NLI inference batch size |
| `nli_model` | PubMedBERT-MNLI-MedNLI | any HuggingFace sequence-classification NLI model |
| `entailment_idx` | `1` | entailment column; pass `None` to auto-detect from `config.id2label` |
| `device` | auto | `"cuda"`, `"cpu"`, or `None` to auto-detect |

## Using a different NLI model

Any HuggingFace sequence-classification NLI model can be plugged in. Because the
entailment class sits at a different output index across models, pass
`entailment_idx=None` to detect it automatically from the model's
`config.id2label`:

```python
me = MedEntail(
    nli_model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
    entailment_idx=None,   # auto-detected from config.id2label
)
```

> **Note.** Changing the NLI model produces a different, internally-consistent
> metric that is **not comparable** to the numbers reported in the paper. The
> default model reproduces the paper's values.

## Performance

The metric runs one NLI pass per (output sentence × source segment), so cost
grows with document length. To speed things up:

- **Use a GPU.** By far the largest factor; `device` auto-detects CUDA.
- **Increase `batch_size`** (e.g. 128) if GPU memory allows.
- **The model caches after first download** (`~/.cache/huggingface`), so only
  the first run pays the download cost.

Long sources (e.g. full-text articles of ~10k tokens) are the slowest case, as
each output sentence is compared against many source chunks.

### Gated NLI models

The default model is public and needs no authentication. If you point
`nli_model` at a *gated* model (one requiring license acceptance), authenticate
first:

```python
from huggingface_hub import login
login(token="hf_...")
```

## Notes

This is an explicit, worst-case formulation of the *MedEntail* metric named in
prior work (Nasimov et al., 2025), grounded in NLI-based faithfulness evaluation
(Laban et al., 2022, *SummaC*). The contribution emphasized here is the
worst-case (minimum) aggregation, `ME_min`.

## License

MIT — see [LICENSE](../LICENSE).

## Citation

This work is under review. A citation will be provided upon acceptance.
