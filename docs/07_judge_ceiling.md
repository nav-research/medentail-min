---
title: Judge ceiling
nav_order: 7
layout: default
---

# Judge ceiling

**A note on scope before the numbers:** the original plan for this page was an oracle comparison — for each example, what's the best score among *all* candidates the judge saw, versus the score of the candidate it actually picked? That comparison needs every candidate's score logged, not just the winner's. The current exports only log the winner (`best_adapter`) and the judge's self-reported confidence (`score`, 1–5) per example, not the full candidate pool's scores. So this page reports what that data *can* show — how often the judge's confidence itself was capped, and how concentrated its choices were — rather than a true oracle gap. If per-candidate logging is added later, this page should be rewritten around the original comparison.

## How often is the judge confident?

| Target | n | score = 5 (full confidence) | score < 5 |
|---|---|---|---|
| PLOS (best-of-5) | 1376 | 1312 (95.3%) | 64 (4.7%) |
| eLife (best-of-3) | 241 | 230 (95.4%) | 11 (4.6%) |

In roughly 19 out of 20 cases, the candidate pool contained at least one output the judge rated as fully acceptable. The remaining ~5% are the cases worth looking at: they're examples where *none* of the candidates in the pool were strong, and the judge had to pick the least-bad option. This is the practical ceiling on output judging — it can only be as good as the best candidate available to it, and roughly 1 in 20 times, that best candidate still wasn't good. See the eLife score = 1 example in [Qualitative examples](08_qualitative_examples) for what one of these looks like concretely.

## How concentrated are the winners?

| Target | Top adapter | Share of wins |
|---|---|---|
| PLOS (best-of-5) | `ministral8b_PLABA_textrank_adapter` | 84.6% |
| eLife (best-of-3) | `ministral8b_PLABA_textrank_adapter` | 70.1% |

The same adapter wins the large majority of the time on both targets. This means output judging, in practice, functions less like a diverse ensemble where different candidates win in different situations, and more like a confirmation step around one strong base candidate — with the pool occasionally supplying a better alternative (llama3.1-8b_PLABA_lead_adapter takes roughly a quarter of eLife wins) and rarely supplying something from further afield (the Cochrane- and SimpleDC-trained adapters combined win under 4% of PLOS cases).

## Practical takeaway

The 5% of low-confidence cases and the concentration of winners are two views of the same limitation: judging quality is bounded by the diversity and strength of the candidate pool, not by the judge's decision rule. A stronger judge model wouldn't move these numbers much; a stronger or more diverse candidate pool would.

## Other Pages:

1. [MedEntail walkthrough](01_medentail_walkthrough) — what the metric computes, step by step, with a worked example.
2. [Premise variants](02_premise_variants) — whole vs. sentence vs. chunk, and which one the public library actually supports.
3. [Repetition penalty](03_repetition_penalty) — why raw entailment scores need a repetition penalty, and how it's applied.
4. [Why worst-case](04_why_worst_case) — why we report $\mathrm{ME}_{\min}$ alongside $\mathrm{ME}_{\mathrm{mean}}$ instead of only the average.
5. [The copy trap](05_copy_trap) — why a system that copies the source is trivially "faithful," and how we guard against it. 
6. [TextRank vs. lead](06_textrank_vs_lead) — comparing source-selection strategies for long articles. 
7. [Judge ceiling](07_judge_ceiling) — how output judging is bounded by the quality of its candidate pool.
8. [Qualitative examples](08_qualitative_examples) — real worst-case and best-case predictions from the test sets, illustrating four distinct failure modes.
