import { SiteHeader } from "@/components/site-header";

export default function SciencePage() {
  return (
    <div className="min-h-full">
      <SiteHeader />
      <article className="mx-auto max-w-2xl px-4 py-12 leading-7">
        <p className="text-xs uppercase tracking-[0.28em] text-primary">The science</p>
        <h1 className="font-heading mt-3 text-4xl">Jet lag is a clock problem</h1>
        <p className="mt-6 text-muted-foreground">
          Your brain contains a master pacemaker — the suprachiasmatic nucleus — that runs close to, but not
          exactly, 24 hours. Light reaching the eyes is the strongest signal that resets that clock each day.
          Crossing time zones moves the sun faster than the pacemaker can follow. The result is jet lag:
          sleep, alertness, digestion, mood, and performance all fire at the wrong local hour.
        </p>
        <h2 className="font-heading mt-10 text-2xl">Light has a direction</h2>
        <p className="mt-4 text-muted-foreground">
          A phase response curve (PRC) describes how a pulse of light moves the clock depending on when it
          lands relative to core body temperature minimum (CBTmin), typically a couple of hours before your
          usual wake time. Light in the late biological night, before CBTmin, delays the clock (useful for
          flying west). Light after CBTmin advances it (useful for flying east). Light at the wrong moment
          makes jet lag worse — including a sunny breakfast that still sits on the delay side of your PRC.
        </p>
        <h2 className="font-heading mt-10 text-2xl">Sleep is darkness</h2>
        <p className="mt-4 text-muted-foreground">
          Closing your eyes blocks the light signal. Sleeping through a seek-light window, or staying awake
          through an avoid-light window, shifts you the wrong way. That is why “sleep as much as possible on
          the plane” is not a strategy. Sleep is scheduled as part of the light-dark plan.
        </p>
        <h2 className="font-heading mt-10 text-2xl">Melatonin and caffeine</h2>
        <p className="mt-4 text-muted-foreground">
          Exogenous melatonin has its own PRC, roughly opposite to light, and a clock-shifting dose is about
          0.5 mg — not a 3–10 mg hypnotic. PhaseShift only recommends it when you are advancing. Caffeine does
          not reset the pacemaker; it masks sleepiness. Used too late, it wrecks the next sleep window and
          therefore the next light-dark cycle.
        </p>
        <h2 className="font-heading mt-10 text-2xl">How PhaseShift times advice</h2>
        <p className="mt-4 text-muted-foreground">
          The planner estimates CBTmin from your usual sleep and chronotype, measures the timezone jump at
          each landing (including DST), and walks your clock forward in daily steps of roughly 1–1.5 hours
          east or 1.5–2 hours west. Each step places a 4-hour seek-light block and a 4-hour avoid-light block
          around that day’s CBTmin, then layers sleep, optional melatonin, caffeine cutoffs, and short naps.
          Short stays can skip a full shift so you are not adapting twice in 48 hours.
        </p>
        <p className="mt-8 text-sm text-muted-foreground">
          Key references: St Hilaire et al., J Physiol 2012 (1-hour light PRC); Eastman & Burgess, Sleep Med
          Clin 2009; Czeisler et al., Science 1999; Sack et al., Sleep 2007. This product is not affiliated
          with Timeshifter and is not medical advice.
        </p>
      </article>
    </div>
  );
}
