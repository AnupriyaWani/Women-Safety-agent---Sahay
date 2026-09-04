"""
wake_word_detector.py

WHAT THIS FILE DOES:
Listens for a specific wake word (e.g. "Hey Xyz") to activate the agent -
the same technique used by "Hey Siri" or "OK Google". This is a narrow,
lightweight, ALWAYS-ON detector that does ONE thing: recognize one short
phrase. It does NOT transcribe or understand anything else being said -
that's what makes it privacy-respecting (see README privacy section).

WHY PORCUPINE:
Porcupine (by Picovoice) is a real, free, industry-standard tool for
exactly this. It needs a free "AccessKey" from picovoice.ai (same idea
as Twilio's account keys - free signup, no cost for small-scale use).

HOW TO GET IT WORKING FOR REAL:
  1. Sign up free at https://console.picovoice.ai
  2. Create an AccessKey (free tier)
  3. (Optional but recommended) Train a CUSTOM wake word there (e.g. "Hey Xyz")
     - their console lets you type a phrase and generates a model file for it
  4. Put your AccessKey below, and the custom model file path if you made one

UNTIL configured, this runs in SIMULATION MODE: instead of listening to a
live microphone (which needs real hardware + real audio, not available in
this environment), it checks a given transcript/text for the wake phrase -
enough to prove the ACTIVATION LOGIC works correctly. On your own laptop
with a microphone, this would run continuously on live audio instead.
"""

import os

PICOVOICE_ACCESS_KEY = os.environ.get("PICOVOICE_ACCESS_KEY", "")
WAKE_WORD = "hey xyz"  # replace "xyz" with your chosen agent name

SIMULATION_MODE = not PICOVOICE_ACCESS_KEY


def check_wake_word_in_text(text):
    """
    SIMULATION MODE version: checks if the wake word appears in a piece
    of text (e.g. a transcript). Used for testing the activation logic
    without live microphone hardware.
    """
    return WAKE_WORD in text.lower().strip()


def listen_live_for_wake_word():
    """
    REAL MODE version: would run continuously on live microphone audio
    using Porcupine, and call agent_activate() the instant it hears the
    wake word. This only runs once PICOVOICE_ACCESS_KEY is set, since it
    needs real audio hardware input (a live microphone), which isn't
    available in this sandboxed code-execution environment.
    """
    import pvporcupine
    import pyaudio
    import struct

    porcupine = pvporcupine.create(access_key=PICOVOICE_ACCESS_KEY, keywords=["hey google"])
    # NOTE: swap "hey google" for a built-in keyword, or point keyword_paths=[...]
    # to your custom-trained "Hey Xyz" model file from the Picovoice console.

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("Listening live for wake word... (Ctrl+C to stop)")
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm)
            if result >= 0:
                print("WAKE WORD DETECTED - activating agent!")
                agent_activate()
    except KeyboardInterrupt:
        pass
    finally:
        audio_stream.close()
        porcupine.delete()


def agent_activate():
    """
    Called the instant the wake word is detected. This is where the full
    listening/distress-analysis pipeline (Parts 3-9) would kick in.
    """
    print(">>> AGENT ACTIVATED - starting full distress analysis pipeline <<<")
    # In the full integration, this would call:
    #   1. record a rolling audio buffer
    #   2. extract_features.py + transcribe.py + keyword_check.py
    #   3. distress_score.py -> tier decision
    #   4. alert_action.py if tier == HIGH


if __name__ == "__main__":
    print(f"Wake word configured: '{WAKE_WORD}'")
    print(f"Mode: {'SIMULATION (no Picovoice key set)' if SIMULATION_MODE else 'LIVE (Picovoice configured)'}\n")

    if SIMULATION_MODE:
        # Test the activation logic with example transcripts
        test_inputs = [
            "hey xyz someone is following me",
            "just talking normally about my day",
            "wait hey xyz please help",
            "hello how are you today",
        ]
        for text in test_inputs:
            triggered = check_wake_word_in_text(text)
            print(f"Input: \"{text}\"")
            if triggered:
                print("   -> WAKE WORD DETECTED")
                agent_activate()
            else:
                print("   -> no wake word, staying idle")
            print()
    else:
        listen_live_for_wake_word()
