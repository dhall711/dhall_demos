"use client"

import { useEffect, useState } from "react"
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

const PRIORITY_COLORS: Record<string, string> = {
  Low: "#10B981", Medium: "#29B5E8", High: "#F59E0B", Critical: "#EF4444", Urgent: "#EF4444",
}
const FALLBACK = ["#10B981", "#29B5E8", "#F59E0B", "#EF4444", "#6C5CE7"]

function fmtUSD(n: number): string {
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(1)}B`
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(0)}M`
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`
  return `$${Math.round(n).toLocaleString()}`
}

const KPICard = ({ label, value, sub, color }: { label: string; value: string; sub?: string; color?: string }) => (
  <div className="bg-gradient-to-br from-[#1B2A4A] to-[#162240] rounded-xl p-5 border border-[#29B5E8]/10 shadow-lg">
    <p className="text-sm text-blue-300/60 mb-1">{label}</p>
    <p className={`text-3xl font-bold ${color || "text-white"}`}>{value}</p>
    {sub && <p className="text-xs text-blue-300/40 mt-1">{sub}</p>}
  </div>
)

const tierColor = (tier: string) => ({ Platinum: "text-purple-400", Gold: "text-yellow-400", Silver: "text-gray-300", Bronze: "text-orange-400" }[tier] || "text-white")
const healthColor = (s: number) => (s >= 80 ? "text-green-400" : s >= 60 ? "text-yellow-400" : "text-red-400")

export default function Dashboard() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/kpis").then((r) => r.json()).then((d) => (d.error ? setError(d.error) : setData(d))).catch((e) => setError(String(e)))
  }, [])

  if (error) return <div className="bg-red-900/30 border border-red-500/30 rounded-xl p-5 text-sm text-red-300">Failed to load data: {error}</div>
  if (!data) return <div className="text-center py-20 text-blue-300/50">Loading live data from Snowflake…</div>

  const aum = Number(data.kpis.AUM || 0)
  const pipeline = Number(data.pipe.PIPELINE_VALUE || 0)
  const oppCount = Number(data.pipe.OPP_COUNT || 0)
  const winRate = Number(data.pipe.WIN_RATE || 0)
  const avgHealth = Number(data.kpis.AVG_HEALTH || 0)
  const accountCount = Number(data.kpis.ACCOUNT_COUNT || 0)

  const pipelineByProduct = data.pipelineByProduct.map((p: any) => ({ name: p.NAME, value: Number(p.VALUE) / 1_000_000 }))
  const quarterly = data.quarterlyTrend.map((q: any) => ({ quarter: q.QUARTER, revenue: Number(q.REVENUE) / 1_000_000, pipeline: Number(q.PIPELINE) / 1_000_000 }))
  const serviceData = data.serviceHealth.map((s: any, i: number) => ({ name: s.NAME, value: Number(s.VALUE), color: PRIORITY_COLORS[s.NAME] ?? FALLBACK[i % FALLBACK.length] }))

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-[#29B5E8]/10 to-[#1B2A4A]/50 rounded-xl p-4 border border-[#29B5E8]/20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-sm text-blue-200">3 Fivetran connectors syncing | 4 Dynamic Tables active | Live Snowflake data</span>
        </div>
        <span className="text-xs text-blue-300/50">FIVETRAN_CRM_CUSTOMER360</span>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <KPICard label="Assets Under Management" value={fmtUSD(aum)} sub="Aggregate annual revenue" color="text-[#29B5E8]" />
        <KPICard label="Active Pipeline" value={fmtUSD(pipeline)} sub={`${oppCount.toLocaleString()} opportunities`} color="text-emerald-400" />
        <KPICard label="Win Rate" value={`${winRate}%`} sub="Across product lines" color="text-yellow-400" />
        <KPICard label="Avg Health Score" value={String(avgHealth)} sub={`${accountCount.toLocaleString()} accounts`} color="text-purple-400" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <h3 className="text-sm font-medium text-blue-200 mb-4">Pipeline by Product Line ($M)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={pipelineByProduct}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="name" tick={{ fill: "#7db8d4", fontSize: 11 }} angle={-15} textAnchor="end" height={60} />
              <YAxis tick={{ fill: "#7db8d4", fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: "#1B2A4A", border: "1px solid #29B5E8", borderRadius: 8, color: "#fff" }} formatter={(v: number) => `$${v.toFixed(1)}M`} />
              <Bar dataKey="value" fill="#29B5E8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <h3 className="text-sm font-medium text-blue-200 mb-4">Pipeline by Quarter ($M)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={quarterly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
              <XAxis dataKey="quarter" tick={{ fill: "#7db8d4", fontSize: 11 }} />
              <YAxis tick={{ fill: "#7db8d4", fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: "#1B2A4A", border: "1px solid #29B5E8", borderRadius: 8, color: "#fff" }} formatter={(v: number) => `$${v.toFixed(1)}M`} />
              <Legend wrapperStyle={{ color: "#7db8d4", fontSize: 12 }} />
              <Line type="monotone" dataKey="revenue" name="Weighted" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="pipeline" name="Total Pipeline" stroke="#29B5E8" strokeWidth={2} dot={{ r: 4 }} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <h3 className="text-sm font-medium text-blue-200 mb-4">Top 10 Accounts by Pipeline</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-blue-300/50 text-left border-b border-blue-900">
                <th className="pb-2">Account</th>
                <th className="pb-2">Tier</th>
                <th className="pb-2">Segment</th>
                <th className="pb-2 text-right">Health</th>
                <th className="pb-2 text-right">Pipeline</th>
                <th className="pb-2 text-right">Cases</th>
              </tr>
            </thead>
            <tbody>
              {data.topAccounts.map((a: any, i: number) => (
                <tr key={i} className="border-b border-blue-900/30 text-gray-200 hover:bg-white/5">
                  <td className="py-2 font-medium">{a.NAME}</td>
                  <td className={`py-2 ${tierColor(a.TIER)}`}>{a.TIER}</td>
                  <td className="py-2 text-blue-300/60">{a.SEGMENT}</td>
                  <td className={`py-2 text-right font-bold ${healthColor(Number(a.HEALTH))}`}>{Number(a.HEALTH)}</td>
                  <td className="py-2 text-right">{fmtUSD(Number(a.PIPELINE))}</td>
                  <td className={`py-2 text-right ${Number(a.CASES) > 3 ? "text-red-400" : "text-gray-400"}`}>{Number(a.CASES)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <h3 className="text-sm font-medium text-blue-200 mb-4">Service Cases by Priority</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={serviceData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value">
                {serviceData.map((entry: any, i: number) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: "#1B2A4A", border: "1px solid #29B5E8", borderRadius: 8, color: "#fff" }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-3 text-xs mt-2">
            {serviceData.map((s: any, i: number) => (
              <div key={i} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
                <span className="text-gray-400">{s.name} ({s.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
