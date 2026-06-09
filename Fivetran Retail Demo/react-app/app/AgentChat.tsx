"use client"

import { useState, useRef, useEffect, ReactNode } from "react"

const SAMPLE_QUESTIONS = [
  "What are our top selling categories?",
  "How do VIP customers compare to new customers?",
  "Which products are at risk of stockout?",
  "What are customers saying about electronics?",
  "Show me the monthly sales trend",
  "What is our highest rated product?",
]

interface Message {
  role: "user" | "assistant"
  content: string
  tool?: string
  sql?: string
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
          <tr className="bg-gray-100">
            {header.map((c, j) => (
              <th key={j} className="px-3 py-2 text-left font-medium text-gray-700 border-b">{c.trim()}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, ri) => (
            <tr key={ri} className="border-b border-gray-100 hover:bg-gray-50">
              {row.split("|").filter((c) => c.trim()).map((c, ci) => (
                <td key={ci} className="px-3 py-2 text-gray-600">{c.trim()}</td>
              ))}
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
        setMessages((prev) => [...prev, { role: "assistant", content: data.text, tool: data.tool, sql: data.sql }])
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Request failed: ${String(e)}`, tool: "Error" }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 h-[calc(100vh-220px)] flex flex-col">
      <div className="p-4 border-b bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#29B5E8] rounded-lg flex items-center justify-center text-white text-sm font-bold">AI</div>
          <div>
            <h3 className="font-semibold text-gray-800">Retail Analytics Assistant</h3>
            <p className="text-xs text-gray-500">Powered by RETAIL_AGENT (Cortex Analyst + Search + Fivetran)</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Ask me anything about your retail data</h3>
            <p className="text-sm text-gray-500 mb-6">Live answers from the Cortex Agent over sales, customers, products, inventory, and reviews</p>
            <div className="grid grid-cols-2 gap-2 max-w-xl mx-auto">
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button key={i} onClick={() => sendMessage(q)}
                  className="text-left px-3 py-2.5 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg text-sm text-gray-700 transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-xl px-4 py-3 ${msg.role === "user" ? "bg-[#29B5E8] text-white" : "bg-gray-50 border border-gray-200"}`}>
              {msg.role === "assistant" && msg.tool && (
                <div className="flex items-center gap-1 mb-2">
                  <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">{msg.tool}</span>
                </div>
              )}
              <div className="text-sm leading-relaxed">
                {msg.role === "assistant" ? formatMessage(msg.content) : msg.content}
              </div>
              {msg.sql && (
                <pre className="mt-2 p-2 bg-gray-900 text-green-400 rounded text-xs overflow-x-auto">{msg.sql}</pre>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>

      <div className="p-4 border-t bg-gray-50">
        <form onSubmit={(e) => { e.preventDefault(); sendMessage() }} className="flex gap-2">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about sales, customers, products, inventory, or reviews…"
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#29B5E8] focus:border-transparent text-sm" />
          <button type="submit" disabled={loading || !input.trim()}
            className="px-6 py-2.5 bg-[#29B5E8] hover:bg-[#1a9dd4] text-white rounded-lg font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
