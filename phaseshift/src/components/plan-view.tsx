"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { DateTime } from "luxon";
import { EVENT_PRIORITY, bodyClockMinutes, eventsOverlapping, minutesToLabel } from "@/lib/circadian/engine";
import type { GeneratedPlan, PlanEvent, PlanInput } from "@/lib/circadian/types";
import { EVENT_META } from "@/components/event-meta";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getAirport } from "@/lib/airports";
import { cn } from "@/lib/utils";

type Props = {
  title: string;
  input: PlanInput;
  plan: GeneratedPlan;
  planId: string;
};

export function PlanView({ title, input, plan, planId }: Props) {
  const range = useMemo(() => {
    const stamps = plan.events.flatMap((event) => [
      DateTime.fromISO(event.startUtc, { zone: "utc" }),
      DateTime.fromISO(event.endUtc, { zone: "utc" }),
    ]);
    const start = stamps.reduce((min, dt) => (dt < min ? dt : min));
    const end = stamps.reduce((max, dt) => (dt > max ? dt : max));
    return { start, end, hours: Math.max(1, end.diff(start, "hours").hours) };
  }, [plan.events]);

  const firstDepart = DateTime.fromISO(plan.segments[0]?.departUtc ?? range.start.toISO()!, { zone: "utc" });
  const defaultHours = Math.max(0, firstDepart.diff(range.start, "hours").hours - 2);
  const [cursorHours, setCursorHours] = useState(defaultHours);
  const [live, setLive] = useState(false);

  useEffect(() => {
    if (!live) return;
    const tick = () => {
      const now = DateTime.utc();
      if (now < range.start || now > range.end) return;
      setCursorHours(now.diff(range.start, "hours").hours);
    };
    tick();
    const id = window.setInterval(tick, 30_000);
    return () => window.clearInterval(id);
  }, [live, range.start, range.end]);

  const cursor = range.start.plus({ hours: cursorHours });
  const windowEnd = cursor.plus({ hours: 3 });
  const active = eventsOverlapping(plan.events, cursor, windowEnd).sort(
    (a, b) => EVENT_PRIORITY[b.kind] - EVENT_PRIORITY[a.kind],
  );
  const primary = active.find((event) => event.kind !== "flight") ?? active[0];
  const bodyMinutes = bodyClockMinutes(plan.homeTimezone, plan.anchors, cursor);
  const localPlace = primary?.timezone ?? plan.homeTimezone;
  const local = cursor.setZone(localPlace);
  const grouped = groupEvents(plan.events);

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-primary">{plan.directionLabel}</p>
          <h1 className="font-heading mt-1 text-3xl">{title}</h1>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">{plan.summary}</p>
        </div>
        <Button asChild variant="outline">
          <Link href={`/plan/new?edit=${planId}`}>Edit itinerary</Link>
        </Button>
      </div>

      <RouteArc input={input} />

      <section className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Local time</div>
            <div className="font-heading text-4xl tabular-nums">{local.toFormat("h:mm a")}</div>
            <div className="text-sm text-muted-foreground">
              {local.toFormat("ccc, LLL d")} · {primary?.place ?? plan.homeCity}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Body clock</div>
            <div className="font-heading text-4xl tabular-nums text-primary">{minutesToLabel(bodyMinutes)}</div>
            <div className="text-sm text-muted-foreground">
              {plan.preShiftDays ? `${plan.preShiftDays}d pre-shift · ` : ""}
              ~{plan.daysToAdapt}d to adapt
            </div>
          </div>
        </div>
        <div className="mt-5">
          <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
            <span>{range.start.setZone(localPlace).toFormat("LLL d, h:mm a")}</span>
            <button
              type="button"
              className={cn("rounded-full px-2 py-0.5", live ? "bg-primary text-primary-foreground" : "bg-white/10")}
              onClick={() => setLive((value) => !value)}
            >
              {live ? "Live" : "Preview"}
            </button>
            <span>{range.end.setZone(localPlace).toFormat("LLL d, h:mm a")}</span>
          </div>
          <Slider
            min={0}
            max={Number(range.hours.toFixed(2))}
            step={0.25}
            value={[cursorHours]}
            onValueChange={(value) => {
              setLive(false);
              setCursorHours(value[0] ?? 0);
            }}
          />
        </div>
      </section>

      <Tabs defaultValue="now" className="mt-6">
        <TabsList className="w-full">
          <TabsTrigger value="now">Next 3 hours</TabsTrigger>
          <TabsTrigger value="full">Full plan</TabsTrigger>
        </TabsList>
        <TabsContent value="now" className="mt-4 space-y-3">
          {primary ? <EventCard event={primary} large cursor={cursor} /> : (
            <p className="rounded-2xl border border-white/10 p-6 text-sm text-muted-foreground">
              No actions in this window. Sleep and light cues sit elsewhere on the timeline — scrub to explore.
            </p>
          )}
          {active
            .filter((event) => event.id !== primary?.id)
            .map((event) => (
              <EventCard key={event.id} event={event} cursor={cursor} />
            ))}
        </TabsContent>
        <TabsContent value="full" className="mt-4 space-y-8">
          {grouped.map((group) => (
            <div key={group.label}>
              <h2 className="mb-3 text-sm font-medium text-muted-foreground">{group.label}</h2>
              <div className="overflow-hidden rounded-2xl border border-white/10">
                <DayBar events={group.events} />
                <div className="divide-y divide-white/5">
                  {group.events.map((event) => (
                    <EventRow key={event.id} event={event} />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </TabsContent>
      </Tabs>

      <p className="mt-10 text-xs leading-5 text-muted-foreground">
        Educational timing based on published human phase response curves to light and melatonin (St Hilaire et
        al. 2012; Eastman & Burgess 2009). Not medical advice. Intended for healthy adults 18+.
      </p>
    </div>
  );
}

function EventCard({
  event,
  large,
  cursor,
}: {
  event: PlanEvent;
  large?: boolean;
  cursor: DateTime;
}) {
  const meta = EVENT_META[event.kind];
  const Icon = meta.Icon;
  const start = DateTime.fromISO(event.startUtc).setZone(event.timezone);
  const end = DateTime.fromISO(event.endUtc).setZone(event.timezone);
  const until = end.diff(cursor, "minutes").minutes;
  return (
    <article
      className={cn(
        "rounded-2xl border p-4",
        meta.className,
        large && "p-6",
      )}
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 rounded-full bg-black/20 p-2">
          <Icon className={large ? "size-6" : "size-4"} />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className={cn("font-medium", large && "font-heading text-2xl")}>{event.title}</h3>
            <span className="text-xs tabular-nums opacity-80">
              {start.toFormat("h:mm a")} – {end.toFormat("h:mm a")}
            </span>
          </div>
          <p className="text-xs opacity-80">
            {event.place}
            {until > 0 ? ` · ${Math.round(until)} min left in this 3-hour view` : ""}
            {event.inFlight ? " · in flight" : ""}
          </p>
          <p className={cn("mt-2 text-sm leading-6 opacity-90", large && "text-base")}>{event.detail}</p>
        </div>
      </div>
    </article>
  );
}

function EventRow({ event }: { event: PlanEvent }) {
  const meta = EVENT_META[event.kind];
  const Icon = meta.Icon;
  const start = DateTime.fromISO(event.startUtc).setZone(event.timezone);
  const end = DateTime.fromISO(event.endUtc).setZone(event.timezone);
  return (
    <div className="flex items-start gap-3 px-3 py-3">
      <span className={cn("mt-1 size-2.5 shrink-0 rounded-full", meta.bar)} />
      <Icon className="mt-0.5 size-4 shrink-0 opacity-70" />
      <div className="min-w-0 flex-1">
        <div className="flex justify-between gap-3 text-sm">
          <span className="font-medium">{event.title}</span>
          <span className="shrink-0 tabular-nums text-muted-foreground">
            {start.toFormat("h:mm a")}–{end.toFormat("h:mm a")}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          {event.place} · {event.detail}
        </p>
      </div>
    </div>
  );
}

function DayBar({ events }: { events: PlanEvent[] }) {
  const start = DateTime.fromISO(events[0].startUtc).startOf("day");
  const end = start.plus({ days: 1 });
  const span = end.toMillis() - start.toMillis();
  return (
    <div className="relative h-8 bg-black/30">
      {events.map((event) => {
        const a = DateTime.fromISO(event.startUtc);
        const b = DateTime.fromISO(event.endUtc);
        const left = ((a.toMillis() - start.toMillis()) / span) * 100;
        const width = ((b.toMillis() - a.toMillis()) / span) * 100;
        return (
          <div
            key={event.id}
            title={event.title}
            className={cn("absolute top-1 h-6 rounded-sm opacity-80", EVENT_META[event.kind].bar)}
            style={{ left: `${left}%`, width: `${Math.max(width, 0.8)}%` }}
          />
        );
      })}
    </div>
  );
}

function groupEvents(events: PlanEvent[]): { label: string; events: PlanEvent[] }[] {
  const map = new Map<string, PlanEvent[]>();
  for (const event of events) {
    const label = DateTime.fromISO(event.startUtc).setZone(event.timezone).toFormat("cccc, LLL d");
    const list = map.get(label) ?? [];
    list.push(event);
    map.set(label, list);
  }
  return [...map.entries()].map(([label, grouped]) => ({ label, events: grouped }));
}

function RouteArc({ input }: { input: PlanInput }) {
  const points = input.flights.flatMap((flight, index) => {
    const origin = getAirport(flight.originIata);
    const dest = getAirport(flight.destinationIata);
    if (!origin || !dest) return [];
    const rows = index === 0 ? [origin, dest] : [dest];
    return rows;
  });
  if (points.length < 2) return null;
  const lons = points.map((point) => point.lon);
  const lats = points.map((point) => point.lat);
  const minLon = Math.min(...lons) - 10;
  const maxLon = Math.max(...lons) + 10;
  const minLat = Math.min(...lats) - 8;
  const maxLat = Math.max(...lats) + 8;
  const project = (lon: number, lat: number) => {
    const x = ((lon - minLon) / (maxLon - minLon)) * 100;
    const y = (1 - (lat - minLat) / (maxLat - minLat)) * 36;
    return { x, y };
  };
  const projected = points.map((point) => ({ ...point, ...project(point.lon, point.lat) }));
  const d = projected
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  return (
    <svg viewBox="0 0 100 40" className="mt-5 h-24 w-full overflow-visible text-primary">
      <path d={d} fill="none" stroke="currentColor" strokeWidth="0.7" strokeDasharray="1.5 1" />
      {projected.map((point, index) => (
        <g key={`${point.iata}-${index}`}>
          <circle cx={point.x} cy={point.y} r="1.2" fill="currentColor" />
          <text x={point.x} y={point.y - 2} textAnchor="middle" fontSize="3.2" fill="currentColor">
            {point.iata}
          </text>
        </g>
      ))}
    </svg>
  );
}
