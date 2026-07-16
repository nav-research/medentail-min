---
title: Premise variants
nav_order: 2
---

# Premise variants: whole, sentence, chunk

MedEntail always splits the *prediction* into sentences (see [MedEntail walkthrough](01_medentail_walkthrough)). The *source* side can be represented three different ways, and which one is appropriate depends on how long the source is.

## The three variants

- **whole** — the entire source, untouched, used as a single premise. The NLI model's own tokenizer truncates it to `max_length` (512 tokens by default) if it's longer. Simple, but for a full-length article this throws away everything past the first ~512 tokens.
- **sentence** — the source split into sentences, each one a separate premise unit. Appropriate when the source is already short (PLABA, Cochrane, SimpleDC), where sentence-level premises give finer granularity than treating the whole thing as one block.
- **chunk** — the source split into overlapping token windows (400 tokens, 50-token overlap by default). Appropriate for full-length articles (PLOS, eLife) that exceed the encoder's limit — this is what lets every part of a long article serve as a potential premise, not just the beginning.

## What the public library supports

The [`medentail_min`](../medentail_min/README.md) library's `MedEntail` class exposes **`method="chunk"`** and **`method="sentence"`** — these are the two variants used to produce every number reported in the paper. **`method="whole"` is not implemented.** The "whole" column that appears in [Why worst-case](04_why_worst_case) was computed with a separate, ad-hoc script for that one illustrative comparison; it isn't part of the library's API and isn't used anywhere in the paper's actual results.

If you want the effect of "whole" for a short source, note that `method="chunk"` already reduces to it automatically: `_chunk()` returns the source untouched as a single-element list whenever it's under `chunk_tokens` (400) tokens to begin with. The gap only matters for sources *longer* than 400 tokens, where "whole" would truncate at the encoder's 512-token limit instead of covering the full text through overlapping windows — which is exactly why "whole" isn't a serious option for PLOS/eLife-length articles and was never adopted beyond the sensitivity test.

## Which one is used where

| Source length | Variant used | Targets |
|---|---|---|
| Short (fits comfortably under ~400 tokens) | `sentence` | PLABA, Cochrane, SimpleDC |
| Long (full articles, exceed the encoder limit) | `chunk` | PLOS, eLife |
| — | `whole` | Not used in any reported result; illustrative only, see [Why worst-case](04_why_worst_case) |
