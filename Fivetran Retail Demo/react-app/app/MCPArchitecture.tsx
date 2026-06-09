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
    active: "bg-green-100 text-green-700", connected: "bg-green-100 text-green-700",
    fresh: "bg-green-100 text-green-700", acceptable: "bg-yellow-100 text-yellow-700",
  }
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status.toLowerCase()] || "bg-gray-100 text-gray-600"}`}>{status}</span>
}

function relTime(iso: string): string {
  if (!iso) return "—"
  const then = new Date(iso).getTime()
  const mins = Math.max(0, Math.round((Date.now() - then) / 60000))
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
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-100">
        <h2 className="text-lg font-bold text-gray-800 mb-2">MCP Bridge: Fivetran + Snowflake</h2>
        <p className="text-sm text-gray-600">
          The Model Context Protocol (MCP) is the standardized bridge between AI agents and data tools. This page reads the
          <span className="font-mono text-xs"> RETAIL_MCP_SERVER</span> tool list and live Fivetran connector status directly from Snowflake.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-xs">S</span>
            Snowflake MCP Server Tools {tools.length > 0 && <span className="text-xs text-gray-400">({tools.length})</span>}
          </h3>
          <div className="space-y-2">
            {tools.length === 0 && <p className="text-xs text-gray-400">Loading tools from DESCRIBE MCP SERVER…</p>}
            {tools.map((tool, i) => (
              <div key={i} className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 border border-gray-50">
                <div className="mt-0.5"><StatusBadge status="active" /></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-800 truncate">{tool.name}</span>
                    <span className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">{TYPE_LABEL[tool.type] ?? tool.type}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{tool.description}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-700 font-medium">MCP Endpoint:</p>
            <p className="text-xs text-blue-600 font-mono break-all mt-1">
              /api/v2/databases/FIVETRAN_RETAIL_DEMO/schemas/ANALYTICS/mcp-servers/RETAIL_MCP_SERVER
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 bg-teal-100 rounded flex items-center justify-center text-xs">F</span>
            Fivetran Connector Status
          </h3>
          {err && <p className="text-xs text-red-500 mb-2">{err}</p>}
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 font-medium">Connector</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 font-medium">Last Sync</th>
                <th className="pb-2 font-medium text-right">Rows</th>
                <th className="pb-2 font-medium">Freshness</th>
              </tr>
            </thead>
            <tbody>
              {connectors.length === 0 && <tr><td colSpan={5} className="py-3 text-xs text-gray-400">Loading connector status from Fivetran UDF…</td></tr>}
              {connectors.map((c, i) => (
                <tr key={i} className="border-b border-gray-50">
                  <td className="py-2 font-medium text-gray-800">{c.name}</td>
                  <td className="py-2"><StatusBadge status={c.status ?? "connected"} /></td>
                  <td className="py-2 text-gray-600">{relTime(c.last_sync_completed)}</td>
                  <td className="py-2 text-right text-gray-600">{Number(c.rows_synced_last ?? 0).toLocaleString()}</td>
                  <td className="py-2"><StatusBadge status={c.data_freshness ?? "fresh"} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4 p-3 bg-teal-50 rounded-lg">
            <p className="text-xs text-teal-700 font-medium">Fivetran MCP Server:</p>
            <p className="text-xs text-teal-600 font-mono mt-1">uvx --from git+https://github.com/fivetran/fivetran-mcp fivetran-mcp</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-5 border border-blue-100">
          <div className="text-2xl mb-2">🔗</div>
          <h4 className="font-semibold text-gray-800 text-sm">Snowflake as MCP Server</h4>
          <p className="text-xs text-gray-600 mt-1">External AI clients (Claude, CoCo, custom apps) connect to Snowflake's managed MCP endpoint to discover and invoke Cortex tools. No infrastructure to deploy.</p>
        </div>
        <div className="bg-gradient-to-br from-teal-50 to-green-50 rounded-xl p-5 border border-teal-100">
          <div className="text-2xl mb-2">🔄</div>
          <h4 className="font-semibold text-gray-800 text-sm">Fivetran as MCP Server</h4>
          <p className="text-xs text-gray-600 mt-1">Fivetran's open-source MCP server lets AI tools manage connectors, check sync status, and trigger syncs. Runs locally via uvx with API key auth.</p>
        </div>
        <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl p-5 border border-orange-100">
          <div className="text-2xl mb-2">🤖</div>
          <h4 className="font-semibold text-gray-800 text-sm">Agent Orchestration</h4>
          <p className="text-xs text-gray-600 mt-1">The Cortex Agent combines structured analytics (Analyst), unstructured search (Search), and pipeline ops (Fivetran UDFs) in one intelligent interface.</p>
        </div>
      </div>
    </div>
  )
}
