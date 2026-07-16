---
title: MedEntail walkthrough
nav_order: 1
---

# MedEntail walkthrough

This page walks through what MedEntail actually computes for a single (source, prediction) pair, step by step, with a small worked example. For the design rationale (why worst-case, why chunk vs. sentence premises), see [Why worst-case](04_why_worst_case) and [Repetition penalty](03_repetition_penalty).

## The idea in one sentence

For every sentence in the model's output, check whether it's entailed by *some* part of the source article; a sentence that isn't supported anywhere in the source is a faithfulness failure, regardless of how well the rest of the output reads.

The code below is trimmed from the actual [`medentail_min`](../medentail_min/README.md) library (the `MedEntail` class), not simplified pseudocode — running `scorer.score_one(source, prediction)` does exactly this.

## Step 1 — split the prediction into sentences

The hypothesis side is always split into sentences (`nltk.sent_tokenize`), never treated as one block. This is what makes the metric sentence-level rather than document-level: a single bad sentence can't be diluted by the good sentences around it. Each sentence is also truncated to `hyp_max_tokens` (400 by default) before scoring.

```python
# inside score_one():
hyp = [s for s in self._sent_tokenize(str(prediction)) if s.strip()]
```

## Step 2 — decide how to split the source (premise units)

The source side is split differently depending on its length, chosen once when the scorer is constructed (`method="chunk"` or `method="sentence"`), not per call:

- **Long articles** (PLOS, eLife — full text exceeds the encoder's token limit): split into overlapping **token windows** (400 tokens, 50-token overlap by default). This is the *chunk* variant.
- **Short sources** (PLABA, Cochrane, SimpleDC): split into **sentences**, the same way the prediction is. This is the *sentence* variant.

```python
def _chunk(self, text: str) -> list[str]:
    ids = self._tok(text, add_special_tokens=False)["input_ids"]
    if len(ids) <= self.chunk_tokens:
        return [text]
    step = max(1, self.chunk_tokens - self.overlap)
    chunks = []
    for st in range(0, len(ids), step):
        piece = ids[st:st + self.chunk_tokens]
        if not piece:
            break
        chunks.append(self._tok.decode(piece, skip_special_tokens=True))
        if st + self.chunk_tokens >= len(ids):
            break
    return chunks

def _premises(self, source: str) -> list[str]:
    if self.method == "chunk":
        return self._chunk(str(source))
    return [s for s in self._sent_tokenize(str(source)) if s.strip()]
```

Both variants exist because chunking a short source into 400-token windows would usually just return the whole source as a single "chunk" anyway (see the `if len(ids) <= self.chunk_tokens: return [text]` short-circuit above) — the sentence variant gives finer-grained premises when the source is already short enough for that to matter.

## Step 3 — score every (premise, prediction-sentence) pair

Every prediction sentence is paired with every premise unit, and all pairs are scored in a single batched pass through the NLI model (`pritamdeka/PubMedBERT-MNLI-MedNLI`) rather than one call per pair — this is the actual bottleneck-avoiding implementation, not just a conceptual simplification:

```python
def _per_sentence_support(self, premises, hypotheses):
    """For each hypothesis sentence, max entailment over the premises."""
    if not premises or not hypotheses:
        return np.array([])
    # each hypothesis sentence is truncated before scoring
    hyp = [
        self._tok.decode(
            self._tok(h, add_special_tokens=False, truncation=True,
                      max_length=self.hyp_max_tokens)["input_ids"],
            skip_special_tokens=True,
        )
        for h in hypotheses
    ]
    P, H = [], []
    for h in hyp:
        for p in premises:
            P.append(p)
            H.append(h)
    M = np.array(self._entail(P, H)).reshape(len(hyp), len(premises))
    return M.max(axis=1)   # best-supporting premise per sentence
```

`self._entail` runs the NLI model in batches (`batch_size=64` by default) and returns the softmax probability of the entailment class (`entailment_idx=1` for this model, out of 3: contradiction / entailment / neutral). Taking the **max** over premises for each sentence answers "is this claim supported *somewhere* in the source?" — a claim doesn't need to be supported by every chunk, just one.

## Step 4 — aggregate

Each prediction sentence now has one score (its best entailment against any premise). Two aggregations are reported:

```python
def score_one(self, source, prediction):
    self._ensure_loaded()   # the NLI model is downloaded/loaded here, on first call
    prem = self._premises(source)
    hyp = [s for s in self._sent_tokenize(str(prediction)) if s.strip()]
    per = self._per_sentence_support(prem, hyp)
    if len(per) == 0:
        return ExampleScore(min=0.0, mean=0.0)
    return ExampleScore(min=float(per.min()), mean=float(per.mean()))
```

- **$\mathrm{ME}_{\mathrm{mean}}$** — average across the prediction's sentences. Answers "how well-grounded is this output on average?"
- **$\mathrm{ME}_{\min}$** — minimum across the prediction's sentences. Answers "is there any sentence in this output that isn't supported at all?" An empty prediction (no sentences) scores 0 on both, rather than being skipped.

These per-example scores are then averaged again across the whole test set (`scorer.score(sources, predictions)`) to get the corpus-level $\mathrm{ME}_{\mathrm{mean}}$ / $\mathrm{ME}_{\min}$ reported in the paper's tables.

## Worked example

Source (toy, three premise units after chunking):

> **P1:** "Patients received either the study drug or placebo for eight weeks."
> **P2:** "The primary outcome was change in symptom score from baseline."
> **P3:** "No serious adverse events were reported in either arm."

Prediction, split into two sentences:

> **H1:** "Patients took the drug or a placebo for eight weeks and were checked for symptom changes."
> **H2:** "The drug cured the underlying condition in most patients."

Scoring:

| Hypothesis sentence | Best premise | Entailment score |
|---|---|---|
| H1 | P1 (and partly P2) | 0.94 |
| H2 | none of P1–P3 support this | 0.03 |

Aggregation for this example:
- $\mathrm{ME}_{\mathrm{mean}} = (0.94 + 0.03) / 2 = 0.485$
- $\mathrm{ME}_{\min} = 0.03$

The average score (0.485) looks like a mediocre-but-not-alarming result. The worst-case score (0.03) makes the actual problem visible: H2 is an unsupported claim ("cured" is stronger than anything in the source, and no premise mentions a cure), and no amount of averaging with the good sentence H1 should hide that. This is the exact failure pattern documented with real model outputs in [Qualitative examples](08_qualitative_examples).

## A preprocessing pitfall to watch for

If you're trying this yourself and your `min`/`mean` come out identical (or otherwise look wrong), check your input lists for **implicit string concatenation**. Python silently joins adjacent string literals that aren't separated by a comma:

```python
# WRONG — no commas between the strings
sources = ["Patients received either the study drug or placebo for eight weeks."
    "The primary outcome was change in symptom score from baseline."
    "No serious adverse events were reported in either arm."]
```

This is not a 3-element list. It's a single string — Python has concatenated the three lines into one, with no space between them (`"...eight weeks.The primary outcome...baseline.No serious adverse..."`). The same mistake in a `predictions` list turns two intended sentences into one. Since a list with one element has an identical min and mean by definition, this bug shows up exactly as `Min == Mean`, which is a useful tell that something upstream got merged that shouldn't have been.

Always add commas between list elements, and add a space (or newline) between sentences you *do* want joined into one string, so `sent_tokenize` can find the sentence boundary:

```python
source = (
    "Patients received either the study drug or placebo for eight weeks. "
    "The primary outcome was change in symptom score from baseline. "
    "No serious adverse events were reported in either arm."
)
```

## Trying it yourself

### `score_one` — a single pair

```python
scorer = MedEntail()

result = scorer.score_one(
    source="Patients received either the study drug or placebo for eight weeks. "
      "The primary outcome was change in symptom score from baseline. "
      "No serious adverse events were reported in either arm.",
    prediction="Patients took the drug or a placebo for eight weeks and were checked for symptom changes. "
        "The drug cured the underlying condition in most patients.",
)

print("Min:", result.min)
print("Mean:", result.mean)
```

```
Min: 0.00020720790780615062
Mean: 0.49971957122761523
```

This matches the toy example above: the second sentence's fabricated "cured" claim collapses `min` toward zero while `mean` stays near 0.5, because it's being averaged against the well-grounded first sentence.

### `score` — a small corpus, faithful vs. unfaithful

```python
source = (
    "Diabetes mellitus is a chronic metabolic disorder marked by elevated "
    "blood glucose. The hormone insulin normally moves glucose from the "
    "blood into cells. When insulin is absent or ineffective, glucose "
    "accumulates in the blood, and over time this can damage nerves, "
    "kidneys, and blood vessels."
)

faithful = (
    "Diabetes is a long-term condition where blood sugar stays too high. "
    "Insulin usually helps sugar move into cells, and without it the sugar "
    "builds up and can harm nerves, kidneys, and blood vessels over time."
)

partly_unfaithful = (
    "Diabetes is a condition where blood sugar stays too high. "
    "It is caused by eating too much sugar and is always cured by insulin."
)

me = MedEntail()

for label, pred in [("faithful", faithful), ("partly unfaithful", partly_unfaithful)]:
    s = me.score_one(source, pred)
    print(f"{label:18s}  ME_min={s.min:.3f}  ME_mean={s.mean:.3f}")

result = me.score([source, source], [faithful, partly_unfaithful])
print(f"\ncorpus  ME_min={result.min:.3f}  ME_mean={result.mean:.3f}")
```

```
faithful            ME_min=0.223  ME_mean=0.611
partly unfaithful   ME_min=0.000  ME_mean=0.500

corpus  ME_min=0.112  ME_mean=0.556
```

The two predictions' `ME_mean` values (0.611 vs. 0.500) don't look dramatically different — both look like middling summaries. `ME_min` tells a sharper story: the faithful version has *some* support for every sentence (0.223), while the unfaithful version has at least one sentence with essentially none (0.000) — the two added claims ("caused by eating too much sugar", "always cured by insulin") that the source never states. Ranking these two by `ME_mean` alone would understate the gap between them.
