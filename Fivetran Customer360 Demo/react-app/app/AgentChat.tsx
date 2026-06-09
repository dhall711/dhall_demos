"use client"

import { useState, useRef, useEffect, ReactNode } from "react"

const SAMPLE_QUESTIONS = [
  "Which accounts have the highest pipeline value?",
  "What's our win rate by product line?",
  "Which accounts are at risk based on health score?",
  "What are advisors noting about at-risk clients?",
  "Show me marketing campaign ROI",
  "Which accounts have the most open service cases?",
]

interface AgentTable {
  columns: string[]
  rows: any[][]
  title?: string
}

interface Message {
  role: "user" | "assistant"
  content: string
  tool?: string
  sql?: string
  table?: AgentTable
}

function StructuredTable({ table }: { table: AgentTable }) {
  return (
    <div className="my-3 overflow-x-auto">
      {table.title && <div className="text-xs font-medium text-blue-300/60 mb-1">{table.title}</div>}
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-[#0f3460]">
            {table.columns.map((c, j) => (
              <th key={j} className="px-3 py-2 text-left font-medium text-blue-200 border-b border-blue-900 whitespace-nowrap">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, ri) => (
            <tr key={ri} className="border-b border-blue-900/30 hover:bg-white/5">
              {row.map((cell, ci) => (
                <td key={ci} className="px-3 py-2 text-gray-300 whitespace-nowrap">{cell == null ? "" : String(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function formatMessage(text: string): ReactNode[] {
  const lines = text.split("\n")
  const result: ReactNode[] = []
  let tableRows: string[] = []
  let inTable = false

  const flushTable = (key: string) => {
    if (tableRows.length === 0) return
    const header = tableRows[0].split("|").filter((c) => c.trim())
    const bodyRows = tableRows.slice(1)
    result.push(
      <table key={key} className="w-full text-sm border-collapse my-3">
        <thead>
          <tr className="bg-[#0f3460]">
            {header.map((c, j) => <th key={j} className="px-3 py-2 text-left font-medium text-blue-200 border-b border-blue-900">{c.trim()}</th>)}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, ri) => (
            <tr key={ri} className="border-b border-blue-900/30 hover:bg-white/5">
              {row.split("|").filter((c) => c.trim()).map((c, ci) => <td key={ci} className="px-3 py-2 text-gray-300">{c.trim()}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    )
    tableRows = []
    inTable = false
  }

  lines.forEach((line, i) => {
    const t = line.trim()
    if (t.startsWith("|") && t.endsWith("|")) {
      inTable = true
      if (!t.includes("---")) tableRows.push(t)
    } else {
      if (inTable) flushTable(`t-${i}`)
      if (t) {
        const html = t.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/"(.*?)"/g, '<em>"$1"</em>')
        result.push(<p key={`p-${i}`} className="my-1" dangerouslySetInnerHTML={{ __html: html }} />)
      }
    }
  })
  if (inTable) flushTable("t-end")
  return result
}

export default function AgentChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const chatEnd = useRef<HTMLDivElement>(null)

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: "smooth" }) }, [messages])

  const sendMessage = async (question?: string) => {
    const q = (question || input).trim()
    if (!q || loading) return
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: q }])
    setLoading(true)
    try {
      const resp = await fetch("/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      })
      const data = await resp.json()
      if (data.error) {
        setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${data.error}`, tool: "Error" }])
      } else {
        setMessages((prev) => [...prev, { role: "assistant", content: data.text, tool: data.tool, sql: data.sql, table: data.table }])
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Request failed: ${String(e)}`, tool: "Error" }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-[#1B2A4A]/60 rounded-xl border border-[#29B5E8]/10 h-[calc(100vh-220px)] flex flex-col">
      <div className="p-4 border-b border-[#29B5E8]/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#29B5E8] rounded-lg flex items-center justify-center text-white text-sm font-bold">AI</div>
          <div>
            <h3 className="font-semibold text-white">Customer 360 Assistant</h3>
            <p className="text-xs text-blue-300/60">Powered by CUSTOMER360_AGENT (Cortex Analyst + Search + Fivetran)</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🏦</div>
            <h3 className="text-lg font-semibold text-blue-100 mb-2">Ask me anything about your customer portfolio</h3>
            <p className="text-sm text-blue-300/50 mb-6">Live answers from the Cortex Agent over accounts, pipeline, campaigns, service, and advisor notes</p>
            <div className="grid grid-cols-2 gap-2 max-w-xl mx-auto">
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button key={i} onClick={() => sendMessage(q)}
                  className="text-left px-3 py-2.5 bg-[#0f3460]/50 hover:bg-[#29B5E8]/20 border border-[#29B5E8]/20 rounded-lg text-sm text-blue-100 transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-xl px-4 py-3 ${msg.role === "user" ? "bg-[#29B5E8] text-white" : "bg-[#0f3460]/50 border border-[#29B5E8]/10 text-gray-200"}`}>
              {msg.role === "assistant" && msg.tool && (
                <div className="flex items-center gap-1 mb-2">
                  <span className="text-xs px-2 py-0.5 bg-[#29B5E8]/20 text-[#29B5E8] rounded-full font-medium">{msg.tool}</span>
                </div>
              )}
              <div className="text-sm leading-relaxed">{msg.role === "assistant" ? formatMessage(msg.content) : msg.content}</div>
              {msg.table && <StructuredTable table={msg.table} />}
              {msg.sql && <pre className="mt-2 p-2 bg-black/40 text-green-400 rounded text-xs overflow-x-auto">{msg.sql}</pre>}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#0f3460]/50 border border-[#29B5E8]/10 rounded-xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-[#29B5E8] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 bg-[#29B5E8] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 bg-[#29B5E8] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>

      <div className="p-4 border-t border-[#29B5E8]/10">
        <form onSubmit={(e) => { e.preventDefault(); sendMessage() }} className="flex gap-2">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about accounts, pipeline, campaigns, service, or advisor notes…"
            className="flex-1 px-4 py-2.5 bg-[#0B1929] border border-[#29B5E8]/20 text-blue-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#29B5E8] text-sm" />
          <button type="submit" disabled={loading || !input.trim()}
            className="px-6 py-2.5 bg-[#29B5E8] hover:bg-[#1a9dd4] text-white rounded-lg font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
