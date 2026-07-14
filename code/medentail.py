"""
medentail_min — worst-case source-entailment for medical text simplification.

MedEntail measures whether a generated simplification is *supported by its
source*. Each sentence of the output (hypothesis) is checked, via natural
language inference, against the source (premise); a sentence's score is the
maximum entailment it achieves over the source segments. The document score
then aggregates these per-sentence scores in two ways:

    ME_mean  — the average sentence support (overall faithfulness)
    ME_min   — the *worst* sentence support (localized unfaithfulness)

ME_min is the quantity this package emphasizes: a summary can be faithful on
average yet contain a single passage that contradicts or is unsupported by the
source, which ME_mean hides but ME_min exposes.

This is an explicit, worst-case formulation of the MedEntail metric named in
prior work (Nasimov et al., 2025), grounded in NLI-based faithfulness
evaluation (Laban et al., 2022).

Basic use
---------
    from medentail_min import MedEntail

    me = MedEntail()                      # loads the NLI model on first use
    result = me.score(sources, predictions)
    print(result.min, result.mean)        # corpus worst-case and average

    single = me.score_one(source, prediction)
    print(single.min, single.mean)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple, Optional

import numpy as np


# ----------------------------------------------------------------------------- 
# Result containers
# -----------------------------------------------------------------------------
@dataclass
class ExampleScore:
    """Per-example faithfulness: worst-case and average sentence support."""
    min: float
    mean: float


@dataclass
class CorpusScore:
    """Corpus faithfulness, plus the per-example scores it aggregates.

    Attributes
    ----------
    min : float
        Mean over examples of each example's worst-case sentence support
        (corpus ME_min).
    mean : float
        Mean over examples of each example's average sentence support
        (corpus ME_mean).
    per_example : list[ExampleScore]
        The (min, mean) score of every (source, prediction) pair, in order.
    """
    min: float
    mean: float
    per_example: List[ExampleScore]


# -----------------------------------------------------------------------------
# Metric
# -----------------------------------------------------------------------------
class MedEntail:
    """Chunk-level source-entailment metric with worst-case aggregation.

    The NLI model is loaded lazily on the first scoring call, so constructing a
    ``MedEntail`` object is cheap. All numerical settings are exposed as
    constructor arguments and default to the values used in the accompanying
    paper; changing them changes the metric and is only recommended for
    ablation.

    Parameters
    ----------
    nli_model : str
        HuggingFace sequence-classification model producing (contradiction,
        entailment, neutral) logits. The entailment index is given by
        ``entailment_idx``.
    entailment_idx : int or None
        Column of the softmax output corresponding to entailment. Defaults to 1
        (correct for PubMedBERT-MNLI-MedNLI). Pass ``None`` to auto-detect it
        from the model's ``config.id2label`` when using a different NLI model.
    method : str
        Segmentation of the *source* into premises: ``"chunk"`` (fixed-length
        token windows, default) or ``"sentence"``. The prediction is always
        split into sentences.
    chunk_tokens, overlap : int
        Source chunk length and overlap in tokens (used when ``method="chunk"``).
    max_length : int
        Maximum NLI input length in tokens.
    hyp_max_tokens : int
        Each prediction sentence is truncated to this many tokens before NLI.
    batch_size : int
        NLI inference batch size.
    device : str or None
        ``"cuda"``, ``"cpu"``, or None to auto-detect.
    """

    def __init__(
        self,
        nli_model: str = "pritamdeka/PubMedBERT-MNLI-MedNLI",
        entailment_idx: Optional[int] = 1,
        method: str = "chunk",
        chunk_tokens: int = 400,
        overlap: int = 50,
        max_length: int = 512,
        hyp_max_tokens: int = 400,
        batch_size: int = 64,
        device: Optional[str] = None,
    ):
        if method not in ("chunk", "sentence"):
            raise ValueError("method must be 'chunk' or 'sentence'")
        self.nli_model = nli_model
        self.entailment_idx = entailment_idx
        self.method = method
        self.chunk_tokens = chunk_tokens
        self.overlap = overlap
        self.max_length = max_length
        self.hyp_max_tokens = hyp_max_tokens
        self.batch_size = batch_size
        self._device = device
        self._model = None
        self._tok = None
        self._sent_tokenize = None

    # --- lazy setup -----------------------------------------------------------
    def _ensure_loaded(self):
        if self._model is not None:
            return
        import torch
        from transformers import (
            AutoTokenizer,
            AutoModelForSequenceClassification,
        )

        if self._device is None:
            self._device = "cuda" if torch.cuda.is_available() else "cpu"

        self._torch = torch
        self._tok = AutoTokenizer.from_pretrained(self.nli_model)
        self._model = (
            AutoModelForSequenceClassification
            .from_pretrained(self.nli_model, num_labels=3)
            .to(self._device)
            .eval()
        )
        self._resolve_entailment_idx()

        import nltk
        for pkg in ("punkt", "punkt_tab"):
            try:
                nltk.data.find(f"tokenizers/{pkg}")
            except LookupError:
                nltk.download(pkg, quiet=True)
        from nltk.tokenize import sent_tokenize
        self._sent_tokenize = sent_tokenize

    def _resolve_entailment_idx(self):
        """Find the entailment column, from config.id2label if not given.

        When ``entailment_idx`` is None, look for a label containing 'entail'
        in the model's ``config.id2label``. Raises if it cannot be found, so a
        misconfigured model fails loudly rather than scoring the wrong class.
        """
        if self.entailment_idx is not None:
            return
        id2label = getattr(self._model.config, "id2label", None) or {}
        for idx, label in id2label.items():
            if "entail" in str(label).lower():
                self.entailment_idx = int(idx)
                return
        raise ValueError(
            "Could not auto-detect the entailment index from the model's "
            f"config.id2label ({id2label}). Pass entailment_idx explicitly."
        )

    # --- NLI ------------------------------------------------------------------
    def _entail(self, premises: Sequence[str], hypotheses: Sequence[str]) -> List[float]:
        """Entailment probability for each (premise, hypothesis) pair."""
        torch = self._torch
        out: List[float] = []
        with torch.no_grad():
            for i in range(0, len(premises), self.batch_size):
                enc = self._tok(
                    list(premises[i:i + self.batch_size]),
                    list(hypotheses[i:i + self.batch_size]),
                    return_tensors="pt",
                    padding=True,
                    truncation="only_first",
                    max_length=self.max_length,
                ).to(self._device)
                probs = torch.softmax(self._model(**enc).logits, dim=1)
                out.extend(probs[:, self.entailment_idx].tolist())
        return out

    # --- segmentation ---------------------------------------------------------
    def _chunk(self, text: str) -> List[str]:
        ids = self._tok(text, add_special_tokens=False)["input_ids"]
        if len(ids) <= self.chunk_tokens:
            return [text]
        step = max(1, self.chunk_tokens - self.overlap)
        chunks = []
        for st in range(0, len(ids), step):
            piece = ids[st:st + self.chunk_tokens]
            if not piece:
                break
            chunks.append(self._tok.decode(piece, skip_special_tokens=True))
            if st + self.chunk_tokens >= len(ids):
                break
        return chunks

    def _premises(self, source: str) -> List[str]:
        if self.method == "chunk":
            return self._chunk(str(source))
        return [s for s in self._sent_tokenize(str(source)) if s.strip()]

    def _per_sentence_support(self, premises, hypotheses) -> np.ndarray:
        """For each hypothesis sentence, max entailment over the premises."""
        if not premises or not hypotheses:
            return np.array([])
        # truncate each hypothesis sentence
        hyp = [
            self._tok.decode(
                self._tok(h, add_special_tokens=False, truncation=True,
                          max_length=self.hyp_max_tokens)["input_ids"],
                skip_special_tokens=True,
            )
            for h in hypotheses
        ]
        P, H = [], []
        for h in hyp:
            for p in premises:
                P.append(p)
                H.append(h)
        M = np.array(self._entail(P, H)).reshape(len(hyp), len(premises))
        return M.max(axis=1)

    # --- public API -----------------------------------------------------------
    def score_one(self, source: str, prediction: str) -> ExampleScore:
        """Score a single (source, prediction) pair.

        Returns an :class:`ExampleScore` with ``.min`` (worst sentence support)
        and ``.mean`` (average sentence support). An empty prediction scores 0.
        """
        self._ensure_loaded()
        prem = self._premises(source)
        hyp = [s for s in self._sent_tokenize(str(prediction)) if s.strip()]
        per = self._per_sentence_support(prem, hyp)
        if len(per) == 0:
            return ExampleScore(min=0.0, mean=0.0)
        return ExampleScore(min=float(per.min()), mean=float(per.mean()))

    def score(
        self,
        sources: Sequence[str],
        predictions: Sequence[str],
        progress: bool = True,
    ) -> CorpusScore:
        """Score a corpus of (source, prediction) pairs.

        Parameters
        ----------
        sources, predictions : sequence of str
            Equal-length sequences. ``sources[i]`` is the full source text,
            ``predictions[i]`` the generated simplification.
        progress : bool
            Show a progress bar (requires ``tqdm``).

        Returns
        -------
        CorpusScore
            ``.min`` and ``.mean`` are corpus-level; ``.per_example`` holds the
            individual scores.
        """
        if len(sources) != len(predictions):
            raise ValueError(
                f"sources ({len(sources)}) and predictions "
                f"({len(predictions)}) must have equal length"
            )
        self._ensure_loaded()

        pairs = zip(sources, predictions)
        if progress:
            try:
                from tqdm import tqdm
                pairs = tqdm(pairs, total=len(sources),
                             desc=f"MedEntail-{self.method}")
            except ImportError:
                pass

        per_example: List[ExampleScore] = []
        for s, p in pairs:
            per_example.append(self.score_one(s, p))

        mins = [e.min for e in per_example]
        means = [e.mean for e in per_example]
        return CorpusScore(
            min=float(np.mean(mins)) if mins else 0.0,
            mean=float(np.mean(means)) if means else 0.0,
            per_example=per_example,
        )
