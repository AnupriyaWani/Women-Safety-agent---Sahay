# Evaluation Report

- Total clips tested: 34
- Precision: 0.87
- Recall: 0.68
- True Positives: 13
- False Positives: 2
- False Negatives: 6
- True Negatives: 13

## Missed distress clips
- real_angry_03.wav (score: 0.334)
- real_angry_04.wav (score: 0.308)
- real_angry_06.wav (score: 0.234)
- real_fearful_04.wav (score: 0.103)
- real_fearful_05.wav (score: 0.332)
- real_fearful_06.wav (score: 0.138)

## False positive clips (normal wrongly flagged)
- real_calm_08.wav (score: 0.489, tier: MEDIUM)
- real_happy_01.wav (score: 0.711, tier: HIGH)

## Key limitation observed
One false positive was a HAPPY/excited clip, not a calm one. This reveals that pitch and energy alone cannot fully distinguish extreme positive excitement from genuine distress, since both produce high pitch and high volume. A next improvement would incorporate additional signals (e.g. spectral tone quality, or context) to separate these two high-arousal emotional states.

## Honesty note
Thresholds were set using observed averages from this same dataset, so this is a first-pass evaluation, not a fully blind held-out test. A next step would be testing on a separate unseen dataset/batch.
