---
title: Qualitative examples
nav_order: 8
layout: default
---

# Qualitative examples

The numbers in the paper's tables are aggregates. This page shows a handful of individual predictions behind those numbers, picked deliberately from the **low end** of the worst-case entailment distribution — the sentence in each output that scored lowest against the source article — paired with the highest-scoring sentence from the same system for contrast.

These are not cherry-picked failures unique to one system. Every stage we tested — zero-shot, in-domain, cross-domain, self-training, merging, and output judging — produced at least one near-zero worst-case sentence somewhere in its test set. That pattern is itself the point of reporting a minimum instead of only an average: a system can look strong on aggregate while still containing an isolated unsupported claim.

The full worst-case and best-case row for every configuration we tested (not just the ones below) is in [`data/worst_case_examples_AB.csv`](../data/worst_case_examples_AB.csv) and [`data/worst_case_examples_judging.csv`](../data/worst_case_examples_judging.csv).

## Failure mode 1: empty generation

Zero-shot baselines occasionally produced no usable output for a given source at all. This isn't a hallucination — the model didn't say anything unsupported, it just didn't say anything — but it still collapses the worst-case score to zero, and a purely reference-based metric like ROUGE would penalize it the same way it penalizes a fluent but wrong sentence. We treat these as a distinct, lower-severity failure mode from the ones below: nothing false was stated, but nothing useful was produced either.

## Failure mode 2: fluent but generic filler

In several self-training runs, the lowest-scoring sentence in an otherwise reasonable output was fluent, on-topic in a loose sense, but disconnected from anything stated in the specific source article — closer to a plausible-sounding continuation than a grounded claim. For example, one self-trained system's worst sentence read as a generic mechanistic statement about a signaling pathway; the reference summary for that same article was about an entirely different anatomical structure. The sentence would not read as obviously wrong to someone unfamiliar with the source, which is exactly why an average-only metric can miss it: the rest of the output was well-grounded, so the mean score stayed high.

## Failure mode 3: a specific, unsupported number

This is the clearest illustration of why worst-case matters. One of the parameter-merged (CO+PLB) predictions on PLOS was, sentence by sentence, a well-grounded and fluent simplification — except for one sentence reporting precise clinical statistics (a median duration in days, an interquartile range) that could not be traced to any single chunk of the source article. Nothing about the sentence looks out of place stylistically; it reads like the rest of the summary. An average-based faithfulness score would be pulled down only slightly by one bad sentence in an otherwise strong output. The worst-case score flags it directly.

## Failure mode 4: the judge's best pick was still unsimplified

Output judging selects the strongest of several candidates, but "strongest of several candidates" is not the same as "good." In the lowest-scoring eLife case (judge score 1 out of 5, selected from `ministral8b_PLABA_textrank_adapter`), the chosen candidate carried over raw inferential statistics from the source article (test statistics, p-values) rather than translating them into lay language. This isn't a faithfulness failure in the entailment sense — the numbers are accurate — but it is a simplification failure, and it's a useful reminder that MedEntail measures *faithfulness*, not *readability*; the two need to be checked separately. The [Complementary Metrics](../README.md) section of the paper covers this distinction.

## Other Pages:

1. [MedEntail walkthrough](01_medentail_walkthrough) — what the metric computes, step by step, with a worked example.
2. [Premise variants](02_premise_variants) — whole vs. sentence vs. chunk, and which one the public library actually supports.
3. [Repetition penalty](03_repetition_penalty) — why raw entailment scores need a repetition penalty, and how it's applied.
4. [Why worst-case](04_why_worst_case) — why we report $\mathrm{ME}_{\min}$ alongside $\mathrm{ME}_{\mathrm{mean}}$ instead of only the average.
5. [The copy trap](05_copy_trap) — why a system that copies the source is trivially "faithful," and how we guard against it. 
6. [TextRank vs. lead](06_textrank_vs_lead) — comparing source-selection strategies for long articles. 
7. [Judge ceiling](07_judge_ceiling) — how output judging is bounded by the quality of its candidate pool.
8. [Qualitative examples](08_qualitative_examples) — real worst-case and best-case predictions from the test sets, illustrating four distinct failure modes.


## Reading these examples

None of the four patterns above are unique to one adaptation level — they're illustrative of the kinds of failures the worst-case metric is designed to catch, not a claim that any one method is uniquely prone to any one pattern. For the aggregate comparison across methods, see the paper's main results table; this page exists to make a few of those numbers concrete.
