---
title: TextRank vs. lead
nav_order: 6
layout: default
---

# TextRank vs. lead

PLOS and eLife source articles are longer than the encoder's context window, so before any generation or scoring happens, a strategy is needed to pick *which part* of the article to actually use. We compare two: **lead** (take the article from the beginning up to the token budget) and **textrank** (use TextRank to extractively rank sentences by centrality, then select from the top-ranked ones up to the same budget).

This page reports the zero-shot comparison — same model, same target corpus, only the source-selection strategy changes.

## Results

| Model | Target | ME_min (lead) | ME_min (textrank) | ROUGE-L (lead) | ROUGE-L (textrank) |
|---|---|---|---|---|---|
| BioMistral-7B | PLOS | 0.918 | 0.916 | 0.076 | 0.067 |
| BioMistral-7B | eLife | 0.935 | 0.937 | 0.049 | 0.042 |
| Llama-3.1-8B | PLOS | 0.556 | 0.595 | 0.143 | 0.143 |
| Llama-3.1-8B | eLife | 0.407 | 0.505 | 0.146 | 0.148 |
| MedGemma-4B | PLOS | 0.790 | 0.821 | 0.167 | 0.156 |
| MedGemma-4B | eLife | 0.703 | 0.808 | 0.153 | 0.136 |
| Ministral-8B | PLOS | 0.769 | 0.791 | 0.150 | 0.145 |
| Ministral-8B | eLife | 0.772 | 0.825 | 0.138 | 0.124 |
| Qwen2.5-7B | PLOS | 0.681 | 0.625 | 0.144 | 0.135 |
| Qwen2.5-7B | eLife | 0.449 | 0.452 | 0.141 | 0.134 |

(ME_min here is the chunk-variant worst-case score, ME_chunk_min, appropriate for these long-source targets — see [Why worst-case](04_why_worst_case).)

## What the pattern shows

In 8 of the 10 model/target pairs, **textrank gives an equal or higher worst-case faithfulness score than lead** — sometimes substantially (Llama-3.1-8B on eLife: 0.407 → 0.505; MedGemma-4B on eLife: 0.703 → 0.808). The intuition is straightforward: TextRank surfaces sentences that are central to the article's content regardless of where they appear, so a claim near the end of a long article is more likely to have a relevant, on-topic premise available to support it. Lead truncation, by contrast, can cut off exactly the passage a later sentence in the prediction depends on.

The trade-off is on the overlap side. In most of the same pairs, **ROUGE-L is flat or slightly lower under textrank** than under lead. This is a smaller, more consistent effect than the faithfulness gain, and the one exception (Qwen2.5-7B on PLOS, where lead outperforms textrank on both metrics) is a reminder that this is a general tendency, not a universal rule.

## Practical takeaway

TextRank source selection is a low-cost way to improve worst-case faithfulness on long-article targets, with a small and inconsistent cost to surface overlap. It doesn't replace any of the three adaptation levels studied in the paper — it's a preprocessing choice that interacts with all of them, since every prediction file used one variant or the other as its source context.
