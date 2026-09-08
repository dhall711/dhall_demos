"use client";

import { useSyncExternalStore } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PlanView } from "@/components/plan-view";
import { getPlanSnapshot, subscribeToPlans, type StoredPlan } from "@/lib/storage";

const NO_PLAN: StoredPlan | null = null;

export default function PlanDetailPage() {
  const params = useParams<{ id: string }>();
  const stored = useSyncExternalStore(
    subscribeToPlans,
    () => getPlanSnapshot(params.id),
    () => NO_PLAN,
  );

  return (
    <div className="mx-auto min-h-full max-w-md bg-background">
      {stored === null ? (
        <div className="px-4 py-16 text-center">
          <h1 className="text-3xl font-semibold">Plan not found</h1>
          <p className="mt-2 text-sm text-muted-foreground">This browser has no saved plan with that id.</p>
          <Link href="/plan/new" className="mt-6 inline-block text-primary">
            Create a new plan
          </Link>
        </div>
      ) : (
        <PlanView title={stored.title} input={stored.input} plan={stored.plan} planId={stored.id} />
      )}
    </div>
  );
}
