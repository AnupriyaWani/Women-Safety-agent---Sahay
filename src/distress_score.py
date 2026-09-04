"""
distress_score.py

WHAT THIS FILE DOES:
This is the "brain" - it combines everything we built so far:
  - audio features (pitch, energy) from extract_features.py
  - keyword detection from keyword_check.py

...into ONE final decision: LOW, MEDIUM, or HIGH distress.

HOW THE SCORING WORKS (explainable, not a black box):
1. We normalize pitch and energy into a 0-1 "how extreme is this" score,
   based on realistic ranges observed in our own real data.
2. We combine pitch_score + energy_score + keyword_bonus into one number.
3. We use fixed thresholds to sort that number into LOW / MEDIUM / HIGH.

These thresholds/weights are a starting point - in a real project you'd
tune them further using more data. That's explicitly fine to say in your
pitch: "these are our starting thresholds, tuned from real observed
audio data, and we'd refine them further with a larger dataset."
"""

import numpy as np

# --- Reference ranges, based on our real dataset's actual observed averages ---
# (from extract_features.py sanity check: distress vs normal averages)
PITCH_LOW_REF = 150    # roughly "calm" pitch (Hz)
PITCH_HIGH_REF = 450   # roughly "distress" pitch (Hz)

ENERGY_LOW_REF = 0.002   # roughly "calm" loudness
ENERGY_HIGH_REF = 0.012  # roughly "distress" loudness

# --- Weights: how much each signal contributes to the final score ---
WEIGHT_PITCH = 0.35
WEIGHT_ENERGY = 0.35
WEIGHT_PITCH_STD = 0.15   # pitch "wobble"/instability
WEIGHT_KEYWORD = 0.15

# --- Thresholds for tiering the final 0-1 score ---
THRESHOLD_MEDIUM = 0.35
THRESHOLD_HIGH = 0.60


def normalize(value, low_ref, high_ref):
    """Scales a raw value into a 0-1 range based on reference low/high points."""
    if high_ref == low_ref:
        return 0.0
    score = (value - low_ref) / (high_ref - low_ref)
    return float(np.clip(score, 0.0, 1.0))  # keep within 0-1 even if value is outside ref range


def compute_distress_score(pitch_mean, pitch_std, energy_mean, keyword_found):
    """
    Takes the measured audio features + whether a keyword was found,
    returns:
      - final_score (0-1 number)
      - tier ("LOW", "MEDIUM", or "HIGH")
      - explanation (dict showing each component's contribution, for transparency)
    """
    pitch_score = normalize(pitch_mean, PITCH_LOW_REF, PITCH_HIGH_REF)
    energy_score = normalize(energy_mean, ENERGY_LOW_REF, ENERGY_HIGH_REF)
    # pitch_std (wobble) - using a reasonable reference range observed in our data
    pitch_std_score = normalize(pitch_std, 50, 180)
    keyword_score = 1.0 if keyword_found else 0.0

    final_score = (
        pitch_score * WEIGHT_PITCH
        + energy_score * WEIGHT_ENERGY
        + pitch_std_score * WEIGHT_PITCH_STD
        + keyword_score * WEIGHT_KEYWORD
    )
    final_score = float(np.clip(final_score, 0.0, 1.0))

    if final_score >= THRESHOLD_HIGH:
        tier = "HIGH"
    elif final_score >= THRESHOLD_MEDIUM:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    explanation = {
        "pitch_score": round(pitch_score, 3),
        "energy_score": round(energy_score, 3),
        "pitch_std_score": round(pitch_std_score, 3),
        "keyword_score": round(keyword_score, 3),
        "final_score": round(final_score, 3),
    }

    return final_score, tier, explanation


if __name__ == "__main__":
    import pandas as pd
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    features_path = os.path.join(base_dir, "data", "features.csv")

    df = pd.read_csv(features_path)

    print("--- Running distress scoring on all real clips ---\n")
    results = []
    for _, row in df.iterrows():
        # NOTE: we don't have real keyword hits from this dataset (explained
        # earlier - RAVDESS actors never say "help"), so keyword_found=False
        # for all of these. Once you upload your own "help me" recordings,
        # we'll re-run this with real keyword detection included too.
        score, tier, explanation = compute_distress_score(
            pitch_mean=row["pitch_mean"],
            pitch_std=row["pitch_std"],
            energy_mean=row["energy_mean"],
            keyword_found=False,
        )
        results.append({
            "filename": row["filename"],
            "true_label": row["label"],
            "predicted_tier": tier,
            "score": score,
        })
        print(f"{row['filename']:25s} | true={row['label']:9s} | score={score:.3f} | tier={tier}")

    results_df = pd.DataFrame(results)
    output_path = os.path.join(base_dir, "data", "scored_results.csv")
    results_df.to_csv(output_path, index=False)
    print(f"\nSaved results to {output_path}")
