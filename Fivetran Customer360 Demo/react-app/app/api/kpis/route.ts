import { querySnowflake } from "@/lib/snowflake"

export const dynamic = "force-dynamic"

const DB = "FIVETRAN_CRM_CUSTOMER360.GOLD"

export async function GET() {
  try {
    const [kpis] = await querySnowflake(`
      SELECT
        SUM(ANNUAL_REVENUE)  AS AUM,
        COUNT(*)             AS ACCOUNT_COUNT,
        ROUND(AVG(HEALTH_SCORE), 0) AS AVG_HEALTH,
        SUM(PIPELINE_VALUE)  AS PIPELINE_VALUE
      FROM ${DB}.DT_CUSTOMER_360
    `)

    const [pipe] = await querySnowflake(`
      SELECT SUM(PIPELINE_VALUE) AS PIPELINE_VALUE, SUM(OPP_COUNT) AS OPP_COUNT,
             ROUND(AVG(WIN_RATE_PCT), 0) AS WIN_RATE
      FROM ${DB}.DT_PIPELINE_ANALYTICS
    `)

    const pipelineByProduct = await querySnowflake(`
      SELECT PRODUCT_LINE AS NAME, SUM(PIPELINE_VALUE) AS VALUE
      FROM ${DB}.DT_PIPELINE_ANALYTICS
      GROUP BY PRODUCT_LINE ORDER BY VALUE DESC
    `)

    const quarterlyTrend = await querySnowflake(`
      SELECT QUARTER, SUM(WEIGHTED_PIPELINE) AS REVENUE, SUM(PIPELINE_VALUE) AS PIPELINE
      FROM ${DB}.DT_PIPELINE_ANALYTICS
      GROUP BY QUARTER ORDER BY QUARTER
    `)

    const serviceHealth = await querySnowflake(`
      SELECT PRIORITY AS NAME, SUM(CASE_COUNT) AS VALUE
      FROM ${DB}.DT_SERVICE_HEALTH
      GROUP BY PRIORITY ORDER BY VALUE DESC
    `)

    const topAccounts = await querySnowflake(`
      SELECT ACCOUNT_NAME AS NAME, ACCOUNT_TIER AS TIER, INDUSTRY_SEGMENT AS SEGMENT,
             HEALTH_SCORE AS HEALTH, PIPELINE_VALUE AS PIPELINE, OPEN_CASES AS CASES
      FROM ${DB}.DT_CUSTOMER_360
      ORDER BY PIPELINE_VALUE DESC LIMIT 10
    `)

    return Response.json({ kpis, pipe, pipelineByProduct, quarterlyTrend, serviceHealth, topAccounts })
  } catch (e) {
    console.error(new Date().toISOString(), "[kpis] query failed", e)
    return Response.json(
      { error: e instanceof Error ? e.message : "Failed to load KPIs" },
      { status: 500 }
    )
  }
}
