import { generatePlan } from "@/lib/circadian/engine";
import { buildPlanDays } from "@/lib/circadian/timeline";
import { generateResetSleep } from "@/lib/circadian/reset-sleep";
import type { PlanInput } from "@/lib/circadian/types";
import { describe, expect, it } from "vitest";

const input: PlanInput = {
  homeIata: "JFK",
  profile: { bedtime: "23:00", waketime: "07:00", chronotype: "intermediate" },
  preferences: {
    useMelatonin: true,
    useCaffeine: true,
    practicality: "balanced",
    shortTripMode: false,
  },
  flights: [
    {
      id: "out",
      originIata: "JFK",
      destinationIata: "LHR",
      departLocal: "2026-11-12T21:30",
      arriveLocal: "2026-11-13T09:30",
    },
  ],
};

describe("buildPlanDays", () => {
  it("groups a trip into labeled days with wake, bedtime, and light items", () => {
    const plan = generatePlan(input);
    const days = buildPlanDays(input, plan);
    expect(days.length).toBeGreaterThan(2);
    expect(days.some((day) => day.chip === "Travel")).toBe(true);
    expect(days.some((day) => day.chip.startsWith("D-"))).toBe(true);
    const kinds = new Set(days.flatMap((day) => day.items.map((item) => item.kind)));
    expect(kinds.has("wake")).toBe(true);
    expect(kinds.has("bedtime")).toBe(true);
    expect(kinds.has("seek-light")).toBe(true);
    expect(kinds.has("caffeine")).toBe(true);
  });
});

describe("generateResetSleep", () => {
  it("builds a multi-day advance from a late wake toward 7am", () => {
    const result = generateResetSleep({
      lastWake: "11:15",
      targetWake: "07:00",
      startDate: "2026-08-15",
      useMelatonin: true,
    });
    expect(result.shiftHours).toBeLessThan(0);
    expect(result.days.length).toBeGreaterThanOrEqual(3);
    expect(result.days[0]?.chip).toBe("Today");
    expect(result.days.some((day) => day.actions.some((action) => action.kind === "melatonin"))).toBe(true);
    expect(result.summary.toLowerCase()).toContain("earlier");
  });
});
