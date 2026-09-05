# NEXORA Mobile v0.3 — Physical Intelligence Core

This branch introduces the first real **Physical Intelligence** prototype for NEXORA.

## What is implemented
- real accelerometer input
- real gyroscope input
- foreground location
- prototype impact candidate detection
- Guardian verification UI
- Human Continuity prototype score
- explicit response states
- emergency-safe wording

## Important
This is a research prototype, not a certified emergency system.
Thresholds are placeholders and must be calibrated from controlled datasets and device-specific tests.

## Run
```bash
cd nexora-mobile
npm install
npx expo start
```

Scan the QR code using Expo Go.

## v0.4 target
1. rolling event timeline
2. adaptive baseline learning
3. fall-vs-phone-drop classification
4. inactivity-after-impact logic
5. Guardian countdown
6. Gemini voice gateway
7. offline safety protocol engine
8. hazard feed adapter interface
