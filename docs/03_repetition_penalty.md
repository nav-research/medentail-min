---
title: Repetition penalty
nav_order: 3
---

> This page accompanies a manuscript currently under review at IEEE J-BHI. A citation will be provided upon acceptance.

# Why `repetition_penalty = 1.15`?

All models in this study generate with a repetition penalty of **1.15**. This
page explains what that value does and why it was chosen, since the choice
affects every reported number.

## What the repetition penalty does

A repetition penalty multiplies down the probability of tokens the model has
already produced, making it less likely to select the same token again
[[Keskar et al., 2019]](#references). It is a decoding-time control, applied
identically to every model here.

- **1.0** — no penalty (raw greedy decoding).
- **> 1.0** — penalty applied; values in the **1.1–1.3** range are considered
  *light* and are the typical operating range. We use **1.15**.

## Why this is a trade-off, not a free choice

The penalty sits between two failure modes, and the value has to balance them.

**No penalty (1.0).** This is pure, uninterrupted greedy decoding — the model's
unmodified behaviour. The risk is that if a model falls into a repetition loop
on a given example, it produces degenerate text for that example
[[Holtzman et al., 2019]](#references). Its ROUGE and MedEntail scores then
collapse, and the metric reflects a *decoding pathology* rather than the model's
actual simplification quality. One looped example can unfairly drag down a
model's reported performance.

**Light penalty (1.15).** This suppresses repetition loops, keeping outputs
clean and making the metrics measure simplification quality rather than decoding
failure. The cost is that it is an intervention: we impose an external
constraint on the model's output. Because the penalty is light, the risk of
distorting meaning is low — but it is no longer strictly "raw" model behaviour.

## Why 1.15 and not 1.5

Higher values (**≥ 1.3**, and especially 1.5) make the penalty aggressive. The
model is then forced to also suppress *legitimate* repetition — medical terms,
numbers, and unavoidable words such as "patients" or "treatment" that naturally
recur in clinical text. At that point the penalty starts to **distort meaning**,
producing less fluent or incomplete output. At 1.5, repetition is essentially
eliminated, but the price can be loss of content.

**1.15 is the light-touch setting** that removes degenerate loops without
suppressing the domain vocabulary that medical simplification legitimately
repeats. The value is fixed in configuration and applied identically to all
models, so no model is advantaged or disadvantaged by a different decoding
setup.

## References

[1] N. S. Keskar, B. McCann, L. R. Varshney, C. Xiong, and R. Socher,
"CTRL: A Conditional Transformer Language Model for Controllable Generation,"
arXiv:1909.05858, 2019.

[2] A. Holtzman, J. Buys, L. Du, M. Forbes, and Y. Choi, "The Curious Case of
Neural Text Degeneration," arXiv:1904.09751, 2019.
