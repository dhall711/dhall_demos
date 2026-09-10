"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { History, MoonStar } from "lucide-react";
import { TripComposer } from "@/components/trip-composer";
import { AppShell } from "@/components/app-shell";
import { exampleTrips } from "@/lib/demo";
import { generatePlan } from "@/lib/circadian/engine";
import { newPlanId, savePlan } from "@/lib/storage";

export default function HomePage() {
  const router = useRouter();

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
    <AppShell>
      <TripComposer />
      <div className="mt-8 grid grid-cols-2 gap-3">
        <Link href="/history" className="rounded-2xl bg-muted px-4 py-3 text-sm">
          <History className="mb-1 size-4 text-primary" />
          History
        </Link>
        <Link href="/reset" className="rounded-2xl bg-muted px-4 py-3 text-sm">
          <MoonStar className="mb-1 size-4 text-primary" />
          Reset sleep
        </Link>
      </div>
      <div className="mt-6">
        <h2 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Try a sample</h2>
        <div className="mt-2 space-y-2">
          {exampleTrips().map((trip) => (
            <button
              key={trip.id}
              type="button"
              onClick={() => openExample(trip.id)}
              className="w-full rounded-2xl bg-muted px-4 py-3 text-left text-sm"
            >
              <div className="font-medium">{trip.title}</div>
              <div className="text-xs text-muted-foreground">{trip.blurb}</div>
            </button>
          ))}
        </div>
      </div>
      <p className="mt-8 text-center text-xs text-muted-foreground">
        <Link href="/science" className="text-primary">
          How the timing works
        </Link>
        {" · "}
        <Link href="/plan/new" className="text-primary">
          Advanced itinerary
        </Link>
      </p>
    </AppShell>
  );
}
