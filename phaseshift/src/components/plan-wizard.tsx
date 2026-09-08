"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { DateTime } from "luxon";
import { ArrowRight, Plus, Trash2 } from "lucide-react";
import { AirportPicker } from "@/components/airport-picker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { generatePlan } from "@/lib/circadian/engine";
import type { Chronotype, FlightInput, PlanInput, Practicality, SleepProfile } from "@/lib/circadian/types";
import { DEFAULT_PREFERENCES, DEFAULT_PROFILE, emptyFlight } from "@/lib/demo";
import { getAirport } from "@/lib/airports";
import { newPlanId, planTitle, savePlan } from "@/lib/storage";
import { cn } from "@/lib/utils";

const STEPS = ["Sleep", "Preferences", "Itinerary", "Review"] as const;

const CHRONOTYPE_COPY: Record<Chronotype, { title: string; detail: string; bed: string; wake: string }> = {
  early: {
    title: "Early",
    detail: "Natural 9 p.m.–5 a.m. energy. CBTmin sits closer to wake.",
    bed: "22:00",
    wake: "06:00",
  },
  intermediate: {
    title: "In between",
    detail: "Most travelers. A typical 11 p.m.–7 a.m. schedule.",
    bed: "23:00",
    wake: "07:00",
  },
  late: {
    title: "Late",
    detail: "Night-owl timing. CBTmin sits deeper into the sleep episode.",
    bed: "00:30",
    wake: "08:30",
  },
};

type Props = { initial?: PlanInput };

export function PlanWizard({ initial }: Props) {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [homeIata, setHomeIata] = useState(initial?.homeIata ?? "JFK");
  const [profile, setProfile] = useState<SleepProfile>(initial?.profile ?? DEFAULT_PROFILE);
  const [preferences, setPreferences] = useState(initial?.preferences ?? DEFAULT_PREFERENCES);
  const [flights, setFlights] = useState<FlightInput[]>(
    initial?.flights?.length ? initial.flights : [emptyFlight()],
  );
  const [error, setError] = useState<string | null>(null);
  const [timesTouched, setTimesTouched] = useState(Boolean(initial));

  const input: PlanInput = useMemo(
    () => ({ homeIata, profile, preferences, flights }),
    [homeIata, profile, preferences, flights],
  );

  function setChronotype(chronotype: Chronotype) {
    const preset = CHRONOTYPE_COPY[chronotype];
    setProfile((current) => ({
      ...current,
      chronotype,
      bedtime: timesTouched ? current.bedtime : preset.bed,
      waketime: timesTouched ? current.waketime : preset.wake,
    }));
  }

  function updateFlight(id: string, patch: Partial<FlightInput>) {
    setFlights((current) => current.map((flight) => (flight.id === id ? { ...flight, ...patch } : flight)));
  }

  function addFlight() {
    const last = flights[flights.length - 1];
    const next = emptyFlight(last?.destinationIata ?? "LHR", "CDG");
    if (last) {
      const arrive = DateTime.fromISO(last.arriveLocal);
      next.departLocal = arrive.plus({ hours: 3 }).toFormat("yyyy-LL-dd'T'HH:mm");
      next.arriveLocal = arrive.plus({ hours: 6 }).toFormat("yyyy-LL-dd'T'HH:mm");
    }
    setFlights((current) => [...current, next]);
  }

  function makeRoundTrip() {
    const first = flights[0];
    if (!first) return;
    const dest = DateTime.fromISO(first.arriveLocal).plus({ days: 6 }).set({ hour: 11, minute: 0 });
    const home = dest.set({ hour: 14, minute: 20 });
    setFlights([
      first,
      {
        id: `ret-${Date.now().toString(36)}`,
        originIata: first.destinationIata,
        destinationIata: first.originIata,
        departLocal: dest.toFormat("yyyy-LL-dd'T'HH:mm"),
        arriveLocal: home.toFormat("yyyy-LL-dd'T'HH:mm"),
      },
    ]);
  }

  function generate() {
    setError(null);
    try {
      if (flights.some((flight) => !flight.originIata || !flight.destinationIata)) {
        throw new Error("Every flight needs an origin and destination.");
      }
      const plan = generatePlan(input);
      const id = newPlanId();
      savePlan({
        id,
        createdAt: new Date().toISOString(),
        title: planTitle(input),
        input,
        plan,
      });
      router.push(`/plan/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not build that plan.");
      setStep(2);
    }
  }

  return (
    <div className="mx-auto w-full max-w-lg px-4 py-8">
      <div className="mb-8 flex items-center gap-2">
        {STEPS.map((label, index) => (
          <button
            key={label}
            type="button"
            onClick={() => setStep(index)}
            className={cn(
              "flex-1 rounded-full py-1.5 text-center text-[11px] tracking-wide uppercase",
              index === step ? "bg-primary text-primary-foreground" : "bg-white/5 text-muted-foreground",
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {step === 0 ? (
        <section className="space-y-6">
          <div>
            <h1 className="font-heading text-3xl">Your home clock</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Plans are timed to your body, not the airport clock. Usual sleep and chronotype set core body
              temperature minimum — the hinge of the light plan.
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="home">Home base</Label>
            <AirportPicker id="home" value={homeIata} onChange={setHomeIata} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="bed">Usual bedtime</Label>
              <Input
                id="bed"
                type="time"
                value={profile.bedtime}
                onChange={(event) => {
                  setTimesTouched(true);
                  setProfile((current) => ({ ...current, bedtime: event.target.value }));
                }}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="wake">Usual wake</Label>
              <Input
                id="wake"
                type="time"
                value={profile.waketime}
                onChange={(event) => {
                  setTimesTouched(true);
                  setProfile((current) => ({ ...current, waketime: event.target.value }));
                }}
              />
            </div>
          </div>
          <div className="grid gap-2">
            <Label>Chronotype</Label>
            {(["early", "intermediate", "late"] as Chronotype[]).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setChronotype(key)}
                className={cn(
                  "rounded-2xl border px-4 py-3 text-left",
                  profile.chronotype === key
                    ? "border-primary bg-primary/10"
                    : "border-white/10 bg-white/5 hover:bg-white/8",
                )}
              >
                <div className="text-sm font-medium">{CHRONOTYPE_COPY[key].title}</div>
                <div className="text-xs text-muted-foreground">{CHRONOTYPE_COPY[key].detail}</div>
              </button>
            ))}
          </div>
        </section>
      ) : null}

      {step === 1 ? (
        <section className="space-y-6">
          <div>
            <h1 className="font-heading text-3xl">How you want to shift</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Light and darkness do the heavy lifting. Melatonin and caffeine are optional tools, timed so they
              do not shove the clock the wrong way.
            </p>
          </div>
          <ToggleRow
            label="Melatonin microdose"
            detail="0.5 mg in the advance window. Not a sleeping pill."
            checked={preferences.useMelatonin}
            onCheckedChange={(useMelatonin) => setPreferences((current) => ({ ...current, useMelatonin }))}
          />
          <ToggleRow
            label="Caffeine windows"
            detail="Allowed after waking, cut off well before the next sleep."
            checked={preferences.useCaffeine}
            onCheckedChange={(useCaffeine) => setPreferences((current) => ({ ...current, useCaffeine }))}
          />
          <ToggleRow
            label="Short-trip mode"
            detail="If you are home again within about four days, stay closer to home time."
            checked={preferences.shortTripMode}
            onCheckedChange={(shortTripMode) => setPreferences((current) => ({ ...current, shortTripMode }))}
          />
          <div>
            <Label>Real-world mode</Label>
            <div className="mt-2 grid gap-2">
              {(
                [
                  ["easy", "Easy", "Rounded times, lighter pre-shift."],
                  ["balanced", "Balanced", "The default for most trips."],
                  ["strict", "Strict", "Tighter windows and more pre-travel shift."],
                ] as [Practicality, string, string][]
              ).map(([key, title, detail]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setPreferences((current) => ({ ...current, practicality: key }))}
                  className={cn(
                    "rounded-2xl border px-4 py-3 text-left",
                    preferences.practicality === key
                      ? "border-primary bg-primary/10"
                      : "border-white/10 bg-white/5",
                  )}
                >
                  <div className="text-sm font-medium">{title}</div>
                  <div className="text-xs text-muted-foreground">{detail}</div>
                </button>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {step === 2 ? (
        <section className="space-y-6">
          <div>
            <h1 className="font-heading text-3xl">Itinerary</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Times are local at each airport. Add every segment — stopovers change where you see light.
            </p>
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={makeRoundTrip}>
              Make round trip
            </Button>
            <Button type="button" variant="outline" onClick={addFlight}>
              <Plus className="size-4" />
              Add segment
            </Button>
          </div>
          <div className="space-y-4">
            {flights.map((flight, index) => (
              <div key={flight.id} className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <div className="text-xs uppercase tracking-wide text-muted-foreground">
                    Flight {index + 1}
                  </div>
                  {flights.length > 1 ? (
                    <button
                      type="button"
                      className="text-muted-foreground hover:text-foreground"
                      onClick={() => setFlights((current) => current.filter((item) => item.id !== flight.id))}
                    >
                      <Trash2 className="size-4" />
                    </button>
                  ) : null}
                </div>
                <div className="grid grid-cols-[1fr_auto_1fr] items-end gap-2">
                  <div className="space-y-2">
                    <Label>From</Label>
                    <AirportPicker
                      id={`${flight.id}-from`}
                      value={flight.originIata}
                      onChange={(originIata) => updateFlight(flight.id, { originIata })}
                    />
                  </div>
                  <ArrowRight className="mb-2 size-4 text-muted-foreground" />
                  <div className="space-y-2">
                    <Label>To</Label>
                    <AirportPicker
                      id={`${flight.id}-to`}
                      value={flight.destinationIata}
                      onChange={(destinationIata) => updateFlight(flight.id, { destinationIata })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label>Depart (local)</Label>
                    <Input
                      type="datetime-local"
                      value={flight.departLocal}
                      onChange={(event) => updateFlight(flight.id, { departLocal: event.target.value })}
                    />
                    <p className="text-[11px] text-muted-foreground">
                      {getAirport(flight.originIata)?.tz.replace("_", " ")}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label>Arrive (local)</Label>
                    <Input
                      type="datetime-local"
                      value={flight.arriveLocal}
                      onChange={(event) => updateFlight(flight.id, { arriveLocal: event.target.value })}
                    />
                    <p className="text-[11px] text-muted-foreground">
                      {getAirport(flight.destinationIata)?.tz.replace("_", " ")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {step === 3 ? (
        <section className="space-y-6">
          <div>
            <h1 className="font-heading text-3xl">Review</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              We will build a timed light, sleep, melatonin, and caffeine plan from published circadian phase
              response curves — not generic “drink water and walk in the sun” advice.
            </p>
          </div>
          <div className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm">
            <Row label="Home" value={`${getAirport(homeIata)?.city} · ${profile.bedtime}–${profile.waketime}`} />
            <Row label="Chronotype" value={CHRONOTYPE_COPY[profile.chronotype].title} />
            <Row
              label="Tools"
              value={[
                preferences.useMelatonin ? "melatonin" : null,
                preferences.useCaffeine ? "caffeine" : null,
                preferences.shortTripMode ? "short-trip mode" : null,
                preferences.practicality,
              ]
                .filter(Boolean)
                .join(" · ")}
            />
            {flights.map((flight) => (
              <Row
                key={flight.id}
                label="Flight"
                value={`${flight.originIata} → ${flight.destinationIata}  ${flight.departLocal.replace("T", " ")}`}
              />
            ))}
          </div>
        </section>
      ) : null}

      {error ? <p className="mt-4 text-sm text-destructive">{error}</p> : null}

      <div className="mt-8 flex justify-between">
        <Button type="button" variant="ghost" disabled={step === 0} onClick={() => setStep((value) => value - 1)}>
          Back
        </Button>
        {step < 3 ? (
          <Button type="button" onClick={() => setStep((value) => value + 1)}>
            Continue
          </Button>
        ) : (
          <Button type="button" onClick={generate}>
            Build my plan
          </Button>
        )}
      </div>
    </div>
  );
}

function ToggleRow({
  label,
  detail,
  checked,
  onCheckedChange,
}: {
  label: string;
  detail: string;
  checked: boolean;
  onCheckedChange: (value: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
      <div>
        <div className="text-sm font-medium">{label}</div>
        <div className="text-xs text-muted-foreground">{detail}</div>
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right">{value}</span>
    </div>
  );
}
