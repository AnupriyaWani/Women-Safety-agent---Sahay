# Women's Safety AI Agent
### Razorpay AI Buildathon — Open Track Submission

## The Problem
Women often face situations where they need help but can't safely reach for a phone,
press buttons, or speak clearly. Existing safety apps rely on manual triggers (buttons,
apps to open), which don't work when hands are occupied, or when speaking loudly is risky.

## Our Approach
An AI agent that detects genuine vocal distress — through voice pitch, loudness, and
distress keywords (English + Hindi) — and automatically alerts emergency contacts with
location, an SMS, and an automated phone call carrying a loud alarm sound. Designed with
a tiered response (LOW/MEDIUM/HIGH) to avoid false alarms while still catching real danger.

## How It Works (Pipeline)
```
Audio input
   -> Speech-to-text (Whisper)          -> Keyword check (English + Hindi)
   -> Audio feature extraction (librosa) -> Pitch / energy / pitch-stability analysis
   -> Combined into a Distress Score (0-1)
   -> Tiered decision: LOW / MEDIUM / HIGH
   -> HIGH: SMS + automated siren call to emergency contacts, logged to audit trail
   -> MEDIUM: soft check-in notification first
   -> LOW: no action, logged only
```

See `architecture.png` for a visual diagram.

## Real Results (Honest Evaluation)
Tested on 23 real labeled voice clips (RAVDESS dataset — 12 distress, 11 normal):

- **Precision: 1.00** — every alert we raised was genuine distress (zero false alarms)
- **Recall: 0.50** — we caught half of all real distress clips; the missed cases were
  subtler/quieter emotional deliveries
- Full breakdown in `data/evaluation_report.md`, including exact filenames of missed clips

This is a deliberate first-pass trade-off: we prioritized **not crying wolf** over
catching every case, since false alarms erode user trust. Next step: expand the dataset
and carefully lower thresholds to improve recall without increasing false positives.

## What We Built (Tier 1 — Core)
- [x] Audio feature extraction (pitch, energy, pitch stability)
- [x] Speech-to-text (Whisper, with offline fallback)
- [x] Distress keyword detection (English + Hindi/Hinglish)
- [x] Tiered distress scoring (LOW / MEDIUM / HIGH)
- [x] Honest evaluation (precision/recall on real audio)
- [x] Alert action — SMS + automated alarm call (via Twilio)
- [x] Full audit trail logging
- [x] Graceful failure handling (no internet, corrupted files, borderline scores)

## What's Simulated vs Real
- **Real:** all audio analysis, scoring logic, evaluation numbers, logging
- **Real (once Twilio configured):** actual SMS + phone calls
- **Simulated for this demo:** wake-word/volume-button trigger (would need native phone
  integration), real police-station auto-dispatch (kept human-in-the-loop by design —
  see Privacy & Safety section)

## Privacy & Safety Design
- No audio is processed until the agent is actively triggered — not always-listening
- Audio is processed and discarded unless a genuine alert fires
- Emergency contacts are explicitly added by the user with their knowledge
- Police escalation is intentionally NOT fully automatic — high false-positive risk
  in an emergency-dispatch context is a real danger, not just an inconvenience; our
  design uses a grace/confirmation window before any such escalation

## Tech Stack
Python, librosa (audio features), Whisper (speech-to-text), scikit-learn-ready scoring
pipeline, Twilio (SMS/calls), pandas (data handling)

## How to Run
```bash
pip install -r requirements.txt
python src/extract_features.py     # analyze audio -> data/features.csv
python src/distress_score.py       # score all clips -> data/scored_results.csv
python tests/evaluate.py           # get precision/recall numbers
python tests/failure_handling.py   # run failure-handling test suite
python src/alert_action.py         # test alert sending (simulated unless Twilio configured)
```

## What We'd Build Next
- Native mobile wake-word + volume-button trigger integration
- Larger, more diverse training dataset (target 200+ clips, including real distress speech)
- Fake-call feature, unsafe-area warnings, "safe walk" timer mode
- Formal legal/consent review for evidence-recording features
