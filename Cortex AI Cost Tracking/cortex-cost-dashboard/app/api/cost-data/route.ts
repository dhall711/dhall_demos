import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

async function getLocalData() {
  const filePath = path.join(process.cwd(), "public", "data.json");
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw);
}

async function getLiveData() {
  const { query } = await import("@/lib/snowflake");

  const db = process.env.SNOWFLAKE_DATABASE;
  const schema = process.env.SNOWFLAKE_SCHEMA;

  if (!db || !schema) {
    throw new Error("SNOWFLAKE_DATABASE and SNOWFLAKE_SCHEMA environment variables are required");
  }

  const fqv = `${db}.${schema}.CORTEX_AI_SUMMARY_COST_VIEW`;

  const [monthly, daily, weekly, yearly, byService, byComponent, byUser, byWarehouse, byObject, byAgent, detail, totals, tokensByService] =
    await Promise.all([
      query(`
        SELECT DATE_TRUNC('MONTH', START_TIME) AS PERIOD,
               ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS,
               ROUND(SUM(SUM(COALESCE(COMPONENT_CREDITS, 0))) OVER (ORDER BY DATE_TRUNC('MONTH', START_TIME)), 2) AS CUMULATIVE_CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 1
      `),
      query(`
        SELECT DATE_TRUNC('DAY', START_TIME) AS PERIOD,
               ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 4) AS CREDITS,
               ROUND(SUM(SUM(COALESCE(COMPONENT_CREDITS, 0))) OVER (ORDER BY DATE_TRUNC('DAY', START_TIME)), 4) AS CUMULATIVE_CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 1
      `),
      query(`
        SELECT DATE_TRUNC('WEEK', START_TIME) AS PERIOD,
               ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS,
               ROUND(SUM(SUM(COALESCE(COMPONENT_CREDITS, 0))) OVER (ORDER BY DATE_TRUNC('WEEK', START_TIME)), 2) AS CUMULATIVE_CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 1
      `),
      query(`
        SELECT DATE_TRUNC('YEAR', START_TIME) AS PERIOD,
               ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS,
               ROUND(SUM(SUM(COALESCE(COMPONENT_CREDITS, 0))) OVER (ORDER BY DATE_TRUNC('YEAR', START_TIME)), 2) AS CUMULATIVE_CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 1
      `),
      query(`
        SELECT SERVICE_TYPE AS NAME, ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 2 DESC
      `),
      query(`
        SELECT COST_COMPONENT AS NAME, ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 2 DESC
      `),
      query(`
        SELECT END_USER_NAME AS NAME, ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 2 DESC LIMIT 10
      `),
      query(`
        SELECT WAREHOUSE_NAME AS NAME, ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS
        FROM ${fqv} WHERE WAREHOUSE_NAME IS NOT NULL AND WAREHOUSE_NAME != '' AND WAREHOUSE_NAME != 'N/A'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 10
      `),
      query(`
        SELECT SERVICE_TYPE || ' | ' || COALESCE(COMPONENT_OBJECT_NAME, '') AS NAME,
               ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS
        FROM ${fqv} GROUP BY 1 ORDER BY 2 DESC LIMIT 10
      `),
      query(`
        SELECT COMPONENT_OBJECT_NAME AS NAME, ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS CREDITS
        FROM ${fqv}
        WHERE SERVICE_TYPE = 'CORTEX AGENT'
        GROUP BY 1 ORDER BY 2 DESC
      `),
      query(`
        SELECT START_TIME, END_USER_NAME, SERVICE_TYPE, COST_COMPONENT,
               COMPONENT_DESCRIPTION, WAREHOUSE_NAME, COMPONENT_OBJECT_NAME,
               ROUND(COALESCE(COMPONENT_CREDITS, 0), 4) AS COMPONENT_CREDITS,
               COALESCE(INPUT_TOKENS, 0) AS INPUT_TOKENS,
               COALESCE(OUTPUT_TOKENS, 0) AS OUTPUT_TOKENS,
               COALESCE(TOTAL_TOKENS, 0) AS TOTAL_TOKENS
        FROM ${fqv} ORDER BY START_TIME DESC LIMIT 200
      `),
      query(`
        SELECT ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 2) AS TOTAL_CREDITS,
               COUNT(DISTINCT END_USER_NAME) AS UNIQUE_USERS,
               COUNT(*) AS TOTAL_QUERIES,
               COUNT(DISTINCT SERVICE_TYPE) AS SERVICE_TYPES,
               SUM(COALESCE(INPUT_TOKENS, 0)) AS TOTAL_INPUT_TOKENS,
               SUM(COALESCE(OUTPUT_TOKENS, 0)) AS TOTAL_OUTPUT_TOKENS,
               SUM(COALESCE(TOTAL_TOKENS, 0)) AS TOTAL_TOKENS
        FROM ${fqv}
      `),
      query(`
        SELECT SERVICE_TYPE AS NAME,
               SUM(COALESCE(INPUT_TOKENS, 0)) AS INPUT_TOKENS,
               SUM(COALESCE(OUTPUT_TOKENS, 0)) AS OUTPUT_TOKENS,
               SUM(COALESCE(TOTAL_TOKENS, 0)) AS TOTAL_TOKENS
        FROM ${fqv} WHERE TOTAL_TOKENS > 0 GROUP BY 1 ORDER BY 4 DESC
      `),
    ]);

  return { totals: totals[0], monthly, daily, weekly, yearly, byService, byComponent, byUser, byWarehouse, byObject, byAgent, detail, tokensByService };
}

export async function GET() {
  try {
    const isSpcs = fs.existsSync("/snowflake/session/token");
    const data = isSpcs ? await getLiveData() : await getLocalData();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error:", error);
    return NextResponse.json({ error: "Failed to fetch data" }, { status: 500 });
  }
}
