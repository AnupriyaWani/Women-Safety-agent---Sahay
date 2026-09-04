"""
evaluate.py

WHAT THIS FILE DOES:
Calculates real, honest performance numbers for our distress detector:
  - Precision: of everything we FLAGGED as distress, how much was really distress?
  - Recall: of everything that WAS really distress, how much did we catch?
  - False positives: normal clips we wrongly flagged (worst for user trust)
  - False negatives: real distress clips we missed (worst for actual safety)

IMPORTANT HONESTY NOTE (read this - it matters for your pitch):
Our reference ranges (PITCH_LOW_REF/HIGH_REF etc in distress_score.py) were
set by looking at averages across this SAME dataset. That means this isn't
a perfectly "blind" held-out test - it's a reasonable first-pass evaluation.
For your final submission, the honest framing is:
  "thresholds were set using observed patterns in our data; a stricter
   held-out validation with more data is a clear next step."
This is completely normal for an early-stage prototype and is a better
thing to say than pretending this was a perfect blind test.
"""

import pandas as pd
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scored_path = os.path.join(base_dir, "data", "scored_results.csv")
    df = pd.read_csv(scored_path)

    # We treat MEDIUM or HIGH as "flagged" (the system takes SOME action -
    # either a soft check-in for MEDIUM, or a full alert for HIGH).
    # LOW means "system stayed quiet."
    df["flagged"] = df["predicted_tier"].isin(["MEDIUM", "HIGH"])
    df["actually_distress"] = df["true_label"] == "distress"

    true_positives = ((df["flagged"]) & (df["actually_distress"])).sum()
    false_positives = ((df["flagged"]) & (~df["actually_distress"])).sum()
    false_negatives = ((~df["flagged"]) & (df["actually_distress"])).sum()
    true_negatives = ((~df["flagged"]) & (~df["actually_distress"])).sum()

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

    print("=== EVALUATION RESULTS (honest numbers) ===\n")
    print(f"Total clips tested: {len(df)}")
    print(f"  - Real distress clips: {df['actually_distress'].sum()}")
    print(f"  - Real normal clips:   {(~df['actually_distress']).sum()}")
    print()
    print(f"True Positives  (correctly flagged distress): {true_positives}")
    print(f"False Positives (normal wrongly flagged):      {false_positives}")
    print(f"False Negatives (distress we MISSED):          {false_negatives}")
    print(f"True Negatives  (normal correctly left alone):  {true_negatives}")
    print()
    print(f"PRECISION: {precision:.2f}  (of everything we flagged, {precision*100:.0f}% was real distress)")
    print(f"RECALL:    {recall:.2f}  (of all real distress, we caught {recall*100:.0f}%)")
    print()

    # Show exactly which distress clips were missed, by name - full transparency
    missed = df[(df["actually_distress"]) & (~df["flagged"])]
    if len(missed) > 0:
        print("--- Missed distress clips (honest exception list) ---")
        for _, row in missed.iterrows():
            print(f"  {row['filename']}  (score: {row['score']:.3f})")

    # Show exactly which normal clips were wrongly flagged - equally important to disclose
    false_alarms = df[(~df["actually_distress"]) & (df["flagged"])]
    if len(false_alarms) > 0:
        print("\n--- False positive clips (normal wrongly flagged) ---")
        for _, row in false_alarms.iterrows():
            print(f"  {row['filename']}  (score: {row['score']:.3f}, tier: {row['predicted_tier']})")

    # Save a small report file
    report_path = os.path.join(base_dir, "data", "evaluation_report.md")
    with open(report_path, "w") as f:
        f.write("# Evaluation Report\n\n")
        f.write(f"- Total clips tested: {len(df)}\n")
        f.write(f"- Precision: {precision:.2f}\n")
        f.write(f"- Recall: {recall:.2f}\n")
        f.write(f"- True Positives: {true_positives}\n")
        f.write(f"- False Positives: {false_positives}\n")
        f.write(f"- False Negatives: {false_negatives}\n")
        f.write(f"- True Negatives: {true_negatives}\n\n")
        f.write("## Missed distress clips\n")
        for _, row in missed.iterrows():
            f.write(f"- {row['filename']} (score: {row['score']:.3f})\n")
        f.write("\n## False positive clips (normal wrongly flagged)\n")
        for _, row in false_alarms.iterrows():
            f.write(f"- {row['filename']} (score: {row['score']:.3f}, tier: {row['predicted_tier']})\n")
        f.write("\n## Key limitation observed\n")
        f.write(
            "One false positive was a HAPPY/excited clip, not a calm one. This reveals that "
            "pitch and energy alone cannot fully distinguish extreme positive excitement from "
            "genuine distress, since both produce high pitch and high volume. A next improvement "
            "would incorporate additional signals (e.g. spectral tone quality, or context) to "
            "separate these two high-arousal emotional states.\n")
        f.write("\n## Honesty note\n")
        f.write(
            "Thresholds were set using observed averages from this same dataset, "
            "so this is a first-pass evaluation, not a fully blind held-out test. "
            "A next step would be testing on a separate unseen dataset/batch.\n"
        )

    print(f"\nSaved full report to {report_path}")


if __name__ == "__main__":
    main()
