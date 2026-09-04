"""
generate_sample_data.py

WHY THIS FILE EXISTS:
We don't have internet access here to download the real RAVDESS dataset.
So we generate FAKE but STRUCTURALLY SIMILAR audio clips:
  - "distress" clips = loud + high-pitched + shaky (mimics screaming/panic)
  - "normal" clips   = quieter + steady pitch (mimics calm talking)

This lets us build and test the ENTIRE pipeline right now.
Later, you'll drop in real RAVDESS .wav files into data/distress/ and
data/normal/ using the SAME filenames pattern, and nothing else changes.
"""

import numpy as np
import soundfile as sf
import os

SAMPLE_RATE = 22050  # standard sample rate librosa expects
DURATION = 3  # seconds per clip

def generate_distress_clip(seed):
    """Simulates a panicked/loud/high-pitched voice-like signal."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION))

    # High, unstable pitch (simulates panicked voice) - frequency wobbles a lot
    base_freq = rng.uniform(350, 500)  # higher pitch
    wobble = np.sin(2 * np.pi * 5 * t) * rng.uniform(40, 80)  # shaky/unstable
    freq = base_freq + wobble

    # Loud amplitude (simulates shouting) with sharp bursts
    amplitude = rng.uniform(0.7, 0.95)
    bursts = np.abs(np.sin(2 * np.pi * rng.uniform(2, 4) * t)) 

    signal = amplitude * bursts * np.sin(2 * np.pi * freq * t)

    # Add noise (simulates chaotic environment)
    noise = rng.normal(0, 0.05, signal.shape)
    signal = signal + noise

    return np.clip(signal, -1, 1)


def generate_normal_clip(seed):
    """Simulates calm, steady speaking voice-like signal."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION))

    # Lower, stable pitch (calm voice)
    base_freq = rng.uniform(120, 220)
    freq = base_freq + np.sin(2 * np.pi * 0.5 * t) * 5  # very slight natural wobble

    # Quieter, steady amplitude
    amplitude = rng.uniform(0.15, 0.3)
    signal = amplitude * np.sin(2 * np.pi * freq * t)

    # Small natural noise
    noise = rng.normal(0, 0.01, signal.shape)
    signal = signal + noise

    return np.clip(signal, -1, 1)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    distress_dir = os.path.join(base_dir, "data", "distress")
    normal_dir = os.path.join(base_dir, "data", "normal")

    os.makedirs(distress_dir, exist_ok=True)
    os.makedirs(normal_dir, exist_ok=True)

    n_clips = 20  # 20 distress + 20 normal = 40 total placeholder clips

    for i in range(n_clips):
        distress_audio = generate_distress_clip(seed=i)
        sf.write(os.path.join(distress_dir, f"distress_{i:02d}.wav"), distress_audio, SAMPLE_RATE)

        normal_audio = generate_normal_clip(seed=i + 100)
        sf.write(os.path.join(normal_dir, f"normal_{i:02d}.wav"), normal_audio, SAMPLE_RATE)

    print(f"Created {n_clips} distress clips in: {distress_dir}")
    print(f"Created {n_clips} normal clips in: {normal_dir}")
    print("Done. These are PLACEHOLDER clips - swap with real recordings later.")


if __name__ == "__main__":
    main()
