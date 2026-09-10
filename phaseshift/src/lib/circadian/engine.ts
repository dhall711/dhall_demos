import { DateTime } from "luxon";
import { requireAirport, type Airport } from "@/lib/airports";
import type {
  Chronotype,
  EventKind,
  FlightInput,
  GeneratedPlan,
  PlanEvent,
  PlanInput,
  PhaseAnchor,
  Practicality,
  Preferences,
  SleepProfile,
  TripSegment,
} from "@/lib/circadian/types";

type ResolvedFlight = {
  id: string;
  origin: Airport;
  dest: Airport;
  departUtc: DateTime;
  arriveUtc: DateTime;
};

type Place = {
  tz: string;
  label: string;
  kind: "city" | "flight";
  iata: string;
};

type Interval = { start: DateTime; end: DateTime };

export function minutesFromHm(hm: string): number {
  const [hours, minutes] = hm.split(":").map(Number);
  if (!Number.isFinite(hours) || !Number.isFinite(minutes)) {
    throw new Error(`Invalid time ${hm}`);
  }
  return hours * 60 + minutes;
}

export function sleepDurationHours(profile: SleepProfile): number {
  const bed = minutesFromHm(profile.bedtime);
  const wake = minutesFromHm(profile.waketime);
  return ((wake - bed + 1440) % 1440) / 60;
}

export function cbtMinHoursBeforeWake(chronotype: Chronotype): number {
  if (chronotype === "early") return 2;
  if (chronotype === "late") return 3;
  return 2.5;
}

export function normalizePhaseHours(hours: number): number {
  let value = hours;
  while (value > 12) value -= 24;
  while (value <= -12) value += 24;
  return Math.round(value * 100) / 100;
}

/** Delay-positive hours the body clock should move to match dest local time. */
export function targetPhaseHours(homeTz: string, destTz: string, atUtc: DateTime): number {
  const homeOffset = atUtc.setZone(homeTz).offset / 60;
  const destOffset = atUtc.setZone(destTz).offset / 60;
  return normalizePhaseHours(homeOffset - destOffset);
}

export function directionFromPhase(phaseHours: number): "east" | "west" | "none" {
  if (phaseHours <= -0.75) return "east";
  if (phaseHours >= 0.75) return "west";
  return "none";
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function roundDateTime(dt: DateTime, incrementMin: number): DateTime {
  const base = dt.set({ second: 0, millisecond: 0 });
  if (incrementMin <= 1) return base;
  const minutes = base.minute;
  const rounded = Math.round(minutes / incrementMin) * incrementMin;
  return base.startOf("hour").plus({ minutes: rounded });
}

function incrementFor(practicality: Practicality): number {
  if (practicality === "easy") return 30;
  if (practicality === "strict") return 5;
  return 15;
}

function minWindowMinutes(practicality: Practicality): number {
  if (practicality === "easy") return 40;
  if (practicality === "strict") return 20;
  return 25;
}

function maxDailyStep(deltaSign: number, preferences: Preferences): number {
  const melatonin = preferences.useMelatonin;
  let advance = melatonin ? 1.5 : 1;
  let delay = melatonin ? 1.75 : 1.5;
  if (preferences.practicality === "easy") {
    advance -= 0.25;
    delay -= 0.25;
  }
  if (preferences.practicality === "strict") {
    advance += 0.25;
    delay += 0.25;
  }
  return deltaSign < 0 ? advance : delay;
}

function caffeineCutoffHours(practicality: Practicality): number {
  return practicality === "easy" ? 10 : 8;
}

function preShiftDaysFor(absShift: number, practicality: Practicality): number {
  if (absShift < 2) return 0;
  if (practicality === "easy") return 1;
  if (practicality === "strict") return Math.min(3, Math.ceil(absShift / 2));
  return Math.min(2, Math.ceil(absShift / 2.5));
}

function resolveFlights(flights: FlightInput[]): ResolvedFlight[] {
  if (flights.length === 0) {
    throw new Error("Add at least one flight.");
  }
  const resolved = flights.map((flight) => {
    const origin = requireAirport(flight.originIata);
    const dest = requireAirport(flight.destinationIata);
    const departUtc = DateTime.fromISO(flight.departLocal, { zone: origin.tz });
    const arriveUtc = DateTime.fromISO(flight.arriveLocal, { zone: dest.tz });
    if (!departUtc.isValid) {
      throw new Error(`Invalid departure time for ${origin.iata}`);
    }
    if (!arriveUtc.isValid) {
      throw new Error(`Invalid arrival time for ${dest.iata}`);
    }
    if (arriveUtc <= departUtc) {
      throw new Error(
        `${origin.iata} → ${dest.iata} arrives before it departs. Check time zones and dates.`,
      );
    }
    return { id: flight.id, origin, dest, departUtc, arriveUtc };
  });
  return resolved.sort((a, b) => a.departUtc.toMillis() - b.departUtc.toMillis());
}

function stayHoursAfter(flights: ResolvedFlight[], index: number): number {
  const next = flights[index + 1];
  if (!next) return Number.POSITIVE_INFINITY;
  return next.departUtc.diff(flights[index].arriveUtc, "hours").hours;
}

function applyShortTrip(
  fullTarget: number,
  stayHours: number,
  enabled: boolean,
): { target: number; shortTrip: boolean } {
  if (!enabled || !Number.isFinite(stayHours) || stayHours >= 96) {
    return { target: fullTarget, shortTrip: false };
  }
  if (stayHours < 48) {
    return { target: 0, shortTrip: true };
  }
  const scaled = clamp(fullTarget * 0.4, -3, 3);
  return { target: normalizePhaseHours(scaled), shortTrip: true };
}

function locationAt(flights: ResolvedFlight[], home: Airport, at: DateTime): Place {
  if (at < flights[0].departUtc) {
    return {
      tz: flights[0].origin.tz,
      label: flights[0].origin.city,
      kind: "city",
      iata: flights[0].origin.iata,
    };
  }
  for (let i = 0; i < flights.length; i += 1) {
    const flight = flights[i];
    if (at >= flight.departUtc && at < flight.arriveUtc) {
      const midpoint = flight.departUtc.plus({
        milliseconds: flight.arriveUtc.diff(flight.departUtc).as("milliseconds") / 2,
      });
      return {
        tz: at < midpoint ? flight.origin.tz : flight.dest.tz,
        label: `${flight.origin.iata} → ${flight.dest.iata}`,
        kind: "flight",
        iata: flight.dest.iata,
      };
    }
    const next = flights[i + 1];
    if (at >= flight.arriveUtc && (!next || at < next.departUtc)) {
      return {
        tz: flight.dest.tz,
        label: flight.dest.city,
        kind: "city",
        iata: flight.dest.iata,
      };
    }
  }
  return { tz: home.tz, label: home.city, kind: "city", iata: home.iata };
}

function targetAtTime(
  flights: ResolvedFlight[],
  home: Airport,
  preferences: Preferences,
  at: DateTime,
): number {
  const upcoming = flights.find((flight) => at < flight.arriveUtc) ?? flights[flights.length - 1];
  const index = flights.indexOf(upcoming);
  const full = targetPhaseHours(home.tz, upcoming.dest.tz, upcoming.arriveUtc);
  const stay = stayHoursAfter(flights, index);
  return applyShortTrip(full, stay, preferences.shortTripMode).target;
}

function cbtMinOnHomeDate(
  date: DateTime,
  homeTz: string,
  profile: SleepProfile,
): DateTime {
  const wakeMinutes = minutesFromHm(profile.waketime);
  const cbtMinutes =
    (wakeMinutes - cbtMinHoursBeforeWake(profile.chronotype) * 60 + 1440) % 1440;
  return date.setZone(homeTz).startOf("day").plus({ minutes: cbtMinutes });
}

function overlaps(a: Interval, b: Interval): boolean {
  return a.start < b.end && a.end > b.start;
}

function clipOutside(window: Interval, blocked: Interval[]): Interval[] {
  let pieces: Interval[] = [window];
  for (const block of blocked) {
    const next: Interval[] = [];
    for (const piece of pieces) {
      if (!overlaps(piece, block)) {
        next.push(piece);
        continue;
      }
      if (piece.start < block.start) {
        next.push({ start: piece.start, end: DateTime.min(piece.end, block.start) });
      }
      if (piece.end > block.end) {
        next.push({ start: DateTime.max(piece.start, block.end), end: piece.end });
      }
    }
    pieces = next;
  }
  return pieces.filter((piece) => piece.end > piece.start);
}

function durationMinutes(interval: Interval): number {
  return interval.end.diff(interval.start, "minutes").minutes;
}

let eventCounter = 0;

function pushEvent(
  events: PlanEvent[],
  kind: EventKind,
  interval: Interval,
  place: Place,
  title: string,
  detail: string,
  minMinutes: number,
  increment: number,
): void {
  const start = roundDateTime(interval.start, increment);
  const end = roundDateTime(interval.end, increment);
  if (end <= start) return;
  if (end.diff(start, "minutes").minutes < minMinutes) return;
  eventCounter += 1;
  events.push({
    id: `${kind}-${start.toUTC().toISO()}-${eventCounter}`,
    kind,
    startUtc: start.toUTC().toISO() ?? start.toUTC().toString(),
    endUtc: end.toUTC().toISO() ?? end.toUTC().toString(),
    title,
    detail,
    place: place.label,
    timezone: place.tz,
    inFlight: place.kind === "flight",
  });
}

function seekCopy(inFlight: boolean, direction: "east" | "west" | "none"): string {
  if (inFlight) {
    return direction === "east"
      ? "Stay awake if you can. Window shade up, skip the eye mask — this light is shifting you east."
      : "Stay awake if you can. Window shade up. Evening-type light now delays your clock westward.";
  }
  return "Get outdoors or sit by a bright window. Skip sunglasses. Light is the main cue that resets your clock.";
}

function avoidCopy(inFlight: boolean, practicality: Practicality): string {
  const extra =
    practicality === "easy"
      ? "Dim screens and cabin lights if you can."
      : "Wear dark sunglasses if you must go outside. Dim indoor lighting and use an eye mask to sleep.";
  if (inFlight) {
    return `Window shade down, eye mask on. Cabin lighting is often timed wrong. ${extra}`;
  }
  return `Avoid bright light — it would push your clock the wrong way. ${extra}`;
}

export function generatePlan(input: PlanInput): GeneratedPlan {
  eventCounter = 0;
  const home = requireAirport(input.homeIata);
  const flights = resolveFlights(input.flights);
  const { profile, preferences } = input;
  const sleepHours = sleepDurationHours(profile);
  if (sleepHours < 4 || sleepHours > 12) {
    throw new Error("Sleep window should be between 4 and 12 hours.");
  }
  const wakeAfterCbt = cbtMinHoursBeforeWake(profile.chronotype);
  const increment = incrementFor(preferences.practicality);
  const minMinutes = minWindowMinutes(preferences.practicality);

  const segments: TripSegment[] = flights.map((flight, index) => {
    const full = targetPhaseHours(home.tz, flight.dest.tz, flight.arriveUtc);
    const stay = stayHoursAfter(flights, index);
    const { target, shortTrip } = applyShortTrip(full, stay, preferences.shortTripMode);
    const shiftHours = -full;
    return {
      originIata: flight.origin.iata,
      destinationIata: flight.dest.iata,
      originCity: flight.origin.city,
      destinationCity: flight.dest.city,
      direction: directionFromPhase(full),
      shiftHours,
      targetPhaseHours: target,
      shortTrip,
      departUtc: flight.departUtc.toUTC().toISO() ?? flight.departUtc.toUTC().toString(),
      arriveUtc: flight.arriveUtc.toUTC().toISO() ?? flight.arriveUtc.toUTC().toString(),
    };
  });

  const firstTarget = segments[0].targetPhaseHours;
  const absFirst = Math.abs(firstTarget);
  const preShiftDays = preShiftDaysFor(absFirst, preferences.practicality);
  const minRate = preferences.useMelatonin ? 1.25 : 1;
  const daysToAdapt = Math.max(1, Math.ceil(Math.max(...segments.map((s) => Math.abs(s.targetPhaseHours))) / minRate));

  const firstDepartHome = flights[0].departUtc.setZone(home.tz);
  const startDay = firstDepartHome.minus({ days: preShiftDays }).startOf("day");
  let cbtMin = cbtMinOnHomeDate(startDay, home.tz, profile);
  if (cbtMin < startDay) cbtMin = cbtMin.plus({ days: 1 });

  const lastArrive = flights[flights.length - 1].arriveUtc;
  const endBound = lastArrive.plus({ days: Math.min(daysToAdapt + 2, 10) });

  const events: PlanEvent[] = [];
  const anchors: PhaseAnchor[] = [];
  let currentPhase = 0;

  for (const flight of flights) {
    const place: Place = {
      tz: flight.origin.tz,
      label: `${flight.origin.iata} → ${flight.dest.iata}`,
      kind: "flight",
      iata: flight.dest.iata,
    };
    const hours = Math.round(flight.arriveUtc.diff(flight.departUtc, "hours").hours * 10) / 10;
    pushEvent(
      events,
      "flight",
      { start: flight.departUtc, end: flight.arriveUtc },
      place,
      `${flight.origin.iata} → ${flight.dest.iata}`,
      `${hours}h airborne. Follow the light and sleep windows — the cabin schedule is not your clock.`,
      20,
      increment,
    );
  }

  for (let cycle = 0; cycle < 20 && cbtMin < endBound; cycle += 1) {
    const target = targetAtTime(flights, home, preferences, cbtMin);
    const delta = target - currentPhase;
    const aligned = Math.abs(delta) < 0.4;
    const step = aligned
      ? 0
      : clamp(delta, -maxDailyStep(Math.sign(delta) || -1, preferences), maxDailyStep(Math.sign(delta) || 1, preferences));
    const direction = directionFromPhase(step !== 0 ? step : target);

    anchors.push({
      utc: cbtMin.toUTC().toISO() ?? cbtMin.toUTC().toString(),
      phaseHours: currentPhase,
    });

    const sleepStart = cbtMin.minus({ hours: sleepHours - wakeAfterCbt });
    const sleepEnd = cbtMin.plus({ hours: wakeAfterCbt });
    const sleep: Interval = { start: sleepStart, end: sleepEnd };
    const sleepPlace = locationAt(flights, home, sleepStart.plus({ hours: sleepHours / 2 }));

    pushEvent(
      events,
      "sleep",
      sleep,
      sleepPlace,
      sleepPlace.kind === "flight" ? "Sleep on the plane" : "Sleep",
      sleepPlace.kind === "flight"
        ? "Sleep only if this window says so. Darkness (an eye mask) is what your clock reads as night."
        : "Protect this window. Sleep equals darkness for your circadian clock, so do not treat extra sleep as automatically helpful.",
      minMinutes,
      increment,
    );

    const avoidCore: Interval =
      direction === "west"
        ? { start: cbtMin, end: cbtMin.plus({ hours: 4 }) }
        : { start: cbtMin.minus({ hours: 4 }), end: cbtMin };
    const seekCore: Interval =
      direction === "west"
        ? { start: cbtMin.minus({ hours: 4 }), end: cbtMin }
        : { start: cbtMin, end: cbtMin.plus({ hours: 4 }) };

    if (!aligned) {
      const avoidPieces =
        locationAt(flights, home, avoidCore.start.plus({ hours: 1 })).kind === "flight"
          ? [avoidCore]
          : clipOutside(avoidCore, [sleep]);
      const visibleAvoid = avoidPieces.length > 0 ? avoidPieces : [avoidCore];
      for (const piece of visibleAvoid) {
        const place = locationAt(flights, home, piece.start.plus({ minutes: Math.max(1, durationMinutes(piece) / 2) }));
        pushEvent(
          events,
          "avoid-light",
          piece,
          place,
          place.kind === "flight" || overlaps(piece, sleep) ? "Keep it dark" : "Avoid bright light",
          avoidCopy(place.kind === "flight", preferences.practicality),
          Math.min(minMinutes, 20),
          increment,
        );
      }
      for (const piece of clipOutside(seekCore, [sleep])) {
        const place = locationAt(flights, home, piece.start.plus({ minutes: durationMinutes(piece) / 2 }));
        pushEvent(
          events,
          "seek-light",
          piece,
          place,
          "Seek bright light",
          seekCopy(place.kind === "flight", direction),
          minMinutes,
          increment,
        );
      }
    } else {
      const maintainSeek = clipOutside({ start: sleepEnd, end: sleepEnd.plus({ hours: 2 }) }, [sleep]);
      for (const piece of maintainSeek) {
        const place = locationAt(flights, home, piece.start);
        pushEvent(
          events,
          "seek-light",
          piece,
          place,
          "Morning light",
          "You are close to aligned. Get outdoor light after waking to lock in local time.",
          minMinutes,
          increment,
        );
      }
    }

    if (preferences.useMelatonin && !aligned && direction === "east") {
      const melatoninAt = sleepStart.minus({ hours: 5 });
      const place = locationAt(flights, home, melatoninAt);
      pushEvent(
        events,
        "melatonin",
        { start: melatoninAt, end: melatoninAt.plus({ minutes: 20 }) },
        place,
        "Take melatonin (0.5 mg)",
        "Use a clock-shifting microdose, not a 3–10 mg sleep tablet. Timing is relative to your body clock, not local bedtime.",
        15,
        increment,
      );
    }

    if (preferences.useCaffeine) {
      const nextSleepStart = sleepStart.plus({ hours: 24 + step });
      const cutoff = nextSleepStart.minus({
        hours: caffeineCutoffHours(preferences.practicality),
      });
      const caffeineStart = sleepEnd.plus({ minutes: 20 });
      if (cutoff > caffeineStart) {
        const place = locationAt(flights, home, caffeineStart.plus({ hours: 1 }));
        pushEvent(
          events,
          "caffeine",
          { start: caffeineStart, end: DateTime.min(cutoff, caffeineStart.plus({ hours: 3 })) },
          place,
          "Caffeine is OK",
          `Optional, for sleepiness only. Stop at least ${caffeineCutoffHours(preferences.practicality)} hours before the next sleep window.`,
          minMinutes,
          increment,
        );
      }
    }

    if (!aligned && cbtMin > flights[0].arriveUtc) {
      const napStart = sleepEnd.plus({ hours: 6 });
      const nap: Interval = { start: napStart, end: napStart.plus({ minutes: 25 }) };
      const napPlace = locationAt(flights, home, napStart);
      const localHour = napStart.setZone(napPlace.tz).hour;
      const farFromNight = nap.end < sleepStart.minus({ hours: 6 });
      if (
        napPlace.kind === "city" &&
        localHour >= 12 &&
        localHour <= 16 &&
        farFromNight &&
        !overlaps(nap, seekCore)
      ) {
        pushEvent(
          events,
          "nap",
          nap,
          napPlace,
          "Optional 20-minute nap",
          "Only if you are struggling. Keep it short so it does not steal from tonight’s sleep or your light window.",
          15,
          increment,
        );
      }
    }

    if (aligned && cbtMin > lastArrive) {
      const place = locationAt(flights, home, cbtMin);
      pushEvent(
        events,
        "aligned",
        { start: sleepEnd, end: sleepEnd.plus({ hours: 1 }) },
        place,
        "You are on local time",
        "Keep a regular local sleep schedule and get outdoor morning light. The hard shift is done.",
        20,
        increment,
      );
      currentPhase += step;
      break;
    }

    currentPhase = Math.round((currentPhase + step) * 100) / 100;
    cbtMin = cbtMin.plus({ hours: 24 + step });
  }

  anchors.push({
    utc: cbtMin.toUTC().toISO() ?? cbtMin.toUTC().toString(),
    phaseHours: currentPhase,
  });

  events.sort((a, b) => a.startUtc.localeCompare(b.startUtc));

  const primary = segments[0];
  const shiftAbs = Math.abs(primary.shiftHours);
  const directionLabel =
    primary.direction === "east"
      ? `Eastbound · advance ${shiftAbs.toFixed(1)}h`
      : primary.direction === "west"
        ? `Westbound · delay ${shiftAbs.toFixed(1)}h`
        : "No significant timezone shift";

  const shortNote = segments.some((segment) => segment.shortTrip)
    ? " Short-trip mode keeps you closer to home time so a brief stay does not require a full shift."
    : "";
  const summary =
    primary.direction === "none"
      ? `This itinerary barely changes time zones. Keep your usual ${profile.bedtime}–${profile.waketime} sleep window.`
      : `Your clock needs to ${primary.direction === "east" ? "advance (wake earlier)" : "delay (stay up later)"} by about ${shiftAbs.toFixed(1)} hours. Timed light is the main lever; melatonin and caffeine are optional supports.${shortNote}`;

  return {
    homeTimezone: home.tz,
    homeCity: home.city,
    events,
    anchors,
    segments,
    daysToAdapt,
    preShiftDays,
    summary,
    directionLabel,
  };
}

export function phaseAt(anchors: PhaseAnchor[], at: DateTime): number {
  if (anchors.length === 0) return 0;
  const t = at.toUTC().toMillis();
  const points = anchors.map((anchor) => ({
    t: DateTime.fromISO(anchor.utc, { zone: "utc" }).toMillis(),
    phase: anchor.phaseHours,
  }));
  if (t <= points[0].t) return points[0].phase;
  const last = points[points.length - 1];
  if (t >= last.t) return last.phase;
  for (let i = 0; i < points.length - 1; i += 1) {
    const a = points[i];
    const b = points[i + 1];
    if (t >= a.t && t <= b.t) {
      const p = (t - a.t) / Math.max(1, b.t - a.t);
      return a.phase + (b.phase - a.phase) * p;
    }
  }
  return last.phase;
}

export function bodyClockMinutes(homeTz: string, anchors: PhaseAnchor[], at: DateTime): number {
  const homeLocal = at.setZone(homeTz);
  const homeMinutes = homeLocal.hour * 60 + homeLocal.minute;
  const phaseMinutes = phaseAt(anchors, at) * 60;
  return (homeMinutes - phaseMinutes + 1440 * 4) % 1440;
}

export function minutesToLabel(minutes: number): string {
  const wrapped = (Math.round(minutes) + 1440) % 1440;
  const hours = Math.floor(wrapped / 60);
  const mins = wrapped % 60;
  const period = hours >= 12 ? "PM" : "AM";
  const hour12 = hours % 12 === 0 ? 12 : hours % 12;
  return `${hour12}:${mins.toString().padStart(2, "0")} ${period}`;
}

export function eventsOverlapping(
  events: PlanEvent[],
  start: DateTime,
  end: DateTime,
): PlanEvent[] {
  const s = start.toUTC().toMillis();
  const e = end.toUTC().toMillis();
  return events.filter((event) => {
    const a = DateTime.fromISO(event.startUtc, { zone: "utc" }).toMillis();
    const b = DateTime.fromISO(event.endUtc, { zone: "utc" }).toMillis();
    return a < e && b > s;
  });
}

export const EVENT_PRIORITY: Record<EventKind, number> = {
  sleep: 10,
  "avoid-light": 8,
  "seek-light": 7,
  melatonin: 6,
  nap: 5,
  caffeine: 4,
  flight: 3,
  aligned: 2,
};
