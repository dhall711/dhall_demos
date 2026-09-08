"use client";

import { useSyncExternalStore } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PlanView } from "@/components/plan-view";
import { SiteHeader } from "@/components/site-header";
import { getPlanSnapshot, subscribeToPlans } from "@/lib/storage";

export default function PlanDetailPage() {
  const params = useParams<{ id: string }>();
  const stored = useSyncExternalStore(
    subscribeToPlans,
    () => getPlanSnapshot(params.id),
    () => null,
  );

  return (
    <div className="min-h-full">
      <SiteHeader />
      {stored === null ? (
        <div className="px-4 py-16 text-center">
          <h1 className="font-heading text-3xl">Plan not found</h1>
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
