# PhaseShift

A circadian jet lag planner in the same product shape as an iPhone travel-sleep app: you pick From / To, flight times, and usual sleep, then follow a day-by-day checklist for **sleep, light, caffeine, and optional melatonin**.

PhaseShift is not affiliated with Jet Lag Bye or Timeshifter. Timing is based on published human phase response curves (St Hilaire et al. 2012; Eastman & Burgess 2009), not a reverse-engineered commercial algorithm.

## Run locally

```bash
cd phaseshift
npm install
npm test
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The UI is iPhone-width.

## What it does

- Home composer: airport From / To, one-way or round trip, usual bedtime and wake, melatonin and caffeine toggles
- Personalized plan: target sleep and wake, seek / avoid bright light, caffeine cutoff, optional 0.5 mg melatonin
- Built to follow: circular checkboxes, day chips (D-n / Travel / D+n), saved history, optional reminders, light or dark mode
- Reset Sleep: recover a drifted schedule without a flight
- Short-trip mode in the advanced itinerary: stay closer to home time on brief stays

Plans are stored in the browser (`localStorage`). There is also `POST /api/plan` if you want the same engine over HTTP.

## Not medical advice

For healthy adults 18+. Do not use melatonin, restriction of light, or sleep shifting as a substitute for clinical care.
