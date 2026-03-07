"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TimeChart, HorizontalBarChart, TokenBarChart, shortenComponentLabel, shortenAgentLabel } from "@/components/charts";
import { Zap, Users, Hash, DollarSign, X, ChevronDown, Calendar, MessageSquare } from "lucide-react";

interface GroupedRow {
  NAME: string;
  CREDITS: number;
  COST?: number;
}

interface MonthlyRow {
  PERIOD: string;
  CREDITS: number;
  CUMULATIVE_CREDITS: number;
  COST?: number;
  CUMULATIVE_COST?: number;
}

interface DetailRow {
  START_TIME: string;
  END_USER_NAME: string;
  SERVICE_TYPE: string;
  COST_COMPONENT: string;
  COMPONENT_DESCRIPTION: string;
  WAREHOUSE_NAME: string;
  COMPONENT_OBJECT_NAME: string;
  COMPONENT_CREDITS: number;
  INPUT_TOKENS: number;
  OUTPUT_TOKENS: number;
  TOTAL_TOKENS: number;
}

interface Totals {
  TOTAL_CREDITS: number;
  UNIQUE_USERS: number;
  TOTAL_QUERIES: number;
  SERVICE_TYPES: number;
  TOTAL_INPUT_TOKENS: number;
  TOTAL_OUTPUT_TOKENS: number;
  TOTAL_TOKENS: number;
}

interface TokenServiceRow {
  NAME: string;
  INPUT_TOKENS: number;
  OUTPUT_TOKENS: number;
  TOTAL_TOKENS: number;
}

interface DashboardData {
  totals: Totals;
  monthly: MonthlyRow[];
  daily: MonthlyRow[];
  weekly: MonthlyRow[];
  yearly: MonthlyRow[];
  byService: GroupedRow[];
  byComponent: GroupedRow[];
  byUser: GroupedRow[];
  byWarehouse: GroupedRow[];
  byObject: GroupedRow[];
  byAgent: GroupedRow[];
  detail: DetailRow[];
  tokensByService: TokenServiceRow[];
}

const DEFAULT_CREDIT_RATE = 3.0;

function LoadingSkeleton() {
  return (
    <div className="space-y-6 p-8 max-w-[1440px] mx-auto">
      <div className="grid grid-cols-4 gap-5">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-[380px] rounded-xl" />
      <div className="grid grid-cols-3 gap-5">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-[320px] rounded-xl" />
        ))}
      </div>
    </div>
  );
}

const SERVICE_COLORS: Record<string, string> = {
  "CORTEX AISQL": "#ef4444",
  "CORTEX ANALYST": "#8b5cf6",
  "CORTEX AGENT": "#a855f7",
  "CORTEX SEARCH": "#06b6d4",
  "FINE TUNING": "#10b981",
  "DOCUMENT AI": "#eab308",
  "CORTEX REST API": "#f97316",
  "CORTEX CODE CLI": "#3b82f6",
  "PROVISIONED THROUGHPUT": "#6366f1",
};

function ServiceBadge({ type }: { type: string }) {
  const bg = SERVICE_COLORS[type] || "#64748b";
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium text-white whitespace-nowrap"
      style={{ backgroundColor: bg }}
    >
      {type}
    </span>
  );
}

function MultiSelect({
  label,
  options,
  selected,
  onChange,
  displayFn,
}: {
  label: string;
  options: string[];
  selected: string[];
  onChange: (val: string[]) => void;
  displayFn?: (val: string) => string;
}) {
  const display = displayFn || ((v: string) => v);
  const [open, setOpen] = useState(false);
  const allSelected = selected.length === 0;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors min-w-[160px]"
      >
        <span className="truncate">
          {allSelected ? label : `${label} (${selected.length})`}
        </span>
        <ChevronDown className="h-3.5 w-3.5 ml-auto text-slate-400 shrink-0" />
      </button>

      {!allSelected && (
        <button
          onClick={(e) => { e.stopPropagation(); onChange([]); }}
          className="absolute -top-1.5 -right-1.5 bg-blue-600 text-white rounded-full p-0.5 hover:bg-blue-700 transition-colors z-10"
        >
          <X className="h-3 w-3" />
        </button>
      )}

      {open && (
        <>
          <div className="fixed inset-0 z-20" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-full mt-1 z-30 w-64 max-h-72 overflow-auto rounded-lg border border-slate-200 bg-white shadow-xl">
            <button
              onClick={() => { onChange([]); setOpen(false); }}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${allSelected ? "bg-blue-50 text-blue-700 font-semibold" : "text-slate-600"}`}
            >
              All
            </button>
            {options.map((opt) => {
              const isActive = selected.includes(opt);
              return (
                <button
                  key={opt}
                  onClick={() => {
                    if (isActive) {
                      const next = selected.filter((s) => s !== opt);
                      onChange(next);
                    } else {
                      onChange([...selected, opt]);
                    }
                  }}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors flex items-center gap-2 ${isActive ? "bg-blue-50 text-blue-700 font-medium" : "text-slate-600"}`}
                >
                  <span className={`h-4 w-4 rounded border flex items-center justify-center shrink-0 ${isActive ? "bg-blue-600 border-blue-600" : "border-slate-300"}`}>
                    {isActive && <svg className="h-3 w-3 text-white" viewBox="0 0 12 12"><path d="M10 3L4.5 8.5L2 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  </span>
                  <span className="truncate">{display(opt)}</span>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

function groupBy(rows: DetailRow[], keyFn: (r: DetailRow) => string): GroupedRow[] {
  const map = new Map<string, number>();
  for (const r of rows) {
    const k = keyFn(r);
    map.set(k, (map.get(k) || 0) + (r.COMPONENT_CREDITS ?? 0));
  }
  return Array.from(map.entries())
    .map(([NAME, CREDITS]) => ({ NAME, CREDITS: Math.round(CREDITS * 100) / 100 }))
    .sort((a, b) => b.CREDITS - a.CREDITS);
}

type TimeGranularity = "daily" | "weekly" | "monthly" | "yearly";

function getWeekStart(dateStr: string): string {
  const d = new Date(dateStr.slice(0, 10) + "T00:00:00");
  const day = d.getDay();
  d.setDate(d.getDate() - day);
  return d.toISOString().slice(0, 10);
}

function groupByPeriod(rows: DetailRow[], granularity: TimeGranularity): MonthlyRow[] {
  const map = new Map<string, number>();
  for (const r of rows) {
    let period: string;
    switch (granularity) {
      case "daily":
        period = r.START_TIME.slice(0, 10);
        break;
      case "weekly":
        period = getWeekStart(r.START_TIME);
        break;
      case "monthly":
        period = r.START_TIME.slice(0, 7) + "-01";
        break;
      case "yearly":
        period = r.START_TIME.slice(0, 4) + "-01-01";
        break;
    }
    map.set(period, (map.get(period) || 0) + (r.COMPONENT_CREDITS ?? 0));
  }
  const sorted = Array.from(map.entries())
    .map(([PERIOD, CREDITS]) => ({ PERIOD, CREDITS: Math.round(CREDITS * 100) / 100 }))
    .sort((a, b) => a.PERIOD.localeCompare(b.PERIOD));

  let cum = 0;
  return sorted.map((r) => {
    cum += r.CREDITS;
    return { ...r, CUMULATIVE_CREDITS: Math.round(cum * 100) / 100 };
  });
}

function addCost<T extends { CREDITS: number }>(rows: T[], rate: number): (T & { COST: number })[] {
  return rows.map((r) => ({ ...r, COST: Math.round(r.CREDITS * rate * 100) / 100 }));
}

function addMonthlyCost(rows: MonthlyRow[], rate: number): MonthlyRow[] {
  return rows.map((r) => ({
    ...r,
    COST: Math.round(r.CREDITS * rate * 100) / 100,
    CUMULATIVE_COST: Math.round(r.CUMULATIVE_CREDITS * rate * 100) / 100,
  }));
}

export default function Dashboard() {
  const [rawData, setRawData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [creditRate, setCreditRate] = useState(DEFAULT_CREDIT_RATE);
  const [showCost, setShowCost] = useState(false);

  const [filterService, setFilterService] = useState<string[]>([]);
  const [filterUser, setFilterUser] = useState<string[]>([]);
  const [filterWarehouse, setFilterWarehouse] = useState<string[]>([]);
  const [filterComponent, setFilterComponent] = useState<string[]>([]);
  const [filterAgent, setFilterAgent] = useState<string[]>([]);
  const [dateStart, setDateStart] = useState<string>("");
  const [dateEnd, setDateEnd] = useState<string>("");
  const [timeGranularity, setTimeGranularity] = useState<TimeGranularity>("monthly");

  useEffect(() => {
    fetch("/api/cost-data")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setRawData)
      .catch((e) => setError(e.message));
  }, []);

  const allServiceTypes = useMemo(() => {
    if (!rawData) return [];
    return rawData.byService.map((r) => r.NAME).sort();
  }, [rawData]);

  const allUsers = useMemo(() => {
    if (!rawData) return [];
    return rawData.byUser.map((r) => r.NAME).sort();
  }, [rawData]);

  const allWarehouses = useMemo(() => {
    if (!rawData) return [];
    return rawData.byWarehouse.map((r) => r.NAME).sort();
  }, [rawData]);

  const allComponents = useMemo(() => {
    if (!rawData) return [];
    return rawData.byComponent.map((r) => r.NAME).sort();
  }, [rawData]);

  const allAgents = useMemo(() => {
    if (!rawData) return [];
    return rawData.byAgent.map((r) => r.NAME).sort();
  }, [rawData]);

  const dateRange = useMemo(() => {
    if (!rawData) return { min: "", max: "" };
    const detailDates = rawData.detail.map((r) => r.START_TIME.slice(0, 10));
    const monthlyDates = rawData.monthly.map((r) => r.PERIOD.slice(0, 10));
    const allDates = [...detailDates, ...monthlyDates];
    return { min: allDates.reduce((a, b) => (a < b ? a : b)), max: allDates.reduce((a, b) => (a > b ? a : b)) };
  }, [rawData]);

  const filtered = useMemo(() => {
    if (!rawData) return null;
    let rows = rawData.detail;
    if (filterService.length > 0) rows = rows.filter((r) => filterService.includes(r.SERVICE_TYPE));
    if (filterUser.length > 0) rows = rows.filter((r) => filterUser.includes(r.END_USER_NAME));
    if (filterWarehouse.length > 0) rows = rows.filter((r) => filterWarehouse.includes(r.WAREHOUSE_NAME));
    if (filterComponent.length > 0) rows = rows.filter((r) => filterComponent.includes(r.COST_COMPONENT));
    if (filterAgent.length > 0) rows = rows.filter((r) => filterAgent.includes(r.COMPONENT_OBJECT_NAME));
    if (dateStart) rows = rows.filter((r) => r.START_TIME.slice(0, 10) >= dateStart);
    if (dateEnd) rows = rows.filter((r) => r.START_TIME.slice(0, 10) <= dateEnd);
    return rows;
  }, [rawData, filterService, filterUser, filterWarehouse, filterComponent, filterAgent, dateStart, dateEnd]);

  const data = useMemo(() => {
    if (!filtered || !rawData) return null;
    const isFiltered = filterService.length > 0 || filterUser.length > 0 || filterWarehouse.length > 0 || filterComponent.length > 0 || filterAgent.length > 0 || !!dateStart || !!dateEnd;

    if (!isFiltered) {
      const trendMap: Record<TimeGranularity, MonthlyRow[]> = {
        daily: rawData.daily,
        weekly: rawData.weekly,
        monthly: rawData.monthly,
        yearly: rawData.yearly,
      };
      const monthly = [...(trendMap[timeGranularity] || rawData.monthly)].sort((a, b) => a.PERIOD.localeCompare(b.PERIOD));
      return {
        ...rawData,
        monthly: addMonthlyCost(monthly, creditRate),
        byService: addCost(rawData.byService, creditRate),
        byComponent: addCost(rawData.byComponent, creditRate),
        byUser: addCost(rawData.byUser, creditRate),
        byWarehouse: addCost(rawData.byWarehouse, creditRate),
        byObject: addCost(rawData.byObject, creditRate),
        byAgent: addCost(rawData.byAgent, creditRate),
      };
    }

    const totalCredits = Math.round(filtered.reduce((s, r) => s + (r.COMPONENT_CREDITS ?? 0), 0) * 100) / 100;
    const totals: Totals = {
      TOTAL_CREDITS: totalCredits,
      UNIQUE_USERS: new Set(filtered.map((r) => r.END_USER_NAME)).size,
      TOTAL_QUERIES: filtered.length,
      SERVICE_TYPES: new Set(filtered.map((r) => r.SERVICE_TYPE)).size,
      TOTAL_INPUT_TOKENS: filtered.reduce((s, r) => s + (r.INPUT_TOKENS ?? 0), 0),
      TOTAL_OUTPUT_TOKENS: filtered.reduce((s, r) => s + (r.OUTPUT_TOKENS ?? 0), 0),
      TOTAL_TOKENS: filtered.reduce((s, r) => s + (r.TOTAL_TOKENS ?? 0), 0),
    };

    const tokenMap = new Map<string, { input: number; output: number; total: number }>();
    for (const r of filtered) {
      if ((r.TOTAL_TOKENS ?? 0) === 0) continue;
      const existing = tokenMap.get(r.SERVICE_TYPE) || { input: 0, output: 0, total: 0 };
      existing.input += r.INPUT_TOKENS ?? 0;
      existing.output += r.OUTPUT_TOKENS ?? 0;
      existing.total += r.TOTAL_TOKENS ?? 0;
      tokenMap.set(r.SERVICE_TYPE, existing);
    }
    const tokensByService = Array.from(tokenMap.entries())
      .map(([NAME, t]) => ({ NAME, INPUT_TOKENS: t.input, OUTPUT_TOKENS: t.output, TOTAL_TOKENS: t.total }))
      .sort((a, b) => b.TOTAL_TOKENS - a.TOTAL_TOKENS);

    return {
      totals,
      monthly: addMonthlyCost(groupByPeriod(filtered, timeGranularity), creditRate),
      byService: addCost(groupBy(filtered, (r) => r.SERVICE_TYPE), creditRate),
      byComponent: addCost(groupBy(filtered, (r) => r.COST_COMPONENT), creditRate),
      byUser: addCost(groupBy(filtered, (r) => r.END_USER_NAME).slice(0, 10), creditRate),
      byWarehouse: addCost(groupBy(filtered, (r) => r.WAREHOUSE_NAME || "N/A").filter((r) => r.NAME !== "N/A").slice(0, 10), creditRate),
      byObject: addCost(groupBy(filtered, (r) => r.SERVICE_TYPE + " | " + (r.COMPONENT_OBJECT_NAME || "")).slice(0, 10), creditRate),
      byAgent: addCost(groupBy(filtered, (r) => r.COMPONENT_OBJECT_NAME).filter((r) => allAgents.includes(r.NAME)), creditRate),
      detail: filtered,
      tokensByService,
    };
  }, [filtered, rawData, filterService, filterUser, filterWarehouse, filterComponent, filterAgent, dateStart, dateEnd, creditRate, timeGranularity, allAgents]);

  const hasFilters = filterService.length > 0 || filterUser.length > 0 || filterWarehouse.length > 0 || filterComponent.length > 0 || filterAgent.length > 0 || !!dateStart || !!dateEnd;
  const clearFilters = useCallback(() => {
    setFilterService([]);
    setFilterUser([]);
    setFilterWarehouse([]);
    setFilterComponent([]);
    setFilterAgent([]);
    setDateStart("");
    setDateEnd("");
  }, []);

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#f8f9fb]">
        <Card className="max-w-md shadow-sm border-0 ring-1 ring-black/[0.04]">
          <CardContent className="p-8 text-center">
            <p className="text-red-600 font-semibold">Failed to load data</p>
            <p className="text-sm text-slate-500 mt-2">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data) return <LoadingSkeleton />;

  const totalCost = Math.round((data.totals.TOTAL_CREDITS ?? 0) * creditRate * 100) / 100;

  const metrics = [
    { key: "credits", label: "Total Credits", icon: Zap, value: (data.totals.TOTAL_CREDITS ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 }), color: "bg-blue-50 text-blue-600" },
    { key: "cost", label: "Estimated Cost", icon: DollarSign, value: `${totalCost.toLocaleString(undefined, { minimumFractionDigits: 2 })}`, color: "bg-emerald-50 text-emerald-600" },
    { key: "tokens", label: "Total Tokens", icon: MessageSquare, value: (data.totals.TOTAL_TOKENS ?? 0).toLocaleString(), color: "bg-amber-50 text-amber-600" },
    { key: "users", label: "Unique Users", icon: Users, value: (data.totals.UNIQUE_USERS ?? 0).toLocaleString(), color: "bg-orange-50 text-orange-600" },
    { key: "queries", label: "Total Queries", icon: Hash, value: (data.totals.TOTAL_QUERIES ?? 0).toLocaleString(), color: "bg-violet-50 text-violet-600" },
  ];

  return (
    <div className="min-h-screen bg-[#f8f9fb]">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="mx-auto max-w-[1440px] px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/snowflake-logo.png" alt="Snowflake" className="h-8" />
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900">
                Cortex AI Usage Dashboard
              </h1>
              <p className="text-xs text-slate-400 font-medium tracking-wide uppercase">
                Usage &amp; Cost Tracking
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <label className="text-slate-500 font-medium">$/credit:</label>
              <input
                type="number"
                value={creditRate}
                onChange={(e) => setCreditRate(Number(e.target.value) || 0)}
                step="0.25"
                min="0"
                className="w-20 rounded-lg border border-slate-200 px-2.5 py-1.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => setShowCost(!showCost)}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${showCost ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}
            >
              {showCost ? "$ Cost" : "Credits"}
            </button>
            <span className="rounded-full bg-slate-100 px-3 py-1.5 font-mono text-xs text-slate-500 font-medium">
              {process.env.NEXT_PUBLIC_SNOWFLAKE_LABEL || ""}
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1440px] px-8 py-6 space-y-6">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Filters:</span>
          <MultiSelect label="Service Type" options={allServiceTypes} selected={filterService} onChange={setFilterService} />
          <MultiSelect label="User" options={allUsers} selected={filterUser} onChange={setFilterUser} />
          <MultiSelect label="Warehouse" options={allWarehouses} selected={filterWarehouse} onChange={setFilterWarehouse} />
              <MultiSelect label="Component" options={allComponents} selected={filterComponent} onChange={setFilterComponent} displayFn={shortenComponentLabel} />
          <MultiSelect label="Cortex Agent" options={allAgents} selected={filterAgent} onChange={setFilterAgent} displayFn={shortenAgentLabel} />
              <div className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-slate-400" />
                <span className="text-xs text-slate-500 font-medium">From</span>
                <input
                  type="date"
                  value={dateStart || dateRange.min}
                  min={dateRange.min}
                  max={dateEnd || dateRange.max}
                  onChange={(e) => setDateStart(e.target.value)}
                  className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-xs text-slate-500 font-medium">to</span>
                <input
                  type="date"
                  value={dateEnd || dateRange.max}
                  min={dateStart || dateRange.min}
                  max={dateRange.max}
                  onChange={(e) => setDateEnd(e.target.value)}
                  className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                {(dateStart || dateEnd) && (
                  <button
                    onClick={() => { setDateStart(""); setDateEnd(""); }}
                    className="bg-blue-600 text-white rounded-full p-0.5 hover:bg-blue-700 transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </div>
          {hasFilters && (
            <button onClick={clearFilters} className="text-xs text-blue-600 hover:text-blue-800 font-medium underline underline-offset-2">
              Clear all
            </button>
          )}
          {hasFilters && (
            <span className="text-xs text-slate-400">
              Showing {filtered?.length.toLocaleString()} of {rawData?.detail.length.toLocaleString()} records
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
          {metrics.map((m) => {
            const Icon = m.icon;
            return (
              <Card key={m.key} className="shadow-sm border-0 ring-1 ring-black/[0.04]">
                <CardContent className="flex items-center gap-4 p-5">
                  <div className={`rounded-xl p-3 ${m.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{m.label}</p>
                    <p className="text-2xl font-bold tracking-tight text-slate-900 mt-0.5">
                      {m.value}
                    </p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <TimeChart data={data.monthly} showCost={showCost} granularity={timeGranularity} onGranularityChange={setTimeGranularity} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <HorizontalBarChart data={data.byService} title="By Service Type" color="#3b82f6" />
          <HorizontalBarChart data={data.byComponent} title="By Cost Component" color="#8b5cf6" shortenComponents />
          <HorizontalBarChart data={data.byUser} title="Top Users" color="#06b6d4" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <HorizontalBarChart data={data.byWarehouse} title="Top Warehouses" color="#f97316" />
          <HorizontalBarChart data={data.byObject} title="Top Objects" color="#10b981" shortenObjects />
          <HorizontalBarChart data={data.byAgent} title="By Cortex Agent" color="#0ea5e9" shortenLabels />
        </div>

        <TokenBarChart data={data.tokensByService} title="Tokens by Service (Input / Output)" />

        <Card className="shadow-sm border-0 ring-1 ring-black/[0.04] overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-blue-600">
              Detailed Usage
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {hasFilters ? `${data.detail.length.toLocaleString()} filtered records` : `Most recent ${data.detail.length.toLocaleString()} records`}
            </p>
          </div>
          <div className="overflow-auto max-h-[500px]">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/80">
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500">Time</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500">User</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500">Service</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500">Component</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500">Warehouse</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500">Object</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500 text-right">Credits</TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500 text-right">Tokens</TableHead>
                  {showCost && (
                    <TableHead className="text-xs font-semibold uppercase tracking-wider text-slate-500 text-right">Est. Cost</TableHead>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.detail.map((row, i) => (
                  <TableRow key={i} className="hover:bg-blue-50/40 transition-colors">
                    <TableCell className="text-sm text-slate-600 whitespace-nowrap">
                      {new Date(row.START_TIME).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </TableCell>
                    <TableCell className="text-sm font-medium text-slate-700">{row.END_USER_NAME}</TableCell>
                    <TableCell>
                      <ServiceBadge type={row.SERVICE_TYPE} />
                    </TableCell>
                    <TableCell className="text-sm text-slate-600 max-w-[200px] truncate">
                      {row.COST_COMPONENT}
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">{row.WAREHOUSE_NAME}</TableCell>
                    <TableCell className="text-sm text-slate-500 max-w-[150px] truncate">
                      {row.COMPONENT_OBJECT_NAME}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm font-medium text-slate-700">
                      {(row.COMPONENT_CREDITS ?? 0).toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm font-medium text-amber-700">
                      {(row.TOTAL_TOKENS ?? 0).toLocaleString()}
                    </TableCell>
                    {showCost && (
                      <TableCell className="text-right font-mono text-sm font-medium text-emerald-700">
                        ${((row.COMPONENT_CREDITS ?? 0) * creditRate).toFixed(2)}
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      </main>
    </div>
  );
}
