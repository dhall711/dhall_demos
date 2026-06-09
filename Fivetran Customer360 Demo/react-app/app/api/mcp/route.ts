import { querySnowflake } from "@/lib/snowflake"

export const dynamic = "force-dynamic"

const MCP_FQN = "FIVETRAN_CRM_CUSTOMER360.ANALYTICS.CUSTOMER360_MCP_SERVER"

// Returns the live tool list from the Snowflake-managed MCP server.
export async function GET() {
  try {
    const rows = await querySnowflake(`DESCRIBE MCP SERVER ${MCP_FQN}`)
    const specRaw = rows?.[0]?.SERVER_SPEC ?? rows?.[0]?.server_spec ?? "{}"
    let tools: any[] = []
    try {
      tools = JSON.parse(specRaw).tools ?? []
    } catch {
      tools = []
    }
    return Response.json({ server: MCP_FQN, tools })
  } catch (e) {
    console.error(new Date().toISOString(), "[mcp] describe failed", e)
    return Response.json(
      { error: e instanceof Error ? e.message : "Failed to describe MCP server", tools: [] },
      { status: 500 }
    )
  }
}
