"""
extract_features.py

WHAT THIS FILE DOES:
Reads every audio clip in data/distress/ and data/normal/, and measures:
  - pitch (how high/low the voice is)
  - energy/loudness (how loud the voice is)
  - pitch variability (how "shaky"/unstable the pitch is - panic tends to wobble)
  - zero-crossing rate (rough proxy for how "harsh"/noisy vs smooth a sound is)

Saves everything into one table: features.csv
This table is what we'll use in later steps to teach the computer
to tell distress apart from normal speech.
"""

import librosa
import numpy as np
import pandas as pd
import os

SAMPLE_RATE = 22050


def extract_features_from_file(filepath):
    """
    Takes one audio file, returns a dictionary of measured features.
    """
    # Load the audio file (librosa reads the sound wave into numbers)
    y, sr = librosa.load(filepath, sr=SAMPLE_RATE)

    # --- PITCH ---
    # librosa.pyin estimates the fundamental frequency (pitch) over time
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
    )
    # f0 has NaN where no pitch was detected (silence/noise) - ignore those
    f0_clean = f0[~np.isnan(f0)]

    if len(f0_clean) > 0:
        pitch_mean = float(np.mean(f0_clean))
        pitch_max = float(np.max(f0_clean))
        pitch_std = float(np.std(f0_clean))  # how much pitch wobbles/varies
    else:
        # fallback if no pitch could be detected at all (rare, e.g. very noisy clip)
        pitch_mean = 0.0
        pitch_max = 0.0
        pitch_std = 0.0

    # --- ENERGY / LOUDNESS ---
    rms = librosa.feature.rms(y=y)[0]  # root-mean-square energy, frame by frame
    energy_mean = float(np.mean(rms))
    energy_max = float(np.max(rms))

    # --- ZERO CROSSING RATE ---
    # how often the sound wave crosses zero - noisy/harsh sounds cross more often
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = float(np.mean(zcr))

    return {
        "pitch_mean": pitch_mean,
        "pitch_max": pitch_max,
        "pitch_std": pitch_std,
        "energy_mean": energy_mean,
        "energy_max": energy_max,
        "zcr_mean": zcr_mean,
    }


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    distress_dir = os.path.join(base_dir, "data", "distress")
    normal_dir = os.path.join(base_dir, "data", "normal")

    rows = []

    # Process distress clips
    for fname in sorted(os.listdir(distress_dir)):
        if fname.endswith(".wav"):
            filepath = os.path.join(distress_dir, fname)
            print(f"Processing (distress): {fname}")
            features = extract_features_from_file(filepath)
            features["filename"] = fname
            features["label"] = "distress"
            rows.append(features)

    # Process normal clips
    for fname in sorted(os.listdir(normal_dir)):
        if fname.endswith(".wav"):
            filepath = os.path.join(normal_dir, fname)
            print(f"Processing (normal): {fname}")
            features = extract_features_from_file(filepath)
            features["filename"] = fname
            features["label"] = "normal"
            rows.append(features)

    df = pd.DataFrame(rows)
    output_path = os.path.join(base_dir, "data", "features.csv")
    df.to_csv(output_path, index=False)

    print(f"\nSaved {len(df)} rows to {output_path}")
    print("\n--- SANITY CHECK: average feature values per label ---")
    print(df.groupby("label")[["pitch_mean", "pitch_std", "energy_mean", "zcr_mean"]].mean())


if __name__ == "__main__":
    main()
