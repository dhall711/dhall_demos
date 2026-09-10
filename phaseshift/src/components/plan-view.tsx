"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { DateTime } from "luxon";
import {
  BedDouble,
  Check,
  Coffee,
  Lightbulb,
  Moon,
  Plane,
  Sparkles,
  Sun,
  Sunrise,
  X,
} from "lucide-react";
import { RemindersToggle, ThemeToggle } from "@/components/theme-toggle";
import { buildPlanDays, shiftHoursLabel, type TimelineKind } from "@/lib/circadian/timeline";
import type { GeneratedPlan, PlanInput } from "@/lib/circadian/types";
import { getAirport } from "@/lib/airports";
import { EMPTY_IDS, getCheckedIds, setCheckedIds, subscribeProgress } from "@/lib/prefs";
import { cn } from "@/lib/utils";

const KIND_ICON: Record<TimelineKind, typeof Sun> = {
  wake: Sunrise,
  bedtime: BedDouble,
  "seek-light": Sun,
  "avoid-light": Moon,
  sleep: BedDouble,
  nap: Moon,
  caffeine: Coffee,
  melatonin: Sparkles,
  flight: Plane,
  aligned: Check,
};

const KIND_DOT: Record<TimelineKind, string> = {
  wake: "bg-orange-400",
  bedtime: "bg-blue-500",
  "seek-light": "bg-orange-400",
  "avoid-light": "bg-violet-500",
  sleep: "bg-blue-500",
  nap: "bg-teal-500",
  caffeine: "bg-amber-700",
  melatonin: "bg-violet-500",
  flight: "bg-sky-500",
  aligned: "bg-emerald-500",
};

type Props = {
  title: string;
  input: PlanInput;
  plan: GeneratedPlan;
  planId: string;
};

export function PlanView({ title, input, plan, planId }: Props) {
  const days = useMemo(() => buildPlanDays(input, plan), [input, plan]);
  const [dayIndex, setDayIndex] = useState(() => {
    const travel = days.findIndex((day) => day.chip === "Travel");
    return travel >= 0 ? Math.max(0, travel - 1) : 0;
  });
  const checked = useSyncExternalStore(
    subscribeProgress,
    () => getCheckedIds(planId),
    () => EMPTY_IDS,
  );
  const day = days[dayIndex] ?? days[0];
  const allIds = days.flatMap((entry) => entry.items.filter((item) => item.checkable).map((item) => item.id));
  const done = allIds.filter((id) => checked.includes(id)).length;
  const percent = allIds.length ? Math.round((done / allIds.length) * 100) : 0;
  const origin = getAirport(input.flights[0]?.originIata);
  const dest = getAirport(input.flights[0]?.destinationIata);
  const outbound = input.flights[0];
  const returning = input.flights[1];

  function toggle(id: string) {
    const next = checked.includes(id) ? checked.filter((item) => item !== id) : [...checked, id];
    setCheckedIds(planId, next);
  }

  const dayDone = day?.items.filter((item) => item.checkable && checked.includes(item.id)).length ?? 0;
  const dayTotal = day?.items.filter((item) => item.checkable).length ?? 0;

  return (
    <div className="mx-auto min-h-full max-w-md bg-background pb-10">
      <header className="sticky top-0 z-20 flex items-center justify-between bg-background/90 px-4 py-3 backdrop-blur">
        <RemindersToggle />
        <div className="text-center">
          <div className="text-sm font-semibold">Jet lag plan</div>
          <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] text-primary">{percent}%</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link href="/" className="flex size-9 items-center justify-center rounded-full bg-muted">
            <X className="size-4" />
          </Link>
        </div>
      </header>

      <div className="space-y-4 px-4">
        <section className="rounded-3xl bg-muted p-4">
          <div className="flex items-center justify-between gap-2 text-sm font-medium">
            <span>{origin?.city}</span>
            <Plane className="size-4 text-primary" />
            <span>{dest?.city}</span>
          </div>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            <span className="rounded-full bg-sky-100 px-2 py-0.5 text-sky-800 dark:bg-sky-900 dark:text-sky-100">
              {shiftHoursLabel(plan)}
            </span>
            <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-100">
              {returning ? "Round trip" : "One way"}
            </span>
          </div>
          <div className="mt-3 space-y-1 rounded-2xl bg-background px-3 py-2 text-xs">
            <p>Depart {DateTime.fromISO(outbound.departLocal).toFormat("ccc, LLL d 'at' h:mm a")}</p>
            <p>Arrive {DateTime.fromISO(outbound.arriveLocal).toFormat("ccc, LLL d 'at' h:mm a")}</p>
            {returning ? (
              <>
                <p>Return {DateTime.fromISO(returning.departLocal).toFormat("ccc, LLL d 'at' h:mm a")}</p>
                <p>Home {DateTime.fromISO(returning.arriveLocal).toFormat("ccc, LLL d 'at' h:mm a")}</p>
              </>
            ) : null}
          </div>
          <p className="mt-3 text-sm text-muted-foreground">{plan.summary}</p>
        </section>

        <p className="text-xs text-muted-foreground">
          General safety · Educational guidance, not medical advice. Ask a clinician before using melatonin.
        </p>

        <div className="flex gap-2 overflow-x-auto pb-1">
          {days.map((entry, index) => (
            <button
              key={entry.key}
              type="button"
              onClick={() => setDayIndex(index)}
              className={cn(
                "min-w-16 shrink-0 rounded-2xl px-3 py-2 text-center text-xs",
                index === dayIndex ? "bg-primary text-primary-foreground" : "bg-muted",
              )}
            >
              <div className="font-semibold">{entry.chip}</div>
              <div className="opacity-80">{DateTime.fromISO(entry.key).toFormat("LLL d")}</div>
            </button>
          ))}
        </div>

        {day ? (
          <section>
            <div className="mb-3 flex items-end justify-between">
              <div>
                <h2 className="text-xl font-semibold">{day.title}</h2>
                <p className="text-sm text-muted-foreground">{day.dateLabel}</p>
              </div>
              <span className="text-xs text-muted-foreground">
                {dayDone}/{dayTotal}
              </span>
            </div>
            <ol className="relative space-y-0">
              {day.items.map((item, index) => {
                const Icon = KIND_ICON[item.kind];
                const complete = checked.includes(item.id);
                return (
                  <li key={item.id} className="relative flex gap-3 pb-5">
                    <div className="flex w-14 shrink-0 flex-col items-end pt-1">
                      <span className="text-xs font-medium tabular-nums">{item.timeLabel}</span>
                      <span className="text-[10px] text-muted-foreground">Local</span>
                    </div>
                    <div className="relative flex flex-col items-center">
                      <span className={cn("mt-1 size-2.5 rounded-full", KIND_DOT[item.kind])} />
                      {index < day.items.length - 1 ? (
                        <span className="absolute top-4 bottom-0 w-px bg-border" />
                      ) : null}
                    </div>
                    <button
                      type="button"
                      onClick={() => toggle(item.id)}
                      className="flex min-w-0 flex-1 items-start gap-3 rounded-2xl bg-muted px-3 py-3 text-left"
                    >
                      <Icon className="mt-0.5 size-4 shrink-0 text-primary" />
                      <span className="min-w-0 flex-1">
                        <span className={cn("block text-sm font-medium", complete && "text-muted-foreground line-through")}>
                          {item.title}
                        </span>
                        {item.untilLabel ? (
                          <span className="block text-xs text-muted-foreground">{item.untilLabel}</span>
                        ) : null}
                        {item.destTimeLabel ? (
                          <span className="mt-1 flex gap-2 text-[11px]">
                            <span className="rounded-md bg-background px-1.5 py-0.5">{item.timeLabel}</span>
                            <span className="rounded-md bg-sky-100 px-1.5 py-0.5 text-sky-800 dark:bg-sky-900 dark:text-sky-100">
                              Dest {item.destTimeLabel}
                            </span>
                          </span>
                        ) : null}
                        <span className="mt-1 block text-xs leading-5 text-muted-foreground">{item.detail}</span>
                      </span>
                      <span
                        className={cn(
                          "mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full border",
                          complete ? "border-orange-400 bg-orange-400 text-white" : "border-muted-foreground/40",
                        )}
                      >
                        {complete ? <Check className="size-3.5" /> : null}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ol>
            <div className="rounded-2xl bg-muted p-4">
              <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                <Lightbulb className="size-4 text-primary" />
                Tips for today
              </div>
              <ul className="space-y-1 text-sm text-muted-foreground">
                {day.tips.map((tip) => (
                  <li key={tip}>• {tip}</li>
                ))}
              </ul>
            </div>
          </section>
        ) : null}

        <p className="text-center text-xs text-muted-foreground">{title}</p>
      </div>
    </div>
  );
}
