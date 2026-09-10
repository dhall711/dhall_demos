export type Chronotype = "early" | "intermediate" | "late";
export type Practicality = "easy" | "balanced" | "strict";

export type SleepProfile = {
  bedtime: string;
  waketime: string;
  chronotype: Chronotype;
};

export type Preferences = {
  useMelatonin: boolean;
  useCaffeine: boolean;
  practicality: Practicality;
  shortTripMode: boolean;
};

export type FlightInput = {
  id: string;
  originIata: string;
  destinationIata: string;
  /** Local wall time at origin, `yyyy-MM-dd'T'HH:mm` */
  departLocal: string;
  /** Local wall time at destination, `yyyy-MM-dd'T'HH:mm` */
  arriveLocal: string;
};

export type PlanInput = {
  homeIata: string;
  profile: SleepProfile;
  preferences: Preferences;
  flights: FlightInput[];
};

export type EventKind =
  | "seek-light"
  | "avoid-light"
  | "sleep"
  | "nap"
  | "caffeine"
  | "melatonin"
  | "flight"
  | "aligned";

export type PlanEvent = {
  id: string;
  kind: EventKind;
  startUtc: string;
  endUtc: string;
  title: string;
  detail: string;
  place: string;
  timezone: string;
  inFlight: boolean;
};

export type PhaseAnchor = {
  utc: string;
  phaseHours: number;
};

export type TripSegment = {
  originIata: string;
  destinationIata: string;
  originCity: string;
  destinationCity: string;
  direction: "east" | "west" | "none";
  shiftHours: number;
  targetPhaseHours: number;
  shortTrip: boolean;
  departUtc: string;
  arriveUtc: string;
};

export type GeneratedPlan = {
  homeTimezone: string;
  homeCity: string;
  events: PlanEvent[];
  anchors: PhaseAnchor[];
  segments: TripSegment[];
  daysToAdapt: number;
  preShiftDays: number;
  summary: string;
  directionLabel: string;
};
