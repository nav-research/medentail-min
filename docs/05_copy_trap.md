---
title: The copy trap
nav_order: 5
layout: default
---

# The copy trap

MedEntail measures whether a prediction is supported by the source. It does not, by itself, measure whether the prediction is a *simplification* of the source. These are not the same thing, and the gap between them has a name in this project: the **copy trap**.

## Why faithfulness alone isn't enough

A system that copies its source verbatim is, by construction, entailed by that source — every sentence it outputs literally appears in the premise. Such a system would score near-perfectly on MedEntail while performing no simplification whatsoever. If faithfulness were the only thing being optimized for or selected on, a non-simplifying copier would look like the best system available.

This isn't a hypothetical failure mode. It shows up in real model-selection decisions in this project.

## The degeneracy rule

We flag a system as degenerate — faithful by copying, not by simplifying — if its ROUGE-L falls below **70% of the target corpus's in-domain ceiling**, where the ceiling is the strongest in-domain fine-tuned ROUGE-L observed for that target. Overlap has to be read relative to this ceiling rather than against some fixed threshold, because extreme-compression tasks like PLOS and eLife lay summarization have low ceilings to begin with (ROUGE-L ≈ 0.16–0.18, not the 0.3–0.4 range typical of less aggressive summarization).

$$\text{degenerate if } \mathrm{ROUGE\text{-}L} < 0.70 \times \mathrm{ROUGE\text{-}L}_{\text{in-domain ceiling}}(T)$$

## Real cases this rule catches

**Base-adapter selection for eLife self-training.** When selecting which cross-domain adapter to warm-start self-training from, the faithfulness-only criterion favors a SimpleDC-trained adapter — but that adapter's ROUGE-L is 0.10 against an in-domain ceiling of 0.16 (62% of ceiling, below the 70% cutoff). It scores well on MedEntail because it largely reproduces the source rather than simplifying it. The degeneracy rule removes it from consideration, and the next-best candidate (PLABA-trained) is used instead.

**Parameter-level merging on eLife.** Among the merged configurations, the one with the highest faithfulness product (PLS+SC) reaches ME_mean 0.981 and ME_min 0.916 — the best faithfulness numbers of any eLife merge — but its ROUGE-L is 0.089, about 55% of the in-domain ceiling. The same trap that appears in base-adapter selection reappears at the merging level: selecting purely by faithfulness would return a system that copies its input.

Both cases share the same shape: near-ceiling faithfulness paired with collapsed overlap. That combination is the signature of the copy trap, and it's why the paper reports ROUGE-L alongside MedEntail rather than treating faithfulness as a stand-alone objective.

## Practical takeaway

If you're using MedEntail to select or rank systems, don't use it in isolation. Pair it with an overlap metric (ROUGE-L is what we use) and check the ratio against an in-domain ceiling for your target corpus — a fixed absolute ROUGE-L threshold won't transfer across tasks with different achievable ceilings.

## Other Pages:

1. [MedEntail walkthrough](01_medentail_walkthrough) — what the metric computes, step by step, with a worked example.
2. [Premise variants](02_premise_variants) — whole vs. sentence vs. chunk, and which one the public library actually supports.
3. [Repetition penalty](03_repetition_penalty) — why raw entailment scores need a repetition penalty, and how it's applied.
4. [Why worst-case](04_why_worst_case) — why we report $\mathrm{ME}_{\min}$ alongside $\mathrm{ME}_{\mathrm{mean}}$ instead of only the average.
5. [The copy trap](05_copy_trap) — why a system that copies the source is trivially "faithful," and how we guard against it. 
6. [TextRank vs. lead](06_textrank_vs_lead) — comparing source-selection strategies for long articles. 
7. [Judge ceiling](07_judge_ceiling) — how output judging is bounded by the quality of its candidate pool.
8. [Qualitative examples](08_qualitative_examples) — real worst-case and best-case predictions from the test sets, illustrating four distinct failure modes.
