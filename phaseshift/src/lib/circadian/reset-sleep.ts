import { DateTime } from "luxon";

export type ResetAction = {
  id: string;
  title: string;
  detail: string;
  startLabel: string;
  kind: "light" | "caffeine" | "dim" | "bed" | "wake" | "melatonin";
};

export type ResetDay = {
  key: string;
  chip: string;
  title: string;
  dateLabel: string;
  wakeLabel: string;
  actions: ResetAction[];
};

export type ResetSleepInput = {
  lastWake: string;
  targetWake: string;
  sleepHours?: number;
  useMelatonin?: boolean;
  startDate?: string;
};

function hm(value: string): number {
  const [hours, minutes] = value.split(":").map(Number);
  return hours * 60 + minutes;
}

function labelFromMinutes(total: number): string {
  const wrapped = (total + 1440 * 4) % 1440;
  const hours = Math.floor(wrapped / 60);
  const minutes = wrapped % 60;
  const period = hours >= 12 ? "PM" : "AM";
  const hour12 = hours % 12 === 0 ? 12 : hours % 12;
  return `${hour12}:${minutes.toString().padStart(2, "0")} ${period}`;
}

export function generateResetSleep(input: ResetSleepInput): {
  shiftHours: number;
  days: ResetDay[];
  summary: string;
} {
  const last = hm(input.lastWake);
  const target = hm(input.targetWake);
  let delta = target - last;
  if (delta > 720) delta -= 1440;
  if (delta < -720) delta += 1440;
  const shiftHours = Math.round((delta / 60) * 10) / 10;
  const sleepHours = input.sleepHours ?? 8;
  const maxStep = 60;
  const dayCount = Math.max(1, Math.min(5, Math.ceil(Math.abs(delta) / maxStep)));
  const start = input.startDate
    ? DateTime.fromISO(input.startDate)
    : DateTime.now().startOf("day");

  const days: ResetDay[] = [];
  for (let i = 0; i < dayCount; i += 1) {
    const progressed = Math.sign(delta) * Math.min(Math.abs(delta), maxStep * (i + 1));
    const wakeMin = last + progressed;
    const date = start.plus({ days: i });
    const bedMin = wakeMin - sleepHours * 60;
    const lightEnd = wakeMin + 120;
    const caffeineEnd = bedMin - 8 * 60;
    const dimAt = bedMin - 90;
    const melatoninAt = bedMin - 30;
    const advancing = shiftHours < 0;
    const actions: ResetAction[] = [
      {
        id: `${date.toISODate()}-wake`,
        kind: "wake",
        title: "Wake up",
        detail: advancing ? "Get up earlier than yesterday, even if it is hard." : "Hold on until the later wake time.",
        startLabel: labelFromMinutes(wakeMin),
      },
      {
        id: `${date.toISODate()}-light`,
        kind: "light",
        title: advancing ? "Get bright light now" : "Seek evening light",
        detail: advancing
          ? "Get outside or use bright light to move your body clock earlier."
          : "Stay in bright light through the evening to delay your clock.",
        startLabel: `${labelFromMinutes(wakeMin)} – ${labelFromMinutes(lightEnd)}`,
      },
      {
        id: `${date.toISODate()}-caffeine`,
        kind: "caffeine",
        title: "No more caffeine",
        detail: "Stop at least 8 hours before the planned bedtime.",
        startLabel: labelFromMinutes(caffeineEnd),
      },
      {
        id: `${date.toISODate()}-dim`,
        kind: "dim",
        title: "Dim lights",
        detail: "Low indoor light and no bright screens close to bed.",
        startLabel: labelFromMinutes(dimAt),
      },
    ];
    if (input.useMelatonin && advancing) {
      actions.push({
        id: `${date.toISODate()}-melatonin`,
        kind: "melatonin",
        title: "Melatonin (optional)",
        detail: "0.5 mg about 30 minutes before bed. Educational timing only.",
        startLabel: labelFromMinutes(melatoninAt),
      });
    }
    actions.push({
      id: `${date.toISODate()}-bed`,
      kind: "bed",
      title: "Bedtime",
      detail: `Aim for about ${sleepHours} hours of sleep.`,
      startLabel: labelFromMinutes(bedMin),
    });
    days.push({
      key: date.toISODate() ?? `${i}`,
      chip: i === 0 ? "Today" : `Day ${i}`,
      title: i === 0 ? "Today" : `Day ${i}`,
      dateLabel: date.toFormat("cccc, LLL d"),
      wakeLabel: labelFromMinutes(wakeMin),
      actions,
    });
  }

  const summary = shiftHours < 0
    ? `Shift wake earlier by about ${Math.abs(shiftHours).toFixed(1)} hours over ${dayCount} days.`
    : shiftHours > 0
      ? `Shift wake later by about ${shiftHours.toFixed(1)} hours over ${dayCount} days.`
      : "You are already on the target wake time.";

  return { shiftHours, days, summary };
}
