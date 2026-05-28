import { NextRequest, NextResponse } from 'next/server';
import * as fs from 'node:fs';

export const dynamic = 'force-dynamic';

function getToken(): string {
  try { return fs.readFileSync('/snowflake/session/token', 'utf-8').trim(); } catch { return process.env.SNOWFLAKE_TOKEN || ''; }
}
function getHost(): string {
  if (process.env.SNOWFLAKE_HOST) return process.env.SNOWFLAKE_HOST;
  return 'sfsenorthamerica-dhall-aws1.snowflakecomputing.com';
}

async function runSQL(sql: string, warehouse = 'COMCAST_DEMO_WH'): Promise<any> {
  const host = getHost();
  const token = getToken();
  const resp = await fetch(`https://${host}/api/v2/statements`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', 'X-Snowflake-Authorization-Token-Type': 'OAUTH' },
    body: JSON.stringify({ statement: sql, warehouse, database: 'COMCAST_CYBER_DEMO', schema: 'CERT_SECURITY', timeout: 60 })
  });
  return resp.json();
}

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q');

  if (q === 'kpis') {
    const IWH = 'CERT_COMPLIANCE_IWH';
    const sql = `
      SELECT
        SUM(cert_count) AS total,
        SUM(CASE WHEN compliance_status='COMPLIANT' THEN cert_count ELSE 0 END) AS compliant,
        SUM(CASE WHEN compliance_status='NON_COMPLIANT' THEN cert_count ELSE 0 END) AS non_compliant,
        SUM(CASE WHEN compliance_status='EXPIRING_SOON' THEN cert_count ELSE 0 END) AS expiring,
        SUM(CASE WHEN compliance_status='EXPIRED' THEN cert_count ELSE 0 END) AS expired,
        SUM(self_signed_count) AS self_signed,
        ROUND(100.0*SUM(CASE WHEN compliance_status='COMPLIANT' THEN cert_count ELSE 0 END)/SUM(cert_count),1) AS compliance_rate
      FROM CERT_COMPLIANCE_INTERACTIVE
    `;
    const regionSql = `
      SELECT region, SUM(cert_count) AS total,
        ROUND(100.0*SUM(CASE WHEN compliance_status='COMPLIANT' THEN cert_count ELSE 0 END)/SUM(cert_count),1) AS compliance_pct,
        SUM(CASE WHEN compliance_status='NON_COMPLIANT' THEN cert_count ELSE 0 END) AS non_compliant
      FROM CERT_COMPLIANCE_INTERACTIVE GROUP BY 1 ORDER BY 2 DESC
    `;
    const deviceSql = `
      SELECT device_type, SUM(cert_count) AS total,
        SUM(self_signed_count) AS self_signed,
        SUM(CASE WHEN compliance_status='EXPIRED' THEN cert_count ELSE 0 END) AS expired
      FROM CERT_COMPLIANCE_INTERACTIVE GROUP BY 1 ORDER BY 2 DESC
    `;

    try {
      const [kpiRes, regionRes, deviceRes] = await Promise.all([runSQL(sql, IWH), runSQL(regionSql, IWH), runSQL(deviceSql, IWH)]);
      const row = kpiRes.data?.[0] || [];
      const kpis = [
        { label: 'Total Certificates', value: fmtNum(Number(row[0])), sub: 'Active inventory', color: '#29a8ff' },
        { label: 'Compliance Rate', value: row[6] + '%', sub: fmtNum(Number(row[1])) + ' compliant', color: '#4caf50' },
        { label: 'Expiring (30 days)', value: fmtNum(Number(row[3])), sub: 'Requires renewal action', color: '#ffc107' },
        { label: 'Non-Compliant', value: fmtNum(Number(row[2])), sub: 'Policy violations', color: '#ff5722' },
        { label: 'Expired', value: fmtNum(Number(row[4])), sub: 'Needs immediate remediation', color: '#e91e63' },
        { label: 'Self-Signed', value: fmtNum(Number(row[5])), sub: 'Prohibited in production', color: '#9c27b0' },
      ];
      const byRegion = (regionRes.data || []).map((r: any) => ({ region: r[0], total: Number(r[1]), compliance_pct: r[2], non_compliant: Number(r[3]) }));
      const byDevice = (deviceRes.data || []).map((r: any) => ({ device_type: r[0], total: Number(r[1]), self_signed: Number(r[2]), expired: Number(r[3]) }));
      return NextResponse.json({ kpis, byRegion, byDevice });
    } catch (e: any) {
      return NextResponse.json({ error: e.message }, { status: 500 });
    }
  }

  if (q === 'geo') {
    const sql = `
      SELECT d.dc_name, d.city, d.latitude, d.longitude, d.region,
        COUNT(*) AS cert_count,
        SUM(CASE WHEN compliance_status='NON_COMPLIANT' THEN 1 ELSE 0 END) AS non_compliant,
        ROUND(100.0*SUM(CASE WHEN compliance_status='COMPLIANT' THEN 1 ELSE 0 END)/COUNT(*),1) AS compliance_pct
      FROM V_CERTIFICATES_FULL v
      JOIN DATA_CENTERS d ON v.data_center_id = d.dc_id
      GROUP BY 1,2,3,4,5
      ORDER BY cert_count DESC
    `;
    try {
      const res = await runSQL(sql);
      const data = (res.data || []).map((r: any) => ({ name: r[0], city: r[1], lat: Number(r[2]), lng: Number(r[3]), region: r[4], certs: Number(r[5]), nonCompliant: Number(r[6]), compliancePct: Number(r[7]) }));
      return NextResponse.json({ locations: data });
    } catch (e: any) {
      return NextResponse.json({ error: e.message }, { status: 500 });
    }
  }

  if (q === 'partners') {
    const sql = `
      SELECT partner_display_name, partner_tier, partner_industry, COUNT(*) AS total,
        ROUND(100.0*SUM(CASE WHEN compliance_status='COMPLIANT' THEN 1 ELSE 0 END)/COUNT(*),1) AS compliance_pct,
        SUM(CASE WHEN compliance_status='NON_COMPLIANT' THEN 1 ELSE 0 END) AS non_compliant,
        SUM(CASE WHEN is_self_signed THEN 1 ELSE 0 END) AS self_signed
      FROM V_CERTIFICATES_FULL GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 50
    `;
    try {
      const res = await runSQL(sql);
      const data = (res.data || []).map((r: any) => ({ partner: r[0], tier: r[1], industry: r[2], total: Number(r[3]), compliancePct: Number(r[4]), nonCompliant: Number(r[5]), selfSigned: Number(r[6]) }));
      return NextResponse.json({ partners: data });
    } catch (e: any) {
      return NextResponse.json({ error: e.message }, { status: 500 });
    }
  }

  if (q === 'lifecycle') {
    const sql = `
      SELECT new_state, COUNT(*) AS cnt, triggered_by
      FROM CERT_LIFECYCLE_EVENTS
      GROUP BY 1, 3 ORDER BY 2 DESC
    `;
    const recentSql = `
      SELECT cert_id, previous_state, new_state, event_timestamp, triggered_by
      FROM CERT_LIFECYCLE_EVENTS ORDER BY event_timestamp DESC LIMIT 20
    `;
    try {
      const [stateRes, recentRes] = await Promise.all([runSQL(sql), runSQL(recentSql)]);
      const byState = (stateRes.data || []).map((r: any) => ({ state: r[0], count: Number(r[1]), trigger: r[2] }));
      const recent = (recentRes.data || []).map((r: any) => ({ certId: r[0], from: r[1], to: r[2], ts: r[3], trigger: r[4] }));
      return NextResponse.json({ byState, recent });
    } catch (e: any) { return NextResponse.json({ error: e.message }, { status: 500 }); }
  }

  if (q === 'forecast') {
    const sql = `SELECT region, TO_VARCHAR(forecast_date, 'YYYY-MM-DD') AS fd, predicted_expiring, lower_bound, upper_bound FROM CERT_EXPIRY_PREDICTIONS ORDER BY region, forecast_date`;
    const historySql = `SELECT TO_VARCHAR(expiry_date, 'YYYY-MM-DD'), region, expiring_certs FROM V_EXPIRY_TIMESERIES WHERE expiry_date >= DATEADD('day', -30, CURRENT_DATE()) ORDER BY region, expiry_date`;
    try {
      const [fcRes, histRes] = await Promise.all([runSQL(sql), runSQL(historySql)]);
      const forecast = (fcRes.data || []).map((r: any) => ({ region: String(r[0]).replace(/"/g, ''), date: r[1], predicted: Number(r[2]), lower: Number(r[3]), upper: Number(r[4]) }));
      const history = (histRes.data || []).map((r: any) => ({ date: r[0], region: String(r[1]).replace(/"/g, ''), actual: Number(r[2]) }));
      return NextResponse.json({ forecast, history });
    } catch (e: any) { return NextResponse.json({ error: e.message }, { status: 500 }); }
  }

  if (q === 'chains') {
    const sql = `
      SELECT ic.ca_name, ic.issuing_org, rc.ca_name AS root_ca, rc.trust_store, 
        COUNT(*) AS chain_count, SUM(CASE WHEN ch.chain_valid THEN 1 ELSE 0 END) AS valid_count,
        ROUND(ic.revocation_rate * 100, 2) AS revocation_pct
      FROM CERT_CHAINS ch
      JOIN INTERMEDIATE_CAS ic ON ch.intermediate_cert_id = ic.ca_id
      JOIN ROOT_CAS rc ON ch.root_ca_id = rc.root_ca_id
      GROUP BY 1,2,3,4,7 ORDER BY 5 DESC
    `;
    try {
      const res = await runSQL(sql);
      const chains = (res.data || []).map((r: any) => ({ intermediate: r[0], org: r[1], rootCa: r[2], trustStore: r[3], count: Number(r[4]), valid: Number(r[5]), revocationPct: Number(r[6]) }));
      return NextResponse.json({ chains });
    } catch (e: any) { return NextResponse.json({ error: e.message }, { status: 500 }); }
  }

  return NextResponse.json({ error: 'Unknown query parameter' }, { status: 400 });
}

function fmtNum(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(0) + 'K';
  return String(n);
}
