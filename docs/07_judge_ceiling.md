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
