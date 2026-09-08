"use client";

import { useSyncExternalStore } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { generatePlan } from "@/lib/circadian/engine";
import { exampleTrips } from "@/lib/demo";
import { listPlans, newPlanId, savePlan, subscribeToPlans } from "@/lib/storage";

export function HomeActions() {
  const router = useRouter();
  const saved = useSyncExternalStore(subscribeToPlans, listPlans, () => []);

  function openExample(id: string) {
    const example = exampleTrips().find((trip) => trip.id === id);
    if (!example) return;
    const plan = generatePlan(example.input);
    const planId = newPlanId();
    savePlan({
      id: planId,
      createdAt: new Date().toISOString(),
      title: example.title,
      input: example.input,
      plan,
    });
    router.push(`/plan/${planId}`);
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-3 sm:flex-row">
        <Button asChild size="lg" className="h-12 rounded-full px-6">
          <Link href="/plan/new">
            Create a jet lag plan
            <ArrowRight className="size-4" />
          </Link>
        </Button>
        <Button asChild size="lg" variant="outline" className="h-12 rounded-full px-6">
          <Link href="/science">Read the science</Link>
        </Button>
      </div>

      <div>
        <h2 className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Try a sample trip</h2>
        <div className="mt-4 grid gap-3">
          {exampleTrips().map((trip) => (
            <button
              key={trip.id}
              type="button"
              onClick={() => openExample(trip.id)}
              className="rounded-2xl border border-white/10 bg-white/5 p-4 text-left transition hover:border-primary/40 hover:bg-primary/5"
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium">{trip.title}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{trip.blurb}</div>
                </div>
                <Sun className="size-4 text-primary" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {saved.length > 0 ? (
        <div>
          <h2 className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Your plans</h2>
          <div className="mt-4 grid gap-2">
            {saved.map((plan) => (
              <Link
                key={plan.id}
                href={`/plan/${plan.id}`}
                className="flex items-center justify-between rounded-xl border border-white/10 px-4 py-3 text-sm hover:bg-white/5"
              >
                <span>{plan.title}</span>
                <span className="text-xs text-muted-foreground">{plan.plan.directionLabel}</span>
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
