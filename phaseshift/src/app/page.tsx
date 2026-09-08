import { SiteHeader } from "@/components/site-header";
import { HomeActions } from "@/components/home-actions";

export default function HomePage() {
  return (
    <div className="relative min-h-full overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(228,176,74,0.18),_transparent_42%),radial-gradient(circle_at_80%_20%,_rgba(80,120,255,0.16),_transparent_35%)]" />
      <SiteHeader />
      <main className="relative mx-auto grid max-w-5xl gap-16 px-4 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:py-24">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-primary">Circadian jet lag planner</p>
          <h1 className="font-heading mt-4 text-5xl leading-[1.05] sm:text-6xl">
            Arrive on local time.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-muted-foreground">
            PhaseShift builds an hour-by-hour plan for light, darkness, sleep, melatonin, and caffeine —
            timed to your body clock, not the terminal screens. Crossing time zones is a circadian problem.
            Treat it like one.
          </p>
          <ul className="mt-8 space-y-3 text-sm text-zinc-300">
            <li>Timed light and light avoidance from human phase response curves</li>
            <li>Pre-travel shift, stopovers, round trips, and short-stay mode</li>
            <li>A 3-hour “what now” view plus the full multi-day timeline</li>
          </ul>
        </div>
        <HomeActions />
      </main>
    </div>
  );
}
