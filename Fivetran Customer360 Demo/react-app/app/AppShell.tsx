"use client"

import { useState } from "react"
import Dashboard from "./Dashboard"
import AgentChat from "./AgentChat"
import MCPArchitecture from "./MCPArchitecture"

const TABS = [
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "chat", label: "AI Assistant", icon: "🤖" },
  { id: "mcp", label: "MCP Architecture", icon: "🔗" },
]

export default function AppShell() {
  const [activeTab, setActiveTab] = useState("dashboard")

  return (
    <div className="min-h-screen bg-[#0B1929]">
      <header className="bg-gradient-to-r from-[#1B2A4A] to-[#0f3460] text-white shadow-lg border-b border-[#29B5E8]/20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#29B5E8]/20 rounded-lg flex items-center justify-center text-xl">🏦</div>
            <div>
              <h1 className="text-xl font-bold">Financial Services CRM Customer 360</h1>
              <p className="text-xs text-blue-300/70">Powered by Snowflake Cortex AI + Fivetran</p>
            </div>
          </div>
          <div className="flex gap-1 bg-white/10 rounded-lg p-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  activeTab === tab.id ? "bg-[#29B5E8] text-white shadow" : "text-white/70 hover:bg-white/10"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-blue-300/70">Pipeline Active</span>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "chat" && <AgentChat />}
        {activeTab === "mcp" && <MCPArchitecture />}
      </main>
      <footer className="text-center py-4 text-xs text-gray-500">
        Built with Snowflake Cortex Code | Fivetran ELT → dbt → Dynamic Tables → Cortex Agent → SPCS
      </footer>
    </div>
  )
}
