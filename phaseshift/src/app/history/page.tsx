"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";
import { AppShell } from "@/components/app-shell";
import { deletePlan, EMPTY_PLANS, listPlans, subscribeToPlans } from "@/lib/storage";

export default function HistoryPage() {
  const plans = useSyncExternalStore(subscribeToPlans, listPlans, () => EMPTY_PLANS);
  return (
    <AppShell title="History">
      <h1 className="text-2xl font-semibold">Saved plans</h1>
      <p className="mt-1 text-sm text-muted-foreground">Kept on this device only.</p>
      <div className="mt-5 space-y-2">
        {plans.length === 0 ? (
          <p className="rounded-2xl bg-muted p-4 text-sm text-muted-foreground">No trips yet.</p>
        ) : (
          plans.map((plan) => (
            <div key={plan.id} className="flex items-center gap-2 rounded-2xl bg-muted px-4 py-3">
              <Link href={`/plan/${plan.id}`} className="min-w-0 flex-1">
                <div className="text-sm font-medium">{plan.title}</div>
                <div className="text-xs text-muted-foreground">{plan.plan.directionLabel}</div>
              </Link>
              <button
                type="button"
                className="text-xs text-muted-foreground"
                onClick={() => deletePlan(plan.id)}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </AppShell>
  );
}
