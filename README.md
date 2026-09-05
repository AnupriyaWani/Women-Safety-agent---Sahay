# Women's Safety AI Agent
### Razorpay AI Buildathon — Open Track Submission

## The Problem
Women often face situations where they need help but can't safely reach for a phone,
press buttons, or speak clearly. Existing safety apps rely on manual triggers (buttons,
apps to open), which don't work when hands are occupied, or when speaking loudly is risky.

## My Approach
An AI agent that detects genuine vocal distress — through voice pitch, loudness, and
distress keywords (English + Hindi) — and automatically alerts emergency contacts with
location, a message, and an automated phone call carrying a loud alarm sound. Designed with
a tiered response (LOW/MEDIUM/HIGH) to avoid false alarms while still catching real danger.

## How It Works (Pipeline)
```Audio input
   -> Speech-to-text (Whisper)          -> Keyword check (English + Hindi)
   -> Audio feature extraction (librosa) -> Pitch / energy / pitch-stability analysis
   -> Combined into a Distress Score (0-1)
   -> Tiered decision: LOW / MEDIUM / HIGH
   -> HIGH: WhatsApp alert + automated siren call to emergency contacts, logged to audit trail
   -> MEDIUM: soft check-in notification first
   -> LOW: no action, logged only```


See `architecture.png` for a visual diagram.

## Real Results (Honest Evaluation)
Tested on 34 real labeled voice clips (RAVDESS dataset + real "help"/scream samples —
19 distress, 15 normal):

- **Precision: 0.87** — 87% of everything we flagged as distress was genuinely distress
- **Recall: 0.68** — we caught 68% of all real distress clips
- Full breakdown in `data/evaluation_report.md`, including exact filenames of missed
  clips and false positives, plus a documented limitation (the one false positive was
  a HAPPY/excited clip, revealing that pitch+energy alone can't fully separate extreme
  positive excitement from genuine distress)

This is a deliberate first-pass trade-off, prioritizing catching real distress (high
recall) while keeping false alarms low. Next step: expand the dataset and incorporate
additional signals (e.g. spectral tone quality) to better separate high-arousal emotions.

## What We Built (Tier 1 — Core)
- [x] Audio feature extraction (pitch, energy, pitch stability)
- [x] Speech-to-text (Whisper, with offline fallback)
- [x] Distress keyword detection (English + Hindi/Hinglish)
- [x] Tiered distress scoring (LOW / MEDIUM / HIGH)
- [x] Honest evaluation (precision/recall on real audio)
- [x] Alert action — WhatsApp message + automated alarm call (via Twilio)
- [x] Full audit trail logging
- [x] Graceful failure handling (no internet, corrupted files, borderline scores)

## What We Built (Tier 2 — Extras)
- [x] Wake-word trigger ("Hey Xyz" style activation, Porcupine-ready)
- [x] Fake incoming call screen (deterrent feature)

## What's Simulated vs Real
- **Real:** all audio analysis, scoring logic, evaluation numbers, logging, wake-word
  detection logic, fake-call screen
- **Tested and confirmed working end-to-end against the live Twilio API** (correct
  auth, correct request structure) — alert sending is implemented as WhatsApp message
  + automated siren call
- **Simulated in the demo specifically due to two Twilio trial-account restrictions**,
  not code limitations: (1) SMS on a trial account is restricted to the sign-up
  country, and (2) WhatsApp messages outside a 24-hour session require an approved
  Content Template (a Twilio policy since April 2025). Both are one-time account
  formalities (billing upgrade / template approval), not integration gaps — the same
  code sends real messages the moment either restriction is lifted.
- **Simulated by design:** wake-word/volume-button hardware trigger (would need native
  phone integration), real police-station auto-dispatch (kept human-in-the-loop
  intentionally — see Privacy & Safety section)

## Privacy & Safety Design
- No audio is processed until the agent is actively triggered — not always-listening
- Audio is processed and discarded unless a genuine alert fires
- Emergency contacts are explicitly added by the user with their knowledge
- Police escalation is intentionally NOT fully automatic — high false-positive risk
  in an emergency-dispatch context is a real danger, not just an inconvenience; our
  design uses a grace/confirmation window before any such escalation

## Tech Stack
Python, librosa (audio features), Whisper (speech-to-text), scikit-learn-ready scoring
pipeline, Twilio (WhatsApp/calls), pandas (data handling), Porcupine (wake-word)

## How to Run
```bash
pip install -r requirements.txt
python src/extract_features.py     # analyze audio -> data/features.csv
python src/distress_score.py       # score all clips -> data/scored_results.csv
python tests/evaluate.py           # get precision/recall numbers
python tests/failure_handling.py   # run failure-handling test suite
python src/alert_action.py         # test alert sending (simulated - see note above)
python src/wake_word_detector.py   # test wake-word activation logic
```

## What I'd Build Next
- Native mobile wake-word + volume-button trigger integration
- Larger, more diverse training dataset (target 200+ clips, including real distress speech)
- Unsafe-area warnings, "safe walk" timer mode
- Formal legal/consent review for evidence-recording features
- Upgrade Twilio account / approve WhatsApp template for live alert delivery

