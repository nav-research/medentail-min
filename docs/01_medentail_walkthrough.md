---
title: MedEntail walkthrough
nav_order: 1
---

# MedEntail walkthrough

This page walks through what MedEntail actually computes for a single (source, prediction) pair, step by step, with a small worked example. For the design rationale (why worst-case, why chunk vs. sentence premises), see [Why worst-case](04_why_worst_case) and [Repetition penalty](03_repetition_penalty).

## The idea in one sentence

For every sentence in the model's output, check whether it's entailed by *some* part of the source article; a sentence that isn't supported anywhere in the source is a faithfulness failure, regardless of how well the rest of the output reads.

## Step 1 — split the prediction into sentences

The hypothesis side is always split into sentences (`nltk.sent_tokenize`), never treated as one block. This is what makes the metric sentence-level rather than document-level: a single bad sentence can't be diluted by the good sentences around it.

```python
hyp = [s for s in sent_tokenize(prediction) if s.strip()]
```

## Step 2 — decide how to split the source (premise units)

The source side is split differently depending on its length:

- **Long articles** (PLOS, eLife — full text exceeds the encoder's token limit): split into overlapping **token windows** (400 tokens, 50-token overlap). This is the *chunk* variant.
- **Short sources** (PLABA, Cochrane, SimpleDC): split into **sentences**, the same way the prediction is. This is the *sentence* variant.

```python
premises = chunk(source, chunk_tokens=400, overlap=50)   # long sources
# or
premises = sent_tokenize(source)                          # short sources
```

Both variants exist because chunking a short source into 400-token windows would usually just return the whole source as a single "chunk" anyway — the sentence variant gives finer-grained premises when the source is already short enough for that to matter.

## Step 3 — score every (premise, prediction-sentence) pair

Each prediction sentence is checked against *every* premise unit using a natural-language-inference model fine-tuned on medical text (`pritamdeka/PubMedBERT-MNLI-MedNLI`), and the **best-supporting premise wins**:

```python
def sentence_score(premises, hyp_sentence):
    return max(entailment_prob(p, hyp_sentence) for p in premises)
```

`entailment_prob` returns the softmax probability of the entailment class (index 1 of 3: contradiction / entailment / neutral). Taking the max over premises answers "is this claim supported *somewhere* in the source?" — a claim doesn't need to be supported by every chunk, just one.

## Step 4 — aggregate

Each prediction sentence now has one score (its best entailment against any premise). Two aggregations are reported:

- **$\mathrm{ME}_{\mathrm{mean}}$** — average across the prediction's sentences. Answers "how well-grounded is this output on average?"
- **$\mathrm{ME}_{\min}$** — minimum across the prediction's sentences. Answers "is there any sentence in this output that isn't supported at all?"

These per-example scores are then averaged again across the whole test set to get the corpus-level $\mathrm{ME}_{\mathrm{mean}}$ / $\mathrm{ME}_{\min}$ reported in the paper's tables.

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

The average score (0.485) looks like a mediocre-but-not-alarming result. The worst-case score (0.03) makes the actual problem visible: H2 is an unsupported claim ("cured" is stronger than anything in the source, and no premise mentions a cure), and no amount of averaging with the good sentence H1 should hide that. This is the exact failure pattern documented with real model outputs in [Qualitative examples](08_qualitative_examples.md).

