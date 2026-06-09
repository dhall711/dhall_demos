import { querySnowflake } from "@/lib/snowflake"

export const dynamic = "force-dynamic"

const FN = "FIVETRAN_RETAIL_DEMO.ANALYTICS"

// GET /api/fivetran                         -> all connector statuses
// GET /api/fivetran?history=shopify_orders  -> sync history for one connector
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const history = (searchParams.get("history") ?? "").replace(/[^a-z_]/gi, "")

    if (history) {
      const [r] = await querySnowflake(
        `SELECT ${FN}.GET_FIVETRAN_SYNC_HISTORY('${history}') AS RESULT`
      )
      return Response.json(r?.RESULT ?? {})
    }

    const [r] = await querySnowflake(
      `SELECT ${FN}.GET_FIVETRAN_CONNECTOR_STATUS('all') AS RESULT`
    )
    return Response.json(r?.RESULT ?? { connectors: [] })
  } catch (e) {
    console.error(new Date().toISOString(), "[fivetran] UDF call failed", e)
    return Response.json(
      { error: e instanceof Error ? e.message : "Failed to load Fivetran status" },
      { status: 500 }
    )
  }
}
