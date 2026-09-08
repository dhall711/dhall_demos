"use client";

import { useState } from "react";
import { AIRPORTS, airportLabel, searchAirports, type Airport } from "@/lib/airports";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

type Props = {
  id: string;
  value: string;
  onChange: (iata: string) => void;
  placeholder?: string;
};

export function AirportPicker({ id, value, onChange, placeholder }: Props) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const selected = AIRPORTS.find((airport) => airport.iata === value);
  const results = searchAirports(query, 8);

  function choose(airport: Airport) {
    onChange(airport.iata);
    setQuery(`${airport.city} (${airport.iata})`);
    setOpen(false);
  }

  return (
    <div className="relative">
      <Input
        id={id}
        value={open ? query : selected ? airportLabel(selected) : query}
        placeholder={placeholder ?? "City or IATA"}
        autoComplete="off"
        onFocus={() => {
          setQuery("");
          setOpen(true);
        }}
        onBlur={() => {
          window.setTimeout(() => setOpen(false), 120);
        }}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
      />
      {open ? (
        <ul className="absolute z-30 mt-1 max-h-64 w-full overflow-auto rounded-xl border border-border bg-popover p-1 shadow-lg">
          {results.map((airport) => (
            <li key={airport.iata}>
              <button
                type="button"
                className={cn(
                  "flex w-full items-start justify-between gap-3 rounded-lg px-3 py-2 text-left text-sm hover:bg-muted",
                  airport.iata === value && "bg-muted",
                )}
                onMouseDown={(event) => {
                  event.preventDefault();
                  choose(airport);
                }}
              >
                <span>
                  <span className="font-medium">{airport.city}</span>
                  <span className="mt-0.5 block text-xs text-muted-foreground">
                    {airport.name}
                  </span>
                </span>
                <span className="font-mono text-xs text-primary">{airport.iata}</span>
              </button>
            </li>
          ))}
          {results.length === 0 ? (
            <li className="px-3 py-2 text-sm text-muted-foreground">No airports match.</li>
          ) : null}
        </ul>
      ) : null}
    </div>
  );
}
