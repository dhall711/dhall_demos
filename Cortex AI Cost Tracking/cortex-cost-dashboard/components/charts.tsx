"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  ComposedChart,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Area,
  Tooltip,
} from "recharts";

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

function shortenName(name: string): string {
  const parts = name.split(".");
  if (parts.length >= 3) return parts.slice(2).join(".");
  if (parts.length === 2) return parts[1];
  return name;
}

const COMPONENT_SHORT_NAMES: Record<string, string> = {
  "SERVING Credits": "Search Serving",
  "EMBED_TEXT_TOKENS Credits": "Embed Text",
  "LLM Inference": "AISQL LLM",
  "Text-to-SQL Inference": "Analyst API",
  "Snowflake Intelligence": "Intelligence",
  "Agent API Inference": "Agent API",
  "Agent Inference": "Cortex Agent",
  "Document Processing": "Document AI",
  "Fine-Tuning Job": "Fine-Tuning",
  "REST API Inference": "REST API",
  "Code CLI Inference": "Code CLI",
  "PTU Credits": "PTU",
};

export function shortenComponentLabel(name: string): string {
  return COMPONENT_SHORT_NAMES[name] || name;
}

function shortenComponentName(name: string): string {
  return shortenComponentLabel(name);
}

export function shortenAgentLabel(name: string): string {
  return shortenName(name);
}

function shortenObjectName(name: string): string {
  const pipeIdx = name.indexOf(" | ");
  if (pipeIdx === -1) return shortenName(name);
  const objPart = name.slice(pipeIdx + 3).trim();
  if (!objPart || objPart === "TBD") return name.slice(0, pipeIdx) + (objPart ? " (" + objPart + ")" : " (unnamed)");
  return shortenName(objPart);
}

function truncateLabel(label: string, maxLen: number): string {
  if (label.length <= maxLen) return label;
  return label.slice(0, maxLen - 1) + "\u2026";
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload?.length) return null;
  const visible = payload.filter((p) => p.name !== "hidden");
  if (!visible.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-lg text-sm">
      {label && <p className="font-medium text-slate-700 mb-1">{label}</p>}
      {visible.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-sm shrink-0" style={{ backgroundColor: p.color }} />
          <span className="text-slate-500">{p.name}:</span>
          <span className="font-semibold text-slate-800 ml-auto pl-3">{typeof p.value === "number" ? p.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : p.value}</span>
        </div>
      ))}
    </div>
  );
}

interface TokenRow {
  NAME: string;
  INPUT_TOKENS: number;
  OUTPUT_TOKENS: number;
  TOTAL_TOKENS: number;
}

function TokenTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: TokenRow & { DISPLAY_NAME: string }; name: string; value: number; color: string }> }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-lg text-sm">
      <p className="font-medium text-slate-700 mb-1 max-w-[260px]">{d.NAME}</p>
      <div className="flex items-center gap-2">
        <span className="h-2.5 w-2.5 rounded-sm shrink-0" style={{ backgroundColor: "#3b82f6" }} />
        <span className="text-slate-500">Input:</span>
        <span className="font-semibold text-slate-800 ml-auto pl-3">{d.INPUT_TOKENS.toLocaleString()}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="h-2.5 w-2.5 rounded-sm shrink-0" style={{ backgroundColor: "#f97316" }} />
        <span className="text-slate-500">Output:</span>
        <span className="font-semibold text-slate-800 ml-auto pl-3">{d.OUTPUT_TOKENS.toLocaleString()}</span>
      </div>
      <div className="flex items-center gap-2 border-t border-slate-100 mt-1 pt-1">
        <span className="text-slate-500">Total:</span>
        <span className="font-semibold text-slate-800 ml-auto pl-3">{d.TOTAL_TOKENS.toLocaleString()}</span>
      </div>
    </div>
  );
}

function BarTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: GroupedRow }> }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-lg text-sm">
      <p className="font-medium text-slate-700 mb-1 max-w-[260px]">{d.NAME}</p>
      <div className="flex items-center gap-2">
        <span className="text-slate-500">Credits:</span>
        <span className="font-semibold text-slate-800 ml-auto pl-3">{d.CREDITS.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
      </div>
      {d.COST !== undefined && (
        <div className="flex items-center gap-2">
          <span className="text-slate-500">Est. Cost:</span>
          <span className="font-semibold text-emerald-700 ml-auto pl-3">${d.COST.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </div>
      )}
    </div>
  );
}

type TimeGranularity = "daily" | "weekly" | "monthly" | "yearly";

const GRANULARITY_OPTIONS: { value: TimeGranularity; label: string }[] = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "yearly", label: "Yearly" },
];

function formatPeriodLabel(period: string, granularity: TimeGranularity): string {
  const dateStr = period.slice(0, 10);
  const d = new Date(dateStr + "T00:00:00");
  switch (granularity) {
    case "daily":
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    case "weekly":
      return "Wk " + d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    case "monthly":
      return d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
    case "yearly":
      return d.getFullYear().toString();
  }
}

export function TimeChart({ data, showCost, granularity = "monthly", onGranularityChange }: { data: MonthlyRow[]; showCost?: boolean; granularity?: TimeGranularity; onGranularityChange?: (g: TimeGranularity) => void }) {
  const formatted = data.map((d) => ({
    ...d,
    label: formatPeriodLabel(d.PERIOD, granularity),
  }));

  return (
    <Card className="shadow-sm border-0 ring-1 ring-black/[0.04]">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-blue-600">
            {showCost ? "Cost Over Time" : "Credits Over Time"}
          </CardTitle>
          {onGranularityChange && (
            <div className="flex items-center gap-1 rounded-lg bg-slate-100 p-0.5">
              {GRANULARITY_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => onGranularityChange(opt.value)}
                  className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                    granularity === opt.value
                      ? "bg-white text-blue-700 shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="overflow-visible">
        <div className="h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={formatted} margin={{ top: 10, right: 50, bottom: 0, left: 10 }}>
              <defs>
                <linearGradient id="cumulativeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f97316" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 12, fill: "#64748b" }}
                axisLine={{ stroke: "#e2e8f0" }}
                tickLine={false}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12, fill: "#64748b" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => showCost ? `$${v.toLocaleString()}` : v.toLocaleString()}
                label={{ value: showCost ? "Cost ($)" : "Credits", angle: -90, position: "insideLeft", style: { fontSize: 11, fill: "#94a3b8" } }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fontSize: 12, fill: "#64748b" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => showCost ? `$${v.toLocaleString()}` : v.toLocaleString()}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(59, 130, 246, 0.04)" }} wrapperStyle={{ zIndex: 1000 }} />
              <Bar
                yAxisId="left"
                dataKey={showCost ? "COST" : "CREDITS"}
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
                opacity={0.9}
                name={showCost ? "Cost ($)" : "Credits"}
                barSize={32}
              />
              <Area
                yAxisId="right"
                type="monotone"
                dataKey={showCost ? "CUMULATIVE_COST" : "CUMULATIVE_CREDITS"}
                fill="url(#cumulativeGrad)"
                stroke="none"
                name="hidden"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey={showCost ? "CUMULATIVE_COST" : "CUMULATIVE_CREDITS"}
                stroke="#f97316"
                strokeWidth={2.5}
                dot={false}
                name={showCost ? "Cumulative Cost ($)" : "Cumulative Credits"}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function TokenBarChart({ data, title }: { data: TokenRow[]; title: string }) {
  const displayData = data.map((d) => ({
    ...d,
    DISPLAY_NAME: d.NAME,
  }));
  const height = Math.max(displayData.length * 42 + 50, 140);
  const maxLabelLen = Math.min(32, Math.max(...displayData.map((d) => d.DISPLAY_NAME.length), 10));
  const labelWidth = Math.min(maxLabelLen * 7.5, 220);

  return (
    <Card className="shadow-sm border-0 ring-1 ring-black/[0.04]">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider text-blue-600">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="overflow-visible">
        <div style={{ height, width: "100%" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={displayData}
              layout="vertical"
              margin={{ left: 10, right: 30, top: 5, bottom: 5 }}
            >
              <CartesianGrid horizontal={false} stroke="#e2e8f0" strokeDasharray="3 3" />
              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: "#64748b" }}
                axisLine={{ stroke: "#e2e8f0" }}
                tickLine={false}
                tickFormatter={(v: number) => v >= 1000000 ? `${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `${(v / 1000).toFixed(0)}K` : v.toLocaleString()}
              />
              <YAxis
                dataKey="DISPLAY_NAME"
                type="category"
                width={labelWidth}
                tick={(props: { x: number; y: number; payload: { value: string } }) => {
                  const label = truncateLabel(props.payload.value, 28);
                  return (
                    <text x={props.x - 4} y={props.y} textAnchor="end" dominantBaseline="central" fontSize={11} fill="#334155" fontWeight={500}>
                      {label}
                    </text>
                  );
                }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<TokenTooltip />} cursor={{ fill: "rgba(59, 130, 246, 0.04)" }} wrapperStyle={{ zIndex: 1000 }} />
              <Bar dataKey="INPUT_TOKENS" stackId="tokens" fill="#3b82f6" radius={[0, 0, 0, 0]} barSize={18} name="Input" />
              <Bar dataKey="OUTPUT_TOKENS" stackId="tokens" fill="#f97316" radius={[0, 6, 6, 0]} barSize={18} name="Output" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function HorizontalBarChart({
  data,
  title,
  color = "#3b82f6",
  shortenLabels = false,
  shortenComponents = false,
  shortenObjects = false,
}: {
  data: GroupedRow[];
  title: string;
  color?: string;
  shortenLabels?: boolean;
  shortenComponents?: boolean;
  shortenObjects?: boolean;
}) {
  const displayData = data.map((d) => ({
    ...d,
    DISPLAY_NAME: shortenLabels
      ? shortenName(d.NAME)
      : shortenComponents
        ? shortenComponentName(d.NAME)
        : shortenObjects
          ? shortenObjectName(d.NAME)
          : d.NAME,
  }));
  const height = Math.max(displayData.length * 42 + 50, 140);
  const maxLabelLen = Math.min(
    32,
    Math.max(...displayData.map((d) => d.DISPLAY_NAME.length), 10)
  );
  const labelWidth = Math.min(maxLabelLen * 7.5, 220);

  return (
    <Card className="shadow-sm border-0 ring-1 ring-black/[0.04]">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider text-blue-600">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="overflow-visible">
        <div style={{ height, width: "100%" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={displayData}
              layout="vertical"
              margin={{ left: 10, right: 30, top: 5, bottom: 5 }}
            >
              <CartesianGrid horizontal={false} stroke="#e2e8f0" strokeDasharray="3 3" />
              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: "#64748b" }}
                axisLine={{ stroke: "#e2e8f0" }}
                tickLine={false}
                tickFormatter={(v: number) => v.toLocaleString()}
              />
              <YAxis
                dataKey="DISPLAY_NAME"
                type="category"
                width={labelWidth}
                tick={(props: { x: number; y: number; payload: { value: string } }) => {
                  const label = truncateLabel(props.payload.value, 28);
                  return (
                    <text x={props.x - 4} y={props.y} textAnchor="end" dominantBaseline="central" fontSize={11} fill="#334155" fontWeight={500}>
                      {label}
                    </text>
                  );
                }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<BarTooltip />} cursor={{ fill: "rgba(59, 130, 246, 0.04)" }} wrapperStyle={{ zIndex: 1000 }} />
              <Bar
                dataKey="CREDITS"
                fill={color}
                radius={[0, 6, 6, 0]}
                barSize={18}
                name="Credits"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
