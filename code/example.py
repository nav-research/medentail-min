"""Minimal example for medentail_min.

Run:  python -m medentail_min.example
The NLI model (~400 MB) downloads on first run.
"""

from medentail_min import MedEntail


def main():
    # A source passage and two candidate simplifications.
    source = (
        "Diabetes mellitus is a chronic metabolic disorder marked by elevated "
        "blood glucose. The hormone insulin normally moves glucose from the "
        "blood into cells. When insulin is absent or ineffective, glucose "
        "accumulates in the blood, and over time this can damage nerves, "
        "kidneys, and blood vessels."
    )

    faithful = (
        "Diabetes is a long-term condition where blood sugar stays too high. "
        "Insulin usually helps sugar move into cells, and without it the sugar "
        "builds up and can harm nerves, kidneys, and blood vessels over time."
    )

    partly_unfaithful = (
        "Diabetes is a condition where blood sugar stays too high. "
        "It is caused by eating too much sugar and is always cured by insulin."
    )

    me = MedEntail()  # loads the NLI model on this first call

    for label, pred in [("faithful", faithful),
                        ("partly unfaithful", partly_unfaithful)]:
        s = me.score_one(source, pred)
        print(f"{label:18s}  ME_min={s.min:.3f}  ME_mean={s.mean:.3f}")

    # Corpus scoring returns per-example scores too.
    result = me.score([source, source], [faithful, partly_unfaithful])
    print(f"\ncorpus  ME_min={result.min:.3f}  ME_mean={result.mean:.3f}")
    print("The unfaithful summary should show a clearly lower ME_min, "
          "even if its ME_mean stays high.")


if __name__ == "__main__":
    main()
