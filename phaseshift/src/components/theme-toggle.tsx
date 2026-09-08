"use client";

import { useSyncExternalStore } from "react";
import { Bell, Moon, Sun } from "lucide-react";
import { getTheme, remindersEnabled, setRemindersEnabled, setTheme, subscribeReminders, subscribeTheme } from "@/lib/prefs";

export function ThemeScript() {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: `document.documentElement.classList.toggle('dark', localStorage.getItem('phaseshift.theme')==='dark')`,
      }}
    />
  );
}

export function ThemeToggle() {
  const theme = useSyncExternalStore(subscribeTheme, getTheme, () => "light" as const);
  return (
    <button
      type="button"
      className="flex size-9 items-center justify-center rounded-full bg-muted text-foreground"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </button>
  );
}

export function RemindersToggle() {
  const on = useSyncExternalStore(subscribeReminders, remindersEnabled, () => false);
  async function toggle() {
    if (!on && typeof Notification !== "undefined") {
      await Notification.requestPermission();
    }
    setRemindersEnabled(!on);
  }
  return (
    <button
      type="button"
      className="flex size-9 items-center justify-center rounded-full bg-muted text-foreground"
      onClick={toggle}
      aria-label="Reminders"
    >
      <Bell className={`size-4 ${on ? "text-primary" : ""}`} />
    </button>
  );
}
