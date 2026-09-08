import { DateTime } from "luxon";
import { describe, expect, it } from "vitest";
import {
  cbtMinHoursBeforeWake,
  generatePlan,
  minutesFromHm,
  normalizePhaseHours,
  sleepDurationHours,
  targetPhaseHours,
} from "@/lib/circadian/engine";
import type { PlanInput } from "@/lib/circadian/types";

const baseProfile = {
  bedtime: "23:00",
  waketime: "07:00",
  chronotype: "intermediate" as const,
};

const basePrefs = {
  useMelatonin: true,
  useCaffeine: true,
  practicality: "balanced" as const,
  shortTripMode: true,
};

function nycLondon(overrides: Partial<PlanInput> = {}): PlanInput {
  return {
    homeIata: "JFK",
    profile: baseProfile,
    preferences: basePrefs,
    flights: [
      {
        id: "out",
        originIata: "JFK",
        destinationIata: "LHR",
        departLocal: "2026-11-12T21:30",
        arriveLocal: "2026-11-13T09:30",
      },
    ],
    ...overrides,
  };
}

describe("circadian helpers", () => {
  it("computes an 8 hour sleep window across midnight", () => {
    expect(sleepDurationHours(baseProfile)).toBe(8);
    expect(minutesFromHm("07:00")).toBe(420);
  });

  it("places CBTmin later for late chronotypes", () => {
    expect(cbtMinHoursBeforeWake("early")).toBe(2);
    expect(cbtMinHoursBeforeWake("late")).toBe(3);
  });

  it("chooses the shorter phase shift across the date line", () => {
    const at = DateTime.fromISO("2026-11-13T12:00:00Z");
    const nycToLondon = targetPhaseHours("America/New_York", "Europe/London", at);
    const nycToTokyo = targetPhaseHours("America/New_York", "Asia/Tokyo", at);
    expect(nycToLondon).toBeCloseTo(-5, 0);
    expect(Math.abs(nycToTokyo)).toBeLessThanOrEqual(12);
    expect(nycToTokyo).toBeGreaterThan(0);
  });

  it("wraps phase hours into (-12, 12]", () => {
    expect(normalizePhaseHours(13)).toBe(-11);
    expect(normalizePhaseHours(-13)).toBe(11);
  });
});

describe("generatePlan", () => {
  it("builds an eastbound NYC to London plan with light, sleep, and melatonin", () => {
    const plan = generatePlan(nycLondon());
    expect(plan.segments[0].direction).toBe("east");
    expect(plan.preShiftDays).toBeGreaterThanOrEqual(1);
    const kinds = new Set(plan.events.map((event) => event.kind));
    expect(kinds.has("sleep")).toBe(true);
    expect(kinds.has("seek-light")).toBe(true);
    expect(kinds.has("avoid-light")).toBe(true);
    expect(kinds.has("melatonin")).toBe(true);
    expect(kinds.has("caffeine")).toBe(true);
    expect(kinds.has("flight")).toBe(true);
    expect(plan.events.some((event) => event.inFlight)).toBe(true);
  });

  it("omits melatonin and caffeine when the traveler turns them off", () => {
    const plan = generatePlan(
      nycLondon({
        preferences: { ...basePrefs, useMelatonin: false, useCaffeine: false },
      }),
    );
    expect(plan.events.every((event) => event.kind !== "melatonin")).toBe(true);
    expect(plan.events.every((event) => event.kind !== "caffeine")).toBe(true);
    expect(plan.events.some((event) => event.kind === "seek-light")).toBe(true);
  });

  it("delays the clock for westbound NYC to Los Angeles", () => {
    const plan = generatePlan({
      homeIata: "JFK",
      profile: baseProfile,
      preferences: basePrefs,
      flights: [
        {
          id: "out",
          originIata: "JFK",
          destinationIata: "LAX",
          departLocal: "2026-11-12T08:00",
          arriveLocal: "2026-11-12T11:30",
        },
      ],
    });
    expect(plan.segments[0].direction).toBe("west");
    expect(plan.segments[0].shiftHours).toBeCloseTo(-3, 0);
    expect(plan.events.some((event) => event.kind === "melatonin")).toBe(false);
    expect(plan.events.some((event) => event.kind === "seek-light")).toBe(true);
  });

  it("keeps home time for a 36-hour London turnaround", () => {
    const plan = generatePlan({
      homeIata: "JFK",
      profile: baseProfile,
      preferences: basePrefs,
      flights: [
        {
          id: "out",
          originIata: "JFK",
          destinationIata: "LHR",
          departLocal: "2026-11-12T21:30",
          arriveLocal: "2026-11-13T09:30",
        },
        {
          id: "back",
          originIata: "LHR",
          destinationIata: "JFK",
          departLocal: "2026-11-14T18:00",
          arriveLocal: "2026-11-14T21:30",
        },
      ],
    });
    expect(plan.segments[0].shortTrip).toBe(true);
    expect(plan.segments[0].targetPhaseHours).toBe(0);
    expect(plan.summary.toLowerCase()).toContain("short-trip");
  });

  it("fully adapts when short-trip mode is off", () => {
    const plan = generatePlan({
      homeIata: "JFK",
      profile: baseProfile,
      preferences: { ...basePrefs, shortTripMode: false },
      flights: [
        {
          id: "out",
          originIata: "JFK",
          destinationIata: "LHR",
          departLocal: "2026-11-12T21:30",
          arriveLocal: "2026-11-13T09:30",
        },
        {
          id: "back",
          originIata: "LHR",
          destinationIata: "JFK",
          departLocal: "2026-11-14T18:00",
          arriveLocal: "2026-11-14T21:30",
        },
      ],
    });
    expect(plan.segments[0].shortTrip).toBe(false);
    expect(plan.segments[0].targetPhaseHours).toBeCloseTo(-5, 0);
  });

  it("tracks a stopover city between two long-haul flights", () => {
    const plan = generatePlan({
      homeIata: "SFO",
      profile: baseProfile,
      preferences: { ...basePrefs, shortTripMode: false },
      flights: [
        {
          id: "1",
          originIata: "SFO",
          destinationIata: "NRT",
          departLocal: "2026-11-10T11:00",
          arriveLocal: "2026-11-11T16:00",
        },
        {
          id: "2",
          originIata: "NRT",
          destinationIata: "SIN",
          departLocal: "2026-11-11T22:00",
          arriveLocal: "2026-11-12T05:00",
        },
      ],
    });
    expect(plan.segments).toHaveLength(2);
    expect(plan.events.some((event) => event.place.includes("NRT"))).toBe(true);
    expect(plan.events.some((event) => event.place.includes("Singapore") || event.place.includes("SIN"))).toBe(
      true,
    );
  });

  it("places late-chronotype CBTmin further from wake than early types", () => {
    const early = generatePlan(nycLondon({ profile: { ...baseProfile, chronotype: "early" } }));
    const late = generatePlan(nycLondon({ profile: { ...baseProfile, chronotype: "late" } }));
    const earlyCbt = DateTime.fromISO(early.anchors[0].utc, { zone: "utc" }).setZone("America/New_York");
    const lateCbt = DateTime.fromISO(late.anchors[0].utc, { zone: "utc" }).setZone("America/New_York");
    const earlyGap = 7 * 60 - (earlyCbt.hour * 60 + earlyCbt.minute);
    const lateGap = 7 * 60 - (lateCbt.hour * 60 + lateCbt.minute);
    expect(lateGap).toBeGreaterThan(earlyGap);
  });

  it("advances body clock for an eastbound trip after several days", () => {
    const plan = generatePlan(nycLondon({ preferences: { ...basePrefs, shortTripMode: false } }));
    expect(plan.anchors[plan.anchors.length - 1].phaseHours).toBeLessThan(-2);
    const firstCbtHome = DateTime.fromISO(plan.anchors[0].utc, { zone: "utc" }).setZone(plan.homeTimezone);
    const lastCbtHome = DateTime.fromISO(plan.anchors[plan.anchors.length - 1].utc, { zone: "utc" }).setZone(
      plan.homeTimezone,
    );
    const firstMinutes = firstCbtHome.hour * 60 + firstCbtHome.minute;
    const lastMinutes = lastCbtHome.hour * 60 + lastCbtHome.minute;
    expect((lastMinutes - firstMinutes + 1440) % 1440).toBeGreaterThan(120);
  });

  it("rejects arrivals that are before departures", () => {
    expect(() =>
      generatePlan({
        homeIata: "JFK",
        profile: baseProfile,
        preferences: basePrefs,
        flights: [
          {
            id: "bad",
            originIata: "JFK",
            destinationIata: "LHR",
            departLocal: "2026-11-12T21:30",
            arriveLocal: "2026-11-12T20:00",
          },
        ],
      }),
    ).toThrow(/arrives before/);
  });
});
