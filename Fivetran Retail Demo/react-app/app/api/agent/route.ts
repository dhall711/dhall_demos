import { getServiceToken } from "@/lib/snowflake"

export const dynamic = "force-dynamic"

const AGENT_PATH =
  "/api/v2/databases/FIVETRAN_RETAIL_DEMO/schemas/ANALYTICS/agents/RETAIL_AGENT:run"

/** Resolve the account base URL for REST calls (SPCS injects SNOWFLAKE_HOST). */
function accountBaseUrl(): string {
  if (process.env.SNOWFLAKE_ACCOUNT_URL) return process.env.SNOWFLAKE_ACCOUNT_URL.replace(/\/$/, "")
  if (process.env.SNOWFLAKE_HOST) return `https://${process.env.SNOWFLAKE_HOST}`
  throw new Error("No SNOWFLAKE_HOST / SNOWFLAKE_ACCOUNT_URL available to reach the Agent API")
}

/**
 * Parse a Cortex Agent SSE response body into a consolidated answer.
 * Accumulates assistant text deltas and captures any SQL emitted by tools.
 */
function parseAgentStream(body: string): { text: string; sql: string } {
  let text = ""
  let sql = ""
  for (const rawLine of body.split("\n")) {
    const line = rawLine.trim()
    if (!line.startsWith("data:")) continue
    const payload = line.slice(5).trim()
    if (!payload || payload === "[DONE]") continue
    let evt: any
    try {
      evt = JSON.parse(payload)
    } catch {
      continue
    }
    // content blocks can appear under delta.content[] or content[]
    const blocks = evt?.delta?.content ?? evt?.content ?? []
    if (Array.isArray(blocks)) {
      for (const b of blocks) {
        if (b?.type === "text" && typeof b.text === "string") text += b.text
        if (b?.type === "tool_results") {
          const items = b?.tool_results?.content ?? []
          for (const it of items) {
            const j = it?.json
            if (j?.sql && !sql) sql = j.sql
            if (j?.text && typeof j.text === "string") text += j.text
          }
        }
      }
    }
    if (typeof evt?.text === "string") text += evt.text
  }
  return { text: text.trim(), sql }
}

export async function POST(request: Request) {
  try {
    const { question } = await request.json()
    if (!question || typeof question !== "string") {
      return Response.json({ error: "Missing 'question'" }, { status: 400 })
    }

    const token = getServiceToken()
    if (!token) {
      // Local dev (no SPCS token): the agent REST path is only available in SPCS.
      return Response.json({
        text: "The live Cortex Agent is only reachable when the app runs in Snowflake (SPCS). Deploy the app to chat with RETAIL_AGENT.",
        tool: "Agent (unavailable in local dev)",
      })
    }

    const url = accountBaseUrl() + AGENT_PATH
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        "X-Snowflake-Authorization-Token-Type": "OAUTH",
      },
      body: JSON.stringify({
        messages: [{ role: "user", content: [{ type: "text", text: question }] }],
      }),
    })

    if (!resp.ok) {
      const errBody = await resp.text()
      console.error(new Date().toISOString(), "[agent] non-200", resp.status, errBody.slice(0, 500))
      return Response.json(
        { error: `Agent API returned ${resp.status}`, detail: errBody.slice(0, 300) },
        { status: 502 }
      )
    }

    const body = await resp.text()
    const { text, sql } = parseAgentStream(body)
    return Response.json({
      text: text || "The agent returned no text response.",
      sql,
      tool: "RETAIL_AGENT (Cortex Agent)",
    })
  } catch (e) {
    console.error(new Date().toISOString(), "[agent] call failed", e)
    return Response.json(
      { error: e instanceof Error ? e.message : "Agent call failed" },
      { status: 500 }
    )
  }
}
