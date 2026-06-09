"use client"

import { useEffect, useState } from "react"

const TYPE_LABEL: Record<string, string> = {
  CORTEX_ANALYST_MESSAGE: "Cortex Analyst",
  CORTEX_SEARCH_SERVICE_QUERY: "Cortex Search",
  CORTEX_AGENT_RUN: "Cortex Agent",
  SYSTEM_EXECUTE_SQL: "SQL Execution",
  GENERIC: "Generic (UDF)",
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "bg-green-500/20 text-green-300", connected: "bg-green-500/20 text-green-300",
    fresh: "bg-green-500/20 text-green-300", acceptable: "bg-yellow-500/20 text-yellow-300",
  }
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status.toLowerCase()] || "bg-gray-500/20 text-gray-300"}`}>{status}</span>
}

function relTime(iso: string): string {
  if (!iso) return "—"
  const mins = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000))
  if (mins < 60) return `${mins} min ago`
  const hrs = Math.round(mins / 60)
  return `${hrs} hr${hrs > 1 ? "s" : ""} ago`
}

export default function MCPArchitecture() {
  const [tools, setTools] = useState<any[]>([])
  const [connectors, setConnectors] = useState<any[]>([])
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    fetch("/api/mcp").then((r) => r.json()).then((d) => setTools(d.tools ?? [])).catch(() => {})
    fetch("/api/fivetran").then((r) => r.json()).then((d) => setConnectors(d.connectors ?? [])).catch((e) => setErr(String(e)))
  }, [])

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-[#29B5E8]/10 to-[#1B2A4A]/50 rounded-xl p-6 border border-[#29B5E8]/20">
        <h2 className="text-lg font-bold text-white mb-2">MCP Bridge: Fivetran + Snowflake</h2>
        <p className="text-sm text-blue-200/80">
          The Model Context Protocol (MCP) is the standardized bridge between AI agents and data tools. This page reads the
          <span className="font-mono text-xs"> CUSTOMER360_MCP_SERVER</span> tool list and live Fivetran connector status directly from Snowflake.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-[#1B2A4A]/60 rounded-xl border border-[#29B5E8]/10 p-5">
          <h3 className="text-sm font-medium text-blue-200 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 bg-[#29B5E8]/20 rounded flex items-center justify-center text-xs">S</span>
            Snowflake MCP Server Tools {tools.length > 0 && <span className="text-xs text-blue-300/50">({tools.length})</span>}
          </h3>
          <div className="space-y-2">
            {tools.length === 0 && <p className="text-xs text-blue-300/40">Loading tools from DESCRIBE MCP SERVER…</p>}
            {tools.map((tool, i) => (
              <div key={i} className="flex items-start gap-3 p-2 rounded-lg hover:bg-white/5">
                <div className="mt-0.5"><StatusBadge status="active" /></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-200 truncate">{tool.name}</span>
                    <span className="text-xs px-1.5 py-0.5 bg-white/10 text-blue-300/70 rounded">{TYPE_LABEL[tool.type] ?? tool.type}</span>
                  </div>
                  <p className="text-xs text-blue-300/50 mt-0.5">{tool.description}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-[#0f3460]/40 rounded-lg">
            <p className="text-xs text-[#29B5E8] font-medium">MCP Endpoint:</p>
            <p className="text-xs text-blue-300/70 font-mono break-all mt-1">
              /api/v2/databases/FIVETRAN_CRM_CUSTOMER360/schemas/ANALYTICS/mcp-servers/CUSTOMER360_MCP_SERVER
            </p>
          </div>
        </div>

        <div className="bg-[#1B2A4A]/60 rounded-xl border border-[#29B5E8]/10 p-5">
          <h3 className="text-sm font-medium text-blue-200 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 bg-teal-500/20 rounded flex items-center justify-center text-xs">F</span>
            Fivetran Connector Status
          </h3>
          {err && <p className="text-xs text-red-400 mb-2">{err}</p>}
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-blue-300/50 border-b border-blue-900">
                <th className="pb-2 font-medium">Connector</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 font-medium">Last Sync</th>
                <th className="pb-2 font-medium text-right">Rows</th>
                <th className="pb-2 font-medium">Freshness</th>
              </tr>
            </thead>
            <tbody>
              {connectors.length === 0 && <tr><td colSpan={5} className="py-3 text-xs text-blue-300/40">Loading connector status from Fivetran UDF…</td></tr>}
              {connectors.map((c, i) => (
                <tr key={i} className="border-b border-blue-900/30">
                  <td className="py-2 font-medium text-gray-200">{c.name}</td>
                  <td className="py-2"><StatusBadge status={c.status ?? "connected"} /></td>
                  <td className="py-2 text-blue-300/60">{relTime(c.last_sync_completed)}</td>
                  <td className="py-2 text-right text-blue-300/60">{Number(c.rows_synced_last ?? 0).toLocaleString()}</td>
                  <td className="py-2"><StatusBadge status={c.data_freshness ?? "fresh"} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4 p-3 bg-teal-500/10 rounded-lg">
            <p className="text-xs text-teal-300 font-medium">Fivetran MCP Server:</p>
            <p className="text-xs text-teal-300/70 font-mono mt-1">uvx --from git+https://github.com/fivetran/fivetran-mcp fivetran-mcp</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <div className="text-2xl mb-2">🔗</div>
          <h4 className="font-semibold text-blue-100 text-sm">Snowflake as MCP Server</h4>
          <p className="text-xs text-blue-300/60 mt-1">External AI clients (Claude, CoCo, custom apps) connect to Snowflake's managed MCP endpoint to discover and invoke Cortex tools. No infrastructure to deploy.</p>
        </div>
        <div className="bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <div className="text-2xl mb-2">🔄</div>
          <h4 className="font-semibold text-blue-100 text-sm">Fivetran as MCP Server</h4>
          <p className="text-xs text-blue-300/60 mt-1">Fivetran's open-source MCP server lets AI tools manage connectors, check sync status, and trigger syncs. Runs locally via uvx with API key auth.</p>
        </div>
        <div className="bg-[#1B2A4A]/60 rounded-xl p-5 border border-[#29B5E8]/10">
          <div className="text-2xl mb-2">🤖</div>
          <h4 className="font-semibold text-blue-100 text-sm">Agent Orchestration</h4>
          <p className="text-xs text-blue-300/60 mt-1">The Cortex Agent combines structured analytics (Analyst), unstructured advisor-note search (Search), and pipeline ops (Fivetran UDFs) in one interface.</p>
        </div>
      </div>
    </div>
  )
}
