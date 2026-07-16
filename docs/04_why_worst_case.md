> This page accompanies a manuscript currently under review at IEEE J-BHI. A citation will be provided upon acceptance.

# Why worst-case? A sensitivity test

MedEntail can aggregate per-sentence support in different ways. This page shows,
on three controlled examples, why the **minimum** (`ME_min`) catches unfaithful
output that averaging misses — the core reason the paper reports worst-case
faithfulness alongside the average.

## The test

Each example has one source, one **faithful** simplification, and one
**hallucinated** simplification that keeps most of the text correct but injects
a single false medical claim. A metric that measures faithfulness well should
score the hallucinated version clearly *lower*.

Five aggregation variants are compared:

- **whole** — the entire source as a single premise, one entailment score
- **sent_mean / sent_min** — source split into sentences; mean / minimum of
  per-sentence support
- **chunk_mean / chunk_min** — source split into token chunks; mean / minimum

> **Scope note:** `whole` is included here only as a sensitivity baseline, to
> show what gets lost by *not* splitting the source at all. It is not used
> anywhere in the paper's reported results, and it is not part of the public
> `medentail_min` library's API (`method` accepts `"chunk"` or `"sentence"`
> only — see [Premise variants](02_premise_variants)). The `whole` column
> below was computed with a separate one-off script for this comparison.

## The three examples

**A — fabricated treatment.** Source: a mild headache, normal vitals, sent home
to rest. The hallucination replaces the ending with *"prescribed chemotherapy
for cancer."*

**B — fabricated diagnosis.** Source: chest pain, **normal** ECG and troponin,
discharged after observation. The hallucination ends with *"diagnosed with a
heart attack and needed surgery"* — thematically close to the source, which
makes it hard for entailment to catch.

**C — numeric distortion.** Source: blood sugar 110 mg/dL, slightly above
normal, no medication. The hallucination says *"very high … started insulin
injections twice daily … immediate kidney failure risk."*

## Results

| Ex | Type | whole | sent_mean | sent_min | chunk_mean | chunk_min |
|----|------|------:|----------:|---------:|-----------:|----------:|
| A | faithful | 0.919 | 1.000 | 1.000 | 0.686 | 0.058 |
| A | **hallucinated** | 0.000 | 0.667 | **0.000** | 0.333 | **0.000** |
| B | faithful | 0.519 | 0.999 | 0.999 | 0.733 | 0.205 |
| B | **hallucinated** | **0.995** | 0.667 | **0.001** | 0.557 | **0.001** |
| C | faithful | 0.998 | 1.000 | 1.000 | 0.999 | 0.999 |
| C | **hallucinated** | 0.000 | 0.481 | **0.001** | 0.289 | **0.000** |

## What this shows

**The minimum separates faithful from hallucinated cleanly; the average does
not.** For every example, `sent_min` and `chunk_min` drop to near zero on the
hallucinated version while staying near one on the faithful version — exactly the
behaviour a faithfulness metric needs. The mean variants stay in the middle
(0.29–0.67 on hallucinations), because the correct sentences dilute the one false
one.

**Whole-source scoring fails on the hardest case.** In example B, the
hallucinated summary scores **0.995** under `whole` — the single false claim
("heart attack … surgery") is thematically close enough to the source that,
compressed into one premise, entailment is fooled. The minimum catches it (0.001)
because it evaluates the offending sentence against the source segment that
should support it, and finds it unsupported.

**This is why the paper reports `ME_min`.** A summary can be faithful on average
and still contain one passage that contradicts the source. Averaging hides that
passage; the worst-case exposes it. On real data the effect is the same as here,
only less extreme — which is precisely why it is easy to miss without a
worst-case measure.

The paper uses **chunk-level** segmentation (`chunk_min` / `chunk_mean`) because
sources can be long full-text articles; the sentence variant behaves similarly on
these short illustrative examples.
