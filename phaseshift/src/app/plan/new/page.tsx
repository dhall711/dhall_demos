"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PlanWizard } from "@/components/plan-wizard";
import { SiteHeader } from "@/components/site-header";
import { getPlan } from "@/lib/storage";

function WizardBody() {
  const edit = useSearchParams().get("edit");
  const stored = edit ? getPlan(edit) : undefined;
  return <PlanWizard initial={stored?.input} />;
}

export default function NewPlanPage() {
  return (
    <div className="mx-auto min-h-full max-w-md bg-background">
      <SiteHeader />
      <Suspense fallback={<div className="px-4 py-10 text-sm text-muted-foreground">Loading planner…</div>}>
        <WizardBody />
      </Suspense>
    </div>
  );
}
