"""
transcribe.py

WHAT THIS FILE DOES:
Converts each audio clip into text (speech-to-text), so we can later
check the text for distress words like "help", "stop", "bachao", etc.

IMPORTANT NOTE ON WHICH ENGINE IS USED:
- WHISPER (by OpenAI) is the accurate, recommended engine for this project.
  It needs to download a model file (~150 MB for the 'base' model) the FIRST
  time you run it - this requires normal internet access.
- This sandbox environment has restricted internet and cannot download
  Whisper's model, so a fallback (pocketsphinx, offline, lower accuracy)
  is used automatically ONLY when Whisper is unavailable.
- On your own laptop, Whisper will download fine and give much better results.
  No code changes needed - it auto-detects which is available.
"""

import os
import pandas as pd

USE_WHISPER = True
whisper_model = None

try:
    import whisper
    whisper_model = whisper.load_model("base")
    print("Using Whisper (accurate mode).")
except Exception as e:
    USE_WHISPER = False
    print("Whisper unavailable in this environment (likely no internet to download model).")
    print("Falling back to offline pocketsphinx (lower accuracy, but works without internet).")
    import speech_recognition as sr


def transcribe_file(filepath):
    """
    Takes an audio file path, returns the transcribed text (lowercase).
    Automatically uses Whisper if available, else falls back to pocketsphinx.
    """
    if USE_WHISPER:
        result = whisper_model.transcribe(filepath)
        return result["text"].strip().lower()
    else:
        r = sr.Recognizer()
        with sr.AudioFile(filepath) as source:
            audio = r.record(source)
        try:
            text = r.recognize_sphinx(audio)
            return text.strip().lower()
        except sr.UnknownValueError:
            return ""  # couldn't understand any speech in the clip


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    distress_dir = os.path.join(base_dir, "data", "distress")
    normal_dir = os.path.join(base_dir, "data", "normal")

    rows = []

    for folder, label in [(distress_dir, "distress"), (normal_dir, "normal")]:
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".wav"):
                filepath = os.path.join(folder, fname)
                print(f"Transcribing ({label}): {fname}")
                text = transcribe_file(filepath)
                print(f"   -> \"{text}\"")
                rows.append({"filename": fname, "label": label, "transcript": text})

    df = pd.DataFrame(rows)
    output_path = os.path.join(base_dir, "data", "transcripts.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} transcripts to {output_path}")


if __name__ == "__main__":
    main()
