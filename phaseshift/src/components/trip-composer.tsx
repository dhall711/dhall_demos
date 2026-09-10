"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { DateTime } from "luxon";
import { Gift, MapPin, Plane, ShieldCheck } from "lucide-react";
import { AirportPicker } from "@/components/airport-picker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { generatePlan } from "@/lib/circadian/engine";
import type { FlightInput, PlanInput } from "@/lib/circadian/types";
import { DEFAULT_PREFERENCES, DEFAULT_PROFILE } from "@/lib/demo";
import { getAirport } from "@/lib/airports";
import { newPlanId, planTitle, savePlan } from "@/lib/storage";
import { cn } from "@/lib/utils";

function stamp(dt: DateTime): string {
  return dt.toFormat("yyyy-LL-dd'T'HH:mm");
}

function defaultOutbound(): FlightInput {
  const depart = DateTime.now().plus({ days: 4 }).set({ hour: 13, minute: 0, second: 0, millisecond: 0 });
  const arrive = depart.plus({ days: 1 }).set({ hour: 17, minute: 0 });
  return {
    id: "out",
    originIata: "LAX",
    destinationIata: "NRT",
    departLocal: stamp(depart),
    arriveLocal: stamp(arrive),
  };
}

function defaultReturn(out: FlightInput): FlightInput {
  const destAirport = getAirport(out.destinationIata);
  const originAirport = getAirport(out.originIata);
  const depart = DateTime.fromISO(out.arriveLocal, { zone: destAirport?.tz }).plus({ days: 8 }).set({
    hour: 18,
    minute: 30,
  });
  const arrive = DateTime.fromISO(depart.toISO() ?? "", { zone: destAirport?.tz }).setZone(originAirport?.tz).set({
    hour: 12,
    minute: 30,
  });
  return {
    id: "ret",
    originIata: out.destinationIata,
    destinationIata: out.originIata,
    departLocal: stamp(depart),
    arriveLocal: stamp(arrive),
  };
}

export function TripComposer({ initial }: { initial?: PlanInput }) {
  const router = useRouter();
  const [roundTrip, setRoundTrip] = useState((initial?.flights.length ?? 1) > 1);
  const [outbound, setOutbound] = useState<FlightInput>(initial?.flights[0] ?? defaultOutbound());
  const [ret, setRet] = useState<FlightInput>(initial?.flights[1] ?? defaultReturn(initial?.flights[0] ?? defaultOutbound()));
  const [bedtime, setBedtime] = useState(initial?.profile.bedtime ?? DEFAULT_PROFILE.bedtime);
  const [waketime, setWaketime] = useState(initial?.profile.waketime ?? DEFAULT_PROFILE.waketime);
  const [useMelatonin, setUseMelatonin] = useState(initial?.preferences.useMelatonin ?? true);
  const [useCaffeine, setUseCaffeine] = useState(initial?.preferences.useCaffeine ?? true);
  const [error, setError] = useState<string | null>(null);

  const origin = getAirport(outbound.originIata);
  const dest = getAirport(outbound.destinationIata);
  const retOrigin = getAirport(ret.originIata);
  const retDest = getAirport(ret.destinationIata);

  const preview = useMemo(() => {
    const leave = DateTime.fromISO(outbound.departLocal);
    const land = DateTime.fromISO(outbound.arriveLocal);
    return {
      leave: leave.toFormat("LLL d 'at' h:mm a"),
      land: land.toFormat("LLL d 'at' h:mm a"),
      retLeave: DateTime.fromISO(ret.departLocal).toFormat("LLL d 'at' h:mm a"),
      retLand: DateTime.fromISO(ret.arriveLocal).toFormat("LLL d 'at' h:mm a"),
    };
  }, [outbound, ret]);

  function create() {
    setError(null);
    try {
      const input: PlanInput = {
        homeIata: outbound.originIata,
        profile: { ...DEFAULT_PROFILE, bedtime, waketime },
        preferences: { ...DEFAULT_PREFERENCES, useMelatonin, useCaffeine, shortTripMode: false },
        flights: roundTrip ? [outbound, { ...ret, originIata: outbound.destinationIata, destinationIata: outbound.originIata }] : [outbound],
      };
      const plan = generatePlan(input);
      const id = newPlanId();
      savePlan({ id, createdAt: new Date().toISOString(), title: planTitle(input), input, plan });
      router.push(`/plan/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not build that plan.");
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">PhaseShift</h1>
          <p className="text-sm text-muted-foreground">Plan your trip</p>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          <Gift className="size-3.5" />
          1 free trip
        </span>
      </div>

      <PlaceCard
        label="From"
        iata={outbound.originIata}
        onIata={(originIata) => setOutbound((current) => ({ ...current, originIata }))}
        when={outbound.departLocal}
        onWhen={(departLocal) => setOutbound((current) => ({ ...current, departLocal }))}
        zone={origin?.tz}
        city={origin?.city}
      />
      <PlaceCard
        label="To"
        iata={outbound.destinationIata}
        onIata={(destinationIata) => setOutbound((current) => ({ ...current, destinationIata }))}
        when={outbound.arriveLocal}
        onWhen={(arriveLocal) => setOutbound((current) => ({ ...current, arriveLocal }))}
        zone={dest?.tz}
        city={dest?.city}
      />

      <div className="grid grid-cols-2 rounded-2xl bg-muted p-1">
        {(["One way", "Round trip"] as const).map((label, index) => {
          const active = roundTrip === (index === 1);
          return (
            <button
              key={label}
              type="button"
              onClick={() => setRoundTrip(index === 1)}
              className={cn(
                "rounded-xl py-2 text-sm font-medium",
                active ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground",
              )}
            >
              {label}
            </button>
          );
        })}
      </div>

      {roundTrip ? (
        <div className="rounded-2xl bg-primary/8 px-4 py-3 text-sm">
          <div className="mb-1 flex items-center gap-2 text-primary">
            <Plane className="size-4" />
            Return flight
          </div>
          <p>
            {dest?.city} ({preview.retLeave})
            <span className="mx-2 text-muted-foreground">→</span>
            {origin?.city} ({preview.retLand})
          </p>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <Input
              type="datetime-local"
              value={ret.departLocal}
              onChange={(event) => setRet((current) => ({ ...current, departLocal: event.target.value }))}
            />
            <Input
              type="datetime-local"
              value={ret.arriveLocal}
              onChange={(event) => setRet((current) => ({ ...current, arriveLocal: event.target.value }))}
            />
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">
            {retOrigin?.tz.replaceAll("_", " ")} → {retDest?.tz.replaceAll("_", " ")}
          </p>
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label>Usual bedtime</Label>
          <Input type="time" value={bedtime} onChange={(event) => setBedtime(event.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>Usual wake</Label>
          <Input type="time" value={waketime} onChange={(event) => setWaketime(event.target.value)} />
        </div>
      </div>

      <div className="space-y-2 rounded-2xl bg-muted p-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">Optional melatonin</div>
            <div className="text-xs text-muted-foreground">0.5 mg clock-shifting dose, not a sleeping pill</div>
          </div>
          <Switch checked={useMelatonin} onCheckedChange={setUseMelatonin} />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">Caffeine windows</div>
            <div className="text-xs text-muted-foreground">Morning only, cutoff before bed</div>
          </div>
          <Switch checked={useCaffeine} onCheckedChange={setUseCaffeine} />
        </div>
      </div>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}

      <Button className="h-12 w-full rounded-2xl text-base" onClick={create}>
        Create my free plan
      </Button>
      <p className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
        <ShieldCheck className="size-3.5" />
        No card required · stored only on this device
      </p>
    </div>
  );
}

function PlaceCard({
  label,
  iata,
  onIata,
  when,
  onWhen,
  zone,
  city,
}: {
  label: string;
  iata: string;
  onIata: (iata: string) => void;
  when: string;
  onWhen: (value: string) => void;
  zone?: string;
  city?: string;
}) {
  return (
    <div className="rounded-3xl bg-muted p-4">
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <MapPin className="size-4 text-primary" />
        {label}
      </div>
      <AirportPicker id={`${label}-airport`} value={iata} onChange={onIata} />
      <div className="mt-3">
        <Input type="datetime-local" value={when} onChange={(event) => onWhen(event.target.value)} />
      </div>
      <p className="mt-2 text-xs text-primary">
        {city ? `${city} · ` : ""}
        {zone ? zone.replaceAll("_", " ") : ""}
      </p>
    </div>
  );
}
