const PROGRESS_KEY = "phaseshift.progress.v1";
const THEME_KEY = "phaseshift.theme";
const REMINDERS_KEY = "phaseshift.reminders";
export const EMPTY_IDS: string[] = [];
const themeListeners = new Set<() => void>();
const reminderListeners = new Set<() => void>();

let progressRaw: string | null | undefined;
let progressCache: Record<string, string[]> = {};
const progressListeners = new Set<() => void>();

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function readProgress(): Record<string, string[]> {
  if (!canUseStorage()) return {};
  const raw = window.localStorage.getItem(PROGRESS_KEY);
  if (raw === progressRaw && progressRaw !== undefined) return progressCache;
  progressRaw = raw;
  try {
    progressCache = raw ? (JSON.parse(raw) as Record<string, string[]>) : {};
  } catch {
    progressCache = {};
  }
  return progressCache;
}

function emitProgress(): void {
  progressRaw = undefined;
  progressListeners.forEach((listener) => listener());
}

export function subscribeProgress(onStoreChange: () => void): () => void {
  progressListeners.add(onStoreChange);
  return () => progressListeners.delete(onStoreChange);
}

export function getCheckedIds(planId: string): string[] {
  return readProgress()[planId] ?? EMPTY_IDS;
}

export function setCheckedIds(planId: string, ids: string[]): void {
  if (!canUseStorage()) return;
  const next = { ...readProgress(), [planId]: ids };
  window.localStorage.setItem(PROGRESS_KEY, JSON.stringify(next));
  emitProgress();
}

export function subscribeTheme(onStoreChange: () => void): () => void {
  themeListeners.add(onStoreChange);
  return () => themeListeners.delete(onStoreChange);
}

export function getTheme(): "light" | "dark" {
  if (!canUseStorage()) return "light";
  return window.localStorage.getItem(THEME_KEY) === "dark" ? "dark" : "light";
}

export function setTheme(theme: "light" | "dark"): void {
  if (!canUseStorage()) return;
  window.localStorage.setItem(THEME_KEY, theme);
  document.documentElement.classList.toggle("dark", theme === "dark");
  themeListeners.forEach((listener) => listener());
}

export function subscribeReminders(onStoreChange: () => void): () => void {
  reminderListeners.add(onStoreChange);
  return () => reminderListeners.delete(onStoreChange);
}

export function remindersEnabled(): boolean {
  if (!canUseStorage()) return false;
  return window.localStorage.getItem(REMINDERS_KEY) === "on";
}

export function setRemindersEnabled(on: boolean): void {
  if (!canUseStorage()) return;
  window.localStorage.setItem(REMINDERS_KEY, on ? "on" : "off");
  reminderListeners.forEach((listener) => listener());
}
