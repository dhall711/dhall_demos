import type { ReactNode } from "react";
import Link from "next/link";
import { RemindersToggle, ThemeToggle } from "@/components/theme-toggle";

export function AppShell({
  children,
  title,
  backHref = "/",
}: {
  children: ReactNode;
  title?: string;
  backHref?: string;
}) {
  return (
    <div className="mx-auto min-h-full w-full max-w-md bg-background shadow-xl">
      <header className="flex items-center justify-between px-4 py-3">
        <RemindersToggle />
        <div className="text-sm font-semibold">{title ?? "PhaseShift"}</div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {title ? (
            <Link href={backHref} className="text-sm text-primary">
              Done
            </Link>
          ) : null}
        </div>
      </header>
      <div className="px-4 pb-10">{children}</div>
    </div>
  );
}
