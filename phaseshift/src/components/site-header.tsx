import type { ReactNode } from "react";
import Link from "next/link";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link href="/" className={`inline-flex items-center gap-2 ${className}`}>
      <span className="relative flex size-8 items-center justify-center rounded-full border border-primary/40 bg-primary/15">
        <span className="absolute inset-1 rounded-full border border-dashed border-primary/50" />
        <span className="size-2 rounded-full bg-primary" />
      </span>
      <span className="font-heading text-lg tracking-tight">PhaseShift</span>
    </Link>
  );
}

export function SiteHeader({ action }: { action?: ReactNode }) {
  return (
    <header className="sticky top-0 z-40 border-b border-white/5 bg-[#071018]/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <Logo />
        <nav className="flex items-center gap-4 text-sm text-muted-foreground">
          <Link href="/science" className="hover:text-foreground">
            Science
          </Link>
          <Link href="/plan/new" className="hover:text-foreground">
            New plan
          </Link>
          {action}
        </nav>
      </div>
    </header>
  );
}
