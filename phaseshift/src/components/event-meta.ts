import type { EventKind } from "@/lib/circadian/types";
import {
  BedDouble,
  Coffee,
  Moon,
  Plane,
  Sparkles,
  Sun,
  SunMoon,
  Timer,
} from "lucide-react";

export const EVENT_META: Record<
  EventKind,
  { label: string; className: string; bar: string; Icon: typeof Sun }
> = {
  "seek-light": {
    label: "Seek light",
    className: "bg-amber-400/15 text-amber-200 border-amber-400/30",
    bar: "bg-amber-400",
    Icon: Sun,
  },
  "avoid-light": {
    label: "Avoid light",
    className: "bg-indigo-400/15 text-indigo-200 border-indigo-400/30",
    bar: "bg-indigo-400",
    Icon: SunMoon,
  },
  sleep: {
    label: "Sleep",
    className: "bg-sky-500/15 text-sky-200 border-sky-400/30",
    bar: "bg-sky-500",
    Icon: BedDouble,
  },
  nap: {
    label: "Nap",
    className: "bg-teal-400/15 text-teal-200 border-teal-400/30",
    bar: "bg-teal-400",
    Icon: Moon,
  },
  caffeine: {
    label: "Caffeine",
    className: "bg-orange-300/15 text-orange-100 border-orange-300/30",
    bar: "bg-orange-300",
    Icon: Coffee,
  },
  melatonin: {
    label: "Melatonin",
    className: "bg-violet-400/15 text-violet-200 border-violet-400/30",
    bar: "bg-violet-400",
    Icon: Sparkles,
  },
  flight: {
    label: "Flight",
    className: "bg-white/5 text-zinc-200 border-white/15",
    bar: "bg-zinc-400",
    Icon: Plane,
  },
  aligned: {
    label: "Aligned",
    className: "bg-emerald-400/15 text-emerald-200 border-emerald-400/30",
    bar: "bg-emerald-400",
    Icon: Timer,
  },
};
