# PhaseShift

A circadian jet lag planner in the same product shape as [Timeshifter](https://www.timeshifter.com/jet-lag-app): you enter sleep timing, chronotype, and an itinerary, and you get an hour-by-hour plan for **light, darkness, sleep, melatonin, and caffeine**.

PhaseShift is not affiliated with Timeshifter. Timing is based on published human phase response curves (St Hilaire et al. 2012; Eastman & Burgess 2009), not a reverse-engineered commercial algorithm.

## Run locally

```bash
cd phaseshift
npm install
npm test
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## What it does

- Estimates core body temperature minimum from usual bedtime, wake time, and chronotype
- Measures the timezone jump at each landing (including DST) and picks eastbound advance vs westbound delay
- Shifts the clock in daily steps, placing seek-light / avoid-light windows around that day’s CBTmin
- Optionally times a 0.5 mg melatonin microdose for eastbound trips and caffeine cutoffs before sleep
- Pre-travel adjustment, stopovers, round trips, and short-trip mode (stay closer to home time on brief stays)
- 3-hour “what now” view plus a full timeline, with a preview scrubber so you can walk the plan

Plans are stored in the browser (`localStorage`). There is also `POST /api/plan` if you want the same engine over HTTP.

## Not medical advice

For healthy adults 18+. Do not use melatonin, restriction of light, or sleep shifting as a substitute for clinical care.
