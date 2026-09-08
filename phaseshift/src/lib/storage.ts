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
const EMPTY_PLANS: StoredPlan[] = [];
const listeners = new Set<() => void>();

let cachedRaw: string | null | undefined;
let cachedPlans: StoredPlan[] = EMPTY_PLANS;

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function emit(): void {
  cachedRaw = undefined;
  listeners.forEach((listener) => listener());
}

export function listPlans(): StoredPlan[] {
  if (!canUseStorage()) return EMPTY_PLANS;
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw === cachedRaw) return cachedPlans;
    cachedRaw = raw;
    if (!raw) {
      cachedPlans = EMPTY_PLANS;
      return cachedPlans;
    }
    const parsed = JSON.parse(raw) as StoredPlan[];
    cachedPlans = Array.isArray(parsed) ? parsed : EMPTY_PLANS;
    return cachedPlans;
  } catch {
    cachedPlans = EMPTY_PLANS;
    return cachedPlans;
  }
}

export function getPlan(id: string): StoredPlan | undefined {
  return listPlans().find((plan) => plan.id === id);
}

export function savePlan(plan: StoredPlan): void {
  if (!canUseStorage()) return;
  const next = [plan, ...listPlans().filter((item) => item.id !== plan.id)].slice(0, 12);
  window.localStorage.setItem(KEY, JSON.stringify(next));
  emit();
}

export function deletePlan(id: string): void {
  if (!canUseStorage()) return;
  window.localStorage.setItem(
    KEY,
    JSON.stringify(listPlans().filter((item) => item.id !== id)),
  );
  emit();
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
  listeners.add(onStoreChange);
  if (!canUseStorage()) {
    return () => {
      listeners.delete(onStoreChange);
    };
  }
  const handler = (event: StorageEvent) => {
    if (event.key === KEY || event.key === null) emit();
  };
  window.addEventListener("storage", handler);
  return () => {
    listeners.delete(onStoreChange);
    window.removeEventListener("storage", handler);
  };
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
