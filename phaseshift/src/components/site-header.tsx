import type { ReactNode } from "react";
import Link from "next/link";
import { RemindersToggle, ThemeToggle } from "@/components/theme-toggle";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link href="/" className={`text-sm font-semibold ${className}`}>
      PhaseShift
    </Link>
  );
}

export function SiteHeader({ action }: { action?: ReactNode }) {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-md items-center justify-between px-4">
        <Logo />
        <nav className="flex items-center gap-3 text-sm text-muted-foreground">
          <Link href="/science" className="hover:text-foreground">
            Science
          </Link>
          <Link href="/history" className="hover:text-foreground">
            History
          </Link>
          <RemindersToggle />
          <ThemeToggle />
          {action}
        </nav>
      </div>
    </header>
  );
}
