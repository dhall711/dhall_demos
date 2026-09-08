import { DateTime } from "luxon";
import type { GeneratedPlan, PlanInput } from "@/lib/circadian/types";

export type StoredPlan = {
  id: string;
  createdAt: string;
  title: string;
  input: PlanInput;
  plan: GeneratedPlan;
};

const KEY = "phaseshift.plans.v1";

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function listPlans(): StoredPlan[] {
  if (!canUseStorage()) return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as StoredPlan[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function getPlan(id: string): StoredPlan | undefined {
  return listPlans().find((plan) => plan.id === id);
}

export function savePlan(plan: StoredPlan): void {
  if (!canUseStorage()) return;
  const next = [plan, ...listPlans().filter((item) => item.id !== plan.id)].slice(0, 12);
  window.localStorage.setItem(KEY, JSON.stringify(next));
}

export function deletePlan(id: string): void {
  if (!canUseStorage()) return;
  window.localStorage.setItem(KEY, JSON.stringify(listPlans().filter((item) => item.id !== id)));
}

export function planTitle(input: PlanInput): string {
  const first = input.flights[0];
  const last = input.flights[input.flights.length - 1];
  if (!first) return "Untitled trip";
  const dest = last?.destinationIata ?? first.destinationIata;
  const day = DateTime.fromISO(first.departLocal).toFormat("LLL d");
  if (input.flights.length > 1) {
    return `${first.originIata} ⇄ ${dest} · ${day}`;
  }
  return `${first.originIata} → ${dest} · ${day}`;
}

export function subscribeToPlans(onStoreChange: () => void): () => void {
  if (!canUseStorage()) return () => {};
  const handler = (event: StorageEvent) => {
    if (event.key === KEY || event.key === null) onStoreChange();
  };
  window.addEventListener("storage", handler);
  return () => window.removeEventListener("storage", handler);
}

export function getPlanSnapshot(id: string): StoredPlan | null {
  return getPlan(id) ?? null;
}

export function newPlanId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `ps_${Date.now().toString(36)}`;
}
