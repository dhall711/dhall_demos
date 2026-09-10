import { DateTime } from "luxon";
import type { FlightInput, PlanInput } from "@/lib/circadian/types";

function localStamp(dt: DateTime): string {
  return dt.toFormat("yyyy-LL-dd'T'HH:mm");
}

function id(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 8)}`;
}

export const DEFAULT_PROFILE = {
  bedtime: "23:00",
  waketime: "07:00",
  chronotype: "intermediate" as const,
};

export const DEFAULT_PREFERENCES = {
  useMelatonin: true,
  useCaffeine: true,
  practicality: "balanced" as const,
  shortTripMode: true,
};

export function emptyFlight(origin = "JFK", destination = "LHR"): FlightInput {
  const originDay = DateTime.now().plus({ days: 4 }).set({ hour: 21, minute: 30, second: 0, millisecond: 0 });
  const destDay = originDay.plus({ days: 1 }).set({ hour: 9, minute: 30 });
  return {
    id: id("flt"),
    originIata: origin,
    destinationIata: destination,
    departLocal: localStamp(originDay),
    arriveLocal: localStamp(destDay),
  };
}

export type ExampleTrip = {
  id: string;
  title: string;
  blurb: string;
  input: PlanInput;
};

export function exampleTrips(): ExampleTrip[] {
  const start = DateTime.now().plus({ days: 5 }).set({ second: 0, millisecond: 0 });
  const nycOut = start.set({ hour: 21, minute: 30 });
  const lonIn = nycOut.plus({ days: 1 }).set({ hour: 9, minute: 30 });
  const lonOut = start.plus({ days: 12 }).set({ hour: 11, minute: 0 });
  const nycIn = lonOut.set({ hour: 14, minute: 20 });

  const sfoOut = start.plus({ days: 1 }).set({ hour: 11, minute: 5 });
  const nrtIn = sfoOut.plus({ days: 1 }).set({ hour: 15, minute: 40 });
  const nrtBack = start.plus({ days: 8 }).set({ hour: 17, minute: 10 });
  const sfoBack = nrtBack.set({ hour: 10, minute: 0 });

  const quickOut = start.set({ hour: 19, minute: 0 });
  const quickIn = quickOut.plus({ days: 1 }).set({ hour: 7, minute: 15 });
  const quickBack = start.plus({ days: 2 }).set({ hour: 18, minute: 30 });
  const quickHome = quickBack.set({ hour: 21, minute: 45 });

  return [
    {
      id: "nyc-london",
      title: "New York → London",
      blurb: "Overnight eastbound, one week, full shift with melatonin.",
      input: {
        homeIata: "JFK",
        profile: DEFAULT_PROFILE,
        preferences: { ...DEFAULT_PREFERENCES, shortTripMode: false },
        flights: [
          {
            id: id("out"),
            originIata: "JFK",
            destinationIata: "LHR",
            departLocal: localStamp(nycOut),
            arriveLocal: localStamp(lonIn),
          },
          {
            id: id("ret"),
            originIata: "LHR",
            destinationIata: "JFK",
            departLocal: localStamp(lonOut),
            arriveLocal: localStamp(nycIn),
          },
        ],
      },
    },
    {
      id: "sfo-tokyo",
      title: "San Francisco → Tokyo",
      blurb: "Westbound Pacific crossing. Delay the clock, seek evening light.",
      input: {
        homeIata: "SFO",
        profile: DEFAULT_PROFILE,
        preferences: { ...DEFAULT_PREFERENCES, shortTripMode: false },
        flights: [
          {
            id: id("out"),
            originIata: "SFO",
            destinationIata: "NRT",
            departLocal: localStamp(sfoOut),
            arriveLocal: localStamp(nrtIn),
          },
          {
            id: id("ret"),
            originIata: "NRT",
            destinationIata: "SFO",
            departLocal: localStamp(nrtBack),
            arriveLocal: localStamp(sfoBack),
          },
        ],
      },
    },
    {
      id: "quick-london",
      title: "36-hour London turnaround",
      blurb: "Stay on New York time. Short-trip mode skips a full five-hour shift.",
      input: {
        homeIata: "JFK",
        profile: DEFAULT_PROFILE,
        preferences: DEFAULT_PREFERENCES,
        flights: [
          {
            id: id("out"),
            originIata: "JFK",
            destinationIata: "LHR",
            departLocal: localStamp(quickOut),
            arriveLocal: localStamp(quickIn),
          },
          {
            id: id("ret"),
            originIata: "LHR",
            destinationIata: "JFK",
            departLocal: localStamp(quickBack),
            arriveLocal: localStamp(quickHome),
          },
        ],
      },
    },
  ];
}
