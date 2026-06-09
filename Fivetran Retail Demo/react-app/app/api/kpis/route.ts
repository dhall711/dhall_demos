import { querySnowflake } from "@/lib/snowflake"

export const dynamic = "force-dynamic"

const DB = "FIVETRAN_RETAIL_DEMO.GOLD"

export async function GET() {
  try {
    const [kpis] = await querySnowflake(`
      SELECT
        SUM(GROSS_REVENUE)            AS TOTAL_REVENUE,
        SUM(ORDER_COUNT)             AS TOTAL_ORDERS,
        ROUND(SUM(GROSS_REVENUE) / NULLIF(SUM(ORDER_COUNT), 0), 0) AS AVG_ORDER_VALUE,
        SUM(TOTAL_UNITS_SOLD)        AS TOTAL_UNITS
      FROM ${DB}.DT_DAILY_SALES
    `)

    const [cust] = await querySnowflake(`
      SELECT SUM(CUSTOMER_COUNT) AS TOTAL_CUSTOMERS,
             SUM(CASE WHEN CUSTOMER_SEGMENT = 'VIP' THEN CUSTOMER_COUNT ELSE 0 END) AS VIP_CUSTOMERS
      FROM ${DB}.DT_CUSTOMER_SEGMENTS
    `)

    const salesByCategory = await querySnowflake(`
      SELECT CATEGORY, SUM(GROSS_REVENUE) AS REVENUE, SUM(ORDER_COUNT) AS ORDERS
      FROM ${DB}.DT_DAILY_SALES
      GROUP BY CATEGORY ORDER BY REVENUE DESC
    `)

    const monthlyTrend = await querySnowflake(`
      SELECT TO_CHAR(DATE_TRUNC('month', ORDER_DATE), 'Mon YY') AS MONTH,
             DATE_TRUNC('month', ORDER_DATE) AS SORT_KEY,
             SUM(GROSS_REVENUE) AS REVENUE, SUM(ORDER_COUNT) AS ORDERS
      FROM ${DB}.DT_DAILY_SALES
      GROUP BY DATE_TRUNC('month', ORDER_DATE)
      ORDER BY SORT_KEY
    `)

    const customerSegments = await querySnowflake(`
      SELECT CUSTOMER_SEGMENT AS NAME, SUM(CUSTOMER_COUNT) AS VALUE
      FROM ${DB}.DT_CUSTOMER_SEGMENTS
      GROUP BY CUSTOMER_SEGMENT ORDER BY VALUE DESC
    `)

    const topProducts = await querySnowflake(`
      SELECT PRODUCT_NAME AS NAME, BRAND, CATEGORY,
             SUM(TOTAL_REVENUE) AS REVENUE, SUM(TOTAL_ORDERS) AS ORDERS,
             ROUND(AVG(AVG_RATING), 1) AS RATING
      FROM ${DB}.DT_PRODUCT_PERFORMANCE
      GROUP BY PRODUCT_NAME, BRAND, CATEGORY
      ORDER BY REVENUE DESC LIMIT 8
    `)

    return Response.json({ kpis, cust, salesByCategory, monthlyTrend, customerSegments, topProducts })
  } catch (e) {
    console.error(new Date().toISOString(), "[kpis] query failed", e)
    return Response.json(
      { error: e instanceof Error ? e.message : "Failed to load KPIs" },
      { status: 500 }
    )
  }
}
