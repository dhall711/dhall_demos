"use client"

import { useEffect, useState } from "react"
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const SEGMENT_COLORS: Record<string, string> = {
  VIP: "#29B5E8", Active: "#00D4AA", New: "#FFD93D", "At-Risk": "#FF6B6B", Churned: "#6C5CE7",
}
const FALLBACK_COLORS = ["#29B5E8", "#00D4AA", "#FF6B6B", "#FFD93D", "#6C5CE7", "#FFA07A"]

function fmtUSD(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(2)}M`
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`
  return `$${Math.round(n).toLocaleString()}`
}

function KPICard({ label, value, subvalue, icon }: { label: string; value: string; subvalue?: string; icon: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-500">{label}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      {subvalue && <div className="text-xs text-gray-500 mt-1">{subvalue}</div>}
    </div>
  )
}

interface KpiData {
  kpis: Record<string, number>
  cust: Record<string, number>
  salesByCategory: any[]
  monthlyTrend: any[]
  customerSegments: any[]
  topProducts: any[]
  error?: string
}

export default function Dashboard() {
  const [data, setData] = useState<KpiData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/kpis")
      .then((r) => r.json())
      .then((d) => (d.error ? setError(d.error) : setData(d)))
      .catch((e) => setError(String(e)))
  }, [])

  if (error) {
    return <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-sm text-red-700">Failed to load data: {error}</div>
  }
  if (!data) {
    return <div className="text-center py-20 text-gray-400">Loading live data from Snowflake…</div>
  }

  const totalRevenue = Number(data.kpis.TOTAL_REVENUE || 0)
  const totalOrders = Number(data.kpis.TOTAL_ORDERS || 0)
  const aov = Number(data.kpis.AVG_ORDER_VALUE || 0)
  const totalCustomers = Number(data.cust.TOTAL_CUSTOMERS || 0)
  const vipCustomers = Number(data.cust.VIP_CUSTOMERS || 0)

  const segments = data.customerSegments.map((s, i) => ({
    name: s.NAME, value: Number(s.VALUE), fill: SEGMENT_COLORS[s.NAME] ?? FALLBACK_COLORS[i % FALLBACK_COLORS.length],
  }))
  const byCategory = data.salesByCategory.map((c) => ({ category: c.CATEGORY, revenue: Number(c.REVENUE), orders: Number(c.ORDERS) }))
  const trend = data.monthlyTrend.map((m) => ({ month: m.MONTH, revenue: Number(m.REVENUE), orders: Number(m.ORDERS) }))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <KPICard label="Total Revenue" value={fmtUSD(totalRevenue)} subvalue="All-time gross revenue" icon="💰" />
        <KPICard label="Total Orders" value={totalOrders.toLocaleString()} subvalue="Fulfilled + in-progress" icon="📦" />
        <KPICard label="Avg Order Value" value={fmtUSD(aov)} subvalue="Revenue / orders" icon="🛒" />
        <KPICard label="Customers" value={totalCustomers.toLocaleString()} subvalue={`${vipCustomers.toLocaleString()} VIP customers`} icon="👥" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Revenue by Category</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={byCategory} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="category" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
              <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
              <Bar dataKey="revenue" fill="#29B5E8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Monthly Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trend} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
              <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
              <Line type="monotone" dataKey="revenue" stroke="#29B5E8" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Top Products by Revenue</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 font-medium">Product</th>
                <th className="pb-2 font-medium">Brand</th>
                <th className="pb-2 font-medium">Category</th>
                <th className="pb-2 font-medium text-right">Revenue</th>
                <th className="pb-2 font-medium text-right">Orders</th>
                <th className="pb-2 font-medium text-right">Rating</th>
              </tr>
            </thead>
            <tbody>
              {data.topProducts.map((p, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2.5 font-medium text-gray-900">{p.NAME}</td>
                  <td className="py-2.5 text-gray-600">{p.BRAND}</td>
                  <td className="py-2.5"><span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{p.CATEGORY}</span></td>
                  <td className="py-2.5 text-right font-medium">{fmtUSD(Number(p.REVENUE))}</td>
                  <td className="py-2.5 text-right text-gray-600">{Number(p.ORDERS).toLocaleString()}</td>
                  <td className="py-2.5 text-right">
                    <span className="text-yellow-500">{"★".repeat(Math.round(Number(p.RATING) || 0))}</span> {Number(p.RATING) || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Customer Segments</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={segments} cx="50%" cy="50%" innerRadius={55} outerRadius={90} dataKey="value"
                label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`} labelLine={false}>
                {segments.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-teal-50 rounded-xl p-5 border border-blue-100">
        <div className="flex items-center gap-3">
          <div className="text-3xl">⚡</div>
          <div>
            <h3 className="font-semibold text-gray-800">Data Pipeline Status</h3>
            <p className="text-sm text-gray-600">
              Fivetran ELT → Bronze (5 tables) → dbt Silver (5 models) → Dynamic Tables Gold (4 DTs) → Cortex Agent (Analyst + Search + Fivetran)
            </p>
          </div>
          <div className="ml-auto flex gap-4 text-center">
            <div><div className="text-lg font-bold text-green-600">Live</div><div className="text-xs text-gray-500">Snowflake Data</div></div>
            <div><div className="text-lg font-bold text-blue-600">10 min</div><div className="text-xs text-gray-500">Data Lag</div></div>
          </div>
        </div>
      </div>
    </div>
  )
}
