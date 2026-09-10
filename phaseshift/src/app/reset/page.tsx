"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import { Check, MoonStar } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { generateResetSleep } from "@/lib/circadian/reset-sleep";
import { EMPTY_IDS, getCheckedIds, setCheckedIds, subscribeProgress } from "@/lib/prefs";
import { cn } from "@/lib/utils";

const RESET_ID = "reset-sleep";

export default function ResetSleepPage() {
  const [lastWake, setLastWake] = useState("11:15");
  const [targetWake, setTargetWake] = useState("07:00");
  const [useMelatonin, setUseMelatonin] = useState(true);
  const [built, setBuilt] = useState(false);
  const result = useMemo(
    () => generateResetSleep({ lastWake, targetWake, useMelatonin }),
    [lastWake, targetWake, useMelatonin],
  );
  const [dayIndex, setDayIndex] = useState(0);
  const checked = useSyncExternalStore(
    subscribeProgress,
    () => getCheckedIds(RESET_ID),
    () => EMPTY_IDS,
  );
  const day = result.days[dayIndex] ?? result.days[0];
  const allIds = result.days.flatMap((entry) => entry.actions.map((action) => action.id));
  const percent = allIds.length
    ? Math.round((allIds.filter((id) => checked.includes(id)).length / allIds.length) * 100)
    : 0;

  function toggle(id: string) {
    const next = checked.includes(id) ? checked.filter((item) => item !== id) : [...checked, id];
    setCheckedIds(RESET_ID, next);
  }

  return (
    <AppShell title="Reset sleep">
      <div className="flex items-center gap-2">
        <MoonStar className="size-5 text-orange-500" />
        <h1 className="text-2xl font-semibold">Recovery plan</h1>
        <span className="ml-auto rounded-full bg-orange-100 px-2 py-0.5 text-xs text-orange-800">{percent}%</span>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        Shift a drifted wake time back to your target without a flight. Educational timing only.
      </p>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label>Last wake-up</Label>
          <Input type="time" value={lastWake} onChange={(event) => setLastWake(event.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>Target wake-up</Label>
          <Input type="time" value={targetWake} onChange={(event) => setTargetWake(event.target.value)} />
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between rounded-2xl bg-muted px-3 py-2">
        <span className="text-sm">Optional melatonin</span>
        <Switch checked={useMelatonin} onCheckedChange={setUseMelatonin} />
      </div>
      <Button className="mt-4 h-11 w-full rounded-2xl" onClick={() => setBuilt(true)}>
        Build recovery plan
      </Button>

      {built ? (
        <div className="mt-6 space-y-4">
          <div className="rounded-3xl bg-muted p-4">
            <div className="text-sm font-medium">{result.days.length}-day recovery roadmap</div>
            <p className="mt-1 text-sm text-muted-foreground">
              Last wake-up {lastWake} → target {targetWake}
            </p>
            <p className="mt-2 text-sm">{result.summary}</p>
          </div>
          <div className="flex gap-2 overflow-x-auto">
            {result.days.map((entry, index) => (
              <button
                key={entry.key}
                type="button"
                onClick={() => setDayIndex(index)}
                className={cn(
                  "min-w-20 shrink-0 rounded-2xl px-3 py-2 text-xs",
                  index === dayIndex ? "bg-orange-500 text-white" : "bg-muted",
                )}
              >
                <div className="font-semibold">{entry.chip}</div>
                <div>{entry.dateLabel.replace(/^\w+, /, "")}</div>
              </button>
            ))}
          </div>
          {day ? (
            <div>
              <div className="mb-3 flex justify-between text-sm">
                <span className="font-medium">
                  {day.title} · {day.dateLabel}
                </span>
                <span className="text-muted-foreground">
                  {day.actions.filter((action) => checked.includes(action.id)).length}/{day.actions.length}
                </span>
              </div>
              <div className="space-y-2">
                {day.actions.map((action) => {
                  const complete = checked.includes(action.id);
                  return (
                    <button
                      key={action.id}
                      type="button"
                      onClick={() => toggle(action.id)}
                      className="flex w-full items-start gap-3 rounded-2xl bg-muted px-3 py-3 text-left"
                    >
                      <span className="min-w-0 flex-1">
                        <span className={cn("block text-sm font-medium", complete && "line-through text-muted-foreground")}>
                          {action.title}
                        </span>
                        <span className="text-xs text-orange-600">{action.startLabel}</span>
                        <span className="mt-1 block text-xs text-muted-foreground">{action.detail}</span>
                      </span>
                      <span
                        className={cn(
                          "mt-0.5 flex size-6 items-center justify-center rounded-full border",
                          complete ? "border-orange-400 bg-orange-400 text-white" : "border-muted-foreground/40",
                        )}
                      >
                        {complete ? <Check className="size-3.5" /> : null}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </AppShell>
  );
}
