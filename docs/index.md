---
title: Index
nav_order: 0
permalink: /
layout: default
---

# medentail-min docs

This section documents the design decisions behind MedEntail, the worst-case entailment metric introduced in the paper, and the library that implements it. It is meant to be read roughly in order, but each page also stands alone.


## Pages

1. [MedEntail walkthrough](01_medentail_walkthrough) — what the metric computes, step by step, with a worked example.
2. [Premise variants](02_premise_variants) — whole vs. sentence vs. chunk, and which one the public library actually supports.
3. [Repetition penalty](03_repetition_penalty) — why raw entailment scores need a repetition penalty, and how it's applied.
4. [Why worst-case](04_why_worst_case) — why we report $\mathrm{ME}_{\min}$ alongside $\mathrm{ME}_{\mathrm{mean}}$ instead of only the average.
5. [The copy trap](05_copy_trap) — why a system that copies the source is trivially "faithful," and how we guard against it. 
6. [TextRank vs. lead](06_textrank_vs_lead) — comparing source-selection strategies for long articles. 
7. [Judge ceiling](07_judge_ceiling) — how output judging is bounded by the quality of its candidate pool.
8. [Qualitative examples](08_qualitative_examples) — real worst-case and best-case predictions from the test sets, illustrating four distinct failure modes.

## Library

The `medentail_min/` folder contains a minimal, MIT-licensed implementation of the metric described here, independent of the adaptation methods studied in the paper. See its own [README](../medentail_min/README.md) for usage.
