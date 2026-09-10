import { DateTime } from "luxon";
import { getAirport } from "@/lib/airports";
import type { EventKind, GeneratedPlan, PlanEvent, PlanInput } from "@/lib/circadian/types";

export type TimelineKind = EventKind | "wake" | "bedtime";

export type TimelineItem = {
  id: string;
  kind: TimelineKind;
  startUtc: string;
  endUtc?: string;
  title: string;
  detail: string;
  timeLabel: string;
  untilLabel?: string;
  place: string;
  timezone: string;
  destTimeLabel?: string;
  checkable: boolean;
};

export type PlanDay = {
  key: string;
  chip: string;
  title: string;
  dateLabel: string;
  items: TimelineItem[];
  tips: string[];
};

function localOf(event: PlanEvent): DateTime {
  return DateTime.fromISO(event.startUtc, { zone: "utc" }).setZone(event.timezone);
}

function formatUntil(event: PlanEvent): string | undefined {
  if (!event.endUtc) return undefined;
  const end = DateTime.fromISO(event.endUtc, { zone: "utc" }).setZone(event.timezone);
  const start = localOf(event);
  if (end.diff(start, "minutes").minutes < 40) return undefined;
  return `Until ${end.toFormat("HH:mm")}`;
}

function itemFromEvent(event: PlanEvent, title?: string): TimelineItem {
  const local = localOf(event);
  return {
    id: event.id,
    kind: event.kind,
    startUtc: event.startUtc,
    endUtc: event.endUtc,
    title: title ?? event.title,
    detail: event.detail,
    timeLabel: local.toFormat("HH:mm"),
    untilLabel: formatUntil(event),
    place: event.place,
    timezone: event.timezone,
    checkable: event.kind !== "aligned",
  };
}

function sleepParts(event: PlanEvent): TimelineItem[] {
  const start = localOf(event);
  const end = DateTime.fromISO(event.endUtc, { zone: "utc" }).setZone(event.timezone);
  const hours = Math.round(end.diff(start, "hours").hours * 10) / 10;
  const bedtime: TimelineItem = {
    id: `${event.id}-bed`,
    kind: "bedtime",
    startUtc: event.startUtc,
    endUtc: event.endUtc,
    title: event.inFlight ? "Sleep on the plane" : "Bedtime",
    detail: event.inFlight
      ? "Darkness (an eye mask) is what your clock reads as night."
      : `Get ${hours} hours of sleep if you can.`,
    timeLabel: start.toFormat("HH:mm"),
    place: event.place,
    timezone: event.timezone,
    checkable: true,
  };
  const wake: TimelineItem = {
    id: `${event.id}-wake`,
    kind: "wake",
    startUtc: event.endUtc,
    title: "Wake up",
    detail: "Get up with the plan even if it feels early or late.",
    timeLabel: end.toFormat("HH:mm"),
    place: event.place,
    timezone: event.timezone,
    checkable: true,
  };
  return [bedtime, wake];
}

function flightItem(event: PlanEvent, destTz?: string): TimelineItem {
  const start = localOf(event);
  const dest = destTz
    ? DateTime.fromISO(event.startUtc, { zone: "utc" }).setZone(destTz)
    : undefined;
  return {
    ...itemFromEvent(event, "Flight timeline"),
    detail: "Set devices to destination time. Start dimming screens if this is an evening flight.",
    destTimeLabel: dest ? dest.toFormat("HH:mm, LLL d") : undefined,
    timeLabel: start.toFormat("HH:mm, LLL d"),
  };
}

function chipFor(diff: number, isTravel: boolean, isReturn: boolean): { chip: string; title: string } {
  if (isReturn) return { chip: "Return", title: "Return travel" };
  if (isTravel || diff === 0) return { chip: "Travel", title: "Travel day" };
  if (diff < 0) {
    const n = Math.abs(diff);
    return { chip: `D-${n}`, title: n === 1 ? "Day before travel" : `Day ${n} before travel` };
  }
  return { chip: `D+${diff}`, title: diff === 1 ? "First day after arrival" : `Day ${diff} after arrival` };
}

function tipsFor(chip: string, direction: "east" | "west" | "none"): string[] {
  if (chip.startsWith("D-")) {
    return direction === "west"
      ? ["Start shifting before you fly", "Stay up a little later than usual", "Seek evening light, protect morning dark"]
      : ["Start shifting before you fly", "Go to bed a little earlier than usual", "Seek morning light, dim evenings"];
  }
  if (chip === "Travel" || chip === "Return") {
    return ["Follow the in-flight light window, not cabin mood lighting", "Set watches to destination time after takeoff", "Skip caffeine once the cutoff hits"];
  }
  return ["Protect the planned sleep window", "Get outdoor light at the seek-light times", "Keep caffeine in the morning window only"];
}

export function buildPlanDays(input: PlanInput, plan: GeneratedPlan): PlanDay[] {
  const outbound = input.flights[0];
  const home = getAirport(input.homeIata);
  const origin = getAirport(outbound.originIata);
  const dest = getAirport(outbound.destinationIata);
  if (!origin || !dest) return [];
  const travelDay = DateTime.fromISO(outbound.departLocal, { zone: origin.tz }).startOf("day");
  const returnFlight = input.flights.length > 1 ? input.flights[input.flights.length - 1] : undefined;
  const returnDay = returnFlight
    ? DateTime.fromISO(returnFlight.departLocal, { zone: getAirport(returnFlight.originIata)?.tz ?? origin.tz }).startOf(
        "day",
      )
    : null;

  const buckets = new Map<string, TimelineItem[]>();

  for (const event of plan.events) {
    if (event.kind === "aligned") continue;
    const local = localOf(event);
    const key = local.toISODate() ?? event.startUtc.slice(0, 10);
    const list = buckets.get(key) ?? [];
    if (event.kind === "sleep") {
      list.push(...sleepParts(event));
    } else if (event.kind === "flight") {
      list.push(flightItem(event, dest.tz));
    } else if (event.kind === "seek-light") {
      list.push(itemFromEvent(event, "Seek bright light"));
    } else if (event.kind === "avoid-light") {
      list.push(itemFromEvent(event, "Dim lights / avoid bright light"));
    } else if (event.kind === "caffeine") {
      list.push(itemFromEvent(event, "Caffeine window"));
    } else if (event.kind === "melatonin") {
      list.push(itemFromEvent(event, "Melatonin (optional)"));
    } else {
      list.push(itemFromEvent(event));
    }
    buckets.set(key, list);
  }

  const direction = plan.segments[0]?.direction ?? "none";
  const days: PlanDay[] = [...buckets.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, items]) => {
      const date = DateTime.fromISO(key, { zone: home?.tz ?? origin.tz }).startOf("day");
      const diff = Math.round(date.diff(travelDay, "days").days);
      const isReturn = Boolean(returnDay && Math.round(date.diff(returnDay, "days").days) === 0);
      const isTravel = diff === 0 || (diff === 1 && items.some((item) => item.kind === "flight") && !isReturn);
      const labels = chipFor(diff, isTravel, isReturn);
      const sorted = items.sort((a, b) => a.startUtc.localeCompare(b.startUtc));
      return {
        key,
        chip: labels.chip,
        title: labels.title,
        dateLabel: date.toFormat("cccc, LLL d"),
        items: sorted,
        tips: tipsFor(labels.chip, direction),
      };
    });

  return days;
}

export function shiftHoursLabel(plan: GeneratedPlan): string {
  const hours = Math.abs(plan.segments[0]?.shiftHours ?? 0);
  const dir = plan.segments[0]?.direction;
  if (dir === "east") return `${hours.toFixed(0)}h behind dest`;
  if (dir === "west") return `${hours.toFixed(0)}h ahead of dest`;
  return "No timezone jump";
}
