import { getServiceToken } from "@/lib/snowflake"

export const dynamic = "force-dynamic"

const AGENT_PATH =
  "/api/v2/databases/FIVETRAN_CRM_CUSTOMER360/schemas/ANALYTICS/agents/CUSTOMER360_AGENT:run"

function accountBaseUrl(): string {
  if (process.env.SNOWFLAKE_ACCOUNT_URL) return process.env.SNOWFLAKE_ACCOUNT_URL.replace(/\/$/, "")
  if (process.env.SNOWFLAKE_HOST) return `https://${process.env.SNOWFLAKE_HOST}`
  throw new Error("No SNOWFLAKE_HOST / SNOWFLAKE_ACCOUNT_URL available to reach the Agent API")
}

interface AgentTable {
  columns: string[]
  rows: any[][]
  title?: string
}

/** Convert a Snowflake SQL-API ResultSet into {columns, rows} for the UI. */
function resultSetToTable(rs: any, title?: string): AgentTable | null {
  const rowType = rs?.resultSetMetaData?.rowType
  const data = rs?.data
  if (!Array.isArray(rowType) || !Array.isArray(data)) return null
  return { columns: rowType.map((c: any) => c.name), rows: data, title }
}

/**
 * Parse a non-streaming Cortex Agent response (the `response` object).
 * content[] holds typed items: text, thinking, tool_use, tool_result, table, chart.
 */
function parseAgentResponse(resp: any): { text: string; sql: string; table: AgentTable | null } {
  let text = ""
  let sql = ""
  let table: AgentTable | null = null

  for (const item of resp?.content ?? []) {
    if (item?.type === "text" && typeof item.text === "string") {
      text += item.text
    } else if (item?.type === "table" && item.table) {
      if (!table) table = resultSetToTable(item.table.result_set, item.table.title)
    } else if (item?.type === "tool_result") {
      for (const c of item.tool_result?.content ?? []) {
        const j = c?.json
        if (!j) continue
        if (j.sql && !sql) sql = j.sql
      }
    }
  }
  return { text: text.trim(), sql, table }
}

export async function POST(request: Request) {
  try {
    const { question } = await request.json()
    if (!question || typeof question !== "string") {
      return Response.json({ error: "Missing 'question'" }, { status: 400 })
    }

    const token = getServiceToken()
    if (!token) {
      return Response.json({
        text: "The live Cortex Agent is only reachable when the app runs in Snowflake (SPCS). Deploy the app to chat with CUSTOMER360_AGENT.",
        tool: "Agent (unavailable in local dev)",
      })
    }

    const url = accountBaseUrl() + AGENT_PATH
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-Snowflake-Authorization-Token-Type": "OAUTH",
      },
      body: JSON.stringify({
        stream: false,
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

    const data = await resp.json()
    const { text, sql, table } = parseAgentResponse(data)
    return Response.json({
      text: text || "The agent completed but returned no text answer.",
      sql,
      table,
      tool: "CUSTOMER360_AGENT (Cortex Agent)",
    })
  } catch (e) {
    console.error(new Date().toISOString(), "[agent] call failed", e)
    return Response.json(
      { error: e instanceof Error ? e.message : "Agent call failed" },
      { status: 500 }
    )
  }
}
