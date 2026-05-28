const SEED_CACHE: Record<string, string> = {};

// === DASHBOARD PAGE SEEDS ===

SEED_CACHE['dashboard:Compliance Rate'] = `## Compliance Rate Analysis

The overall compliance rate is **75.0%**, which is **10 percentage points below** the 85% target. Here are the main drivers of non-compliance:

| Violation Type | Count | % of Non-Compliant |
|---|---|---|
| Weak Key Size (< 2048-bit) | 4.2M | 33.6% |
| Self-Signed Certificate | 3.8M | 30.4% |
| SHA-1 Signature Algorithm | 3.2M | 25.6% |
| Expired Certificate | 1.3M | 10.4% |

### Regional Breakdown
| Region | Compliance Rate | Gap to Target |
|---|---|---|
| EU | 78.2% | -6.8% |
| NA | 76.1% | -8.9% |
| APAC | 72.4% | -12.6% |
| LATAM | 69.8% | -15.2% |

**Key Insight**: LATAM and APAC are dragging down the global average. The primary drivers are IoT devices with self-signed certificates and legacy partners still using SHA-1 signing. The top 5 non-compliant partners account for 42% of all violations.

**Recommended Actions**:
1. Prioritize LATAM partner outreach — 3 partners below 60%
2. Enforce ACME auto-renewal for IoT fleet (addresses 60% of expiry issues)
3. Set hard deadline for SHA-1 deprecation (currently ~1.6M certs)`;

SEED_CACHE['dashboard:Total Certificates'] = `## Certificate Inventory Summary

Total certificates under management: **50,000,000**

### By Region
| Region | Count | % of Total |
|---|---|---|
| NA | 22.5M | 45.0% |
| EU | 13.5M | 27.0% |
| APAC | 9.0M | 18.0% |
| LATAM | 5.0M | 10.0% |

### By Device Type
| Device Type | Count | % of Total | Compliance Rate |
|---|---|---|---|
| IoT | 30.0M | 60.0% | 71.2% |
| Streaming | 8.5M | 17.0% | 79.4% |
| Gateway | 6.0M | 12.0% | 82.1% |
| Server | 3.5M | 7.0% | 88.3% |
| Partner | 2.0M | 4.0% | 74.6% |

**Key Insight**: IoT devices represent 60% of the certificate inventory but have the lowest compliance rate. The high volume combined with self-signed certificates and weak key sizes makes IoT the highest-priority remediation target.`;

SEED_CACHE['dashboard:Expiring (30 days)'] = `## Certificates Expiring Within 30 Days

**~2.0 million certificates** will expire in the next 30 days across all regions.

### By Device Type
| Device Type | Expiring (30d) | Auto-Renewal Coverage |
|---|---|---|
| IoT | 1.2M | 45% (ACME) |
| Streaming | 380K | 72% (ACME) |
| Gateway | 220K | 68% (ACME) |
| Server | 120K | 91% (manual + ACME) |
| Partner | 80K | 35% (manual) |

### By Region
| Region | Expiring | Highest Risk Partner |
|---|---|---|
| NA | 900K | Aruba Networks (124K) |
| EU | 540K | Nokia (89K) |
| APAC | 360K | Huawei (67K) |
| LATAM | 200K | ZTE Corp (45K) |

**Critical Alert**: 340K IoT certificates expiring within 7 days do NOT have auto-renewal configured. These require immediate manual intervention or ACME enrollment.

**Recommendations**:
1. Enroll all IoT expiring certs in ACME auto-renewal immediately
2. Alert top 10 partners with >50K expiring certs
3. Escalate 7-day critical infrastructure certs to NOC`;

SEED_CACHE['dashboard:Non-Compliant'] = `## Non-Compliant Certificate Breakdown

**12.5 million certificates** (25.0%) are currently non-compliant.

### By Violation Type
| Violation | Count | Severity |
|---|---|---|
| Weak Key (RSA < 2048) | 4.2M | HIGH |
| Self-Signed | 3.8M | HIGH |
| SHA-1 Algorithm | 3.2M | MEDIUM |
| Expired | 1.3M | CRITICAL |

### By Region
| Region | Non-Compliant | Rate |
|---|---|---|
| NA | 5.4M | 24.0% |
| EU | 2.9M | 21.8% |
| APAC | 2.5M | 27.6% |
| LATAM | 1.7M | 30.2% |

**Key Insight**: LATAM has the highest non-compliance rate at 30.2%, primarily driven by partner devices using legacy PKI infrastructure. The 1.3M expired certificates represent immediate security risk and should be the top priority for remediation.`;

// === INVESTIGATE PAGE SEEDS ===

SEED_CACHE['investigate:compliance_rate'] = SEED_CACHE['dashboard:Compliance Rate'];

SEED_CACHE['investigate:expiring_30d'] = SEED_CACHE['dashboard:Expiring (30 days)'];

SEED_CACHE['investigate:self_signed'] = `## Self-Signed Certificate Analysis

**3.8 million self-signed certificates** are in the inventory, representing a significant compliance risk.

### By Device Type
| Device Type | Self-Signed | % of Device Fleet |
|---|---|---|
| IoT | 2.4M | 8.0% |
| Partner | 680K | 34.0% |
| Gateway | 420K | 7.0% |
| Streaming | 200K | 2.4% |
| Server | 100K | 2.9% |

### Top Partners Using Self-Signed
| Partner | Self-Signed Certs | Industry |
|---|---|---|
| Aruba Networks | 340K | Networking |
| ZTE Corp | 280K | Telecom |
| Juniper | 195K | Networking |
| Huawei | 180K | Telecom |
| Palo Alto Networks | 145K | Security |

### Policy Reference
Per the **Certificate Compliance Policy v3.2**, self-signed certificates are:
- **Prohibited** in production environments
- **Allowed** only for internal development/testing with 90-day max validity
- Subject to **mandatory replacement** within 60 days of detection

**Remediation Plan**:
1. Partner devices: Issue CA-signed replacements via ACME enrollment
2. IoT fleet: Batch re-issue through automated provisioning pipeline
3. Set enforcement deadline: Q3 2026 for zero self-signed in production`;

SEED_CACHE['investigate:sha1_deprecated'] = `## SHA-1 Signature Algorithm Analysis

**~3.2 million certificates** still use the deprecated SHA-1 signing algorithm.

### By Region
| Region | SHA-1 Certs | % of Region |
|---|---|---|
| APAC | 1.1M | 12.2% |
| LATAM | 720K | 14.4% |
| NA | 890K | 4.0% |
| EU | 490K | 3.6% |

### By Device Type
| Device Type | SHA-1 Certs | % of Type |
|---|---|---|
| IoT | 1.9M | 6.3% |
| Partner | 520K | 26.0% |
| Gateway | 440K | 7.3% |
| Streaming | 220K | 2.6% |
| Server | 120K | 3.4% |

### Deprecation Policy
Per **NIST SP 800-131A Rev.2** and internal policy:
- SHA-1 is **disallowed** for digital signatures after 12/31/2025
- Replacement must use **SHA-256 or SHA-384**
- All SHA-1 certificates must be replaced by **Q2 2026**

**Key Risk**: APAC and LATAM have disproportionately high SHA-1 usage, primarily in IoT and partner devices running legacy firmware that doesn't support SHA-256.

**Recommendations**:
1. Force firmware upgrades for IoT devices supporting SHA-256
2. Issue replacement certificates with SHA-256 for capable devices
3. Isolate non-upgradeable devices to restricted network segments`;

SEED_CACHE['investigate:partner_risk'] = `## At-Risk Partners (Compliance < 60%)

**5 partners** currently have compliance rates below the 60% critical threshold:

| Partner | Compliance | Total Certs | Primary Violation | Tier |
|---|---|---|---|---|
| ZTE Corp | 48.2% | 1.8M | Self-Signed + SHA-1 | BRONZE |
| Huawei Technologies | 52.1% | 2.1M | Weak Key Size | BRONZE |
| Legacy Telecom Co | 55.4% | 890K | Expired + SHA-1 | BRONZE |
| IoT Innovations | 57.8% | 1.2M | Self-Signed | SILVER |
| Pacific Networks | 59.1% | 640K | Weak Key + SHA-1 | BRONZE |

### SLA Impact
Per the **Partner Compliance SLA Agreement**:
- Below 60%: **30-day remediation notice** + quarterly review
- Below 50%: **Suspension warning** + weekly check-ins required
- Below 40%: **Certificate issuance suspended** pending remediation

### Remediation Status
- ZTE Corp: Remediation plan submitted, migration to SHA-256 in progress
- Huawei: Key rotation program started, ETA 6 weeks
- Legacy Telecom: No response to remediation notice — **escalation required**

**Recommended Actions**:
1. Escalate Legacy Telecom to partner management
2. Schedule weekly syncs with ZTE and Huawei
3. Block new cert issuance for partners below 50% after 30-day notice`;

// === DEVICES PAGE SEEDS ===

SEED_CACHE['devices:IoT'] = `## IoT Device Certificate Analysis

IoT represents the largest certificate fleet with **30.0M certificates** (60% of total inventory).

### Compliance Profile
| Metric | Value |
|---|---|
| Total Certificates | 30.0M |
| Compliance Rate | 71.2% |
| Self-Signed | 2.4M (8.0%) |
| Expired | 780K (2.6%) |
| Weak Key (< 2048-bit) | 3.1M (10.3%) |
| SHA-1 Signatures | 1.9M (6.3%) |

### Top Partners Issuing IoT Certs
| Partner | IoT Certs | Compliance |
|---|---|---|
| Comcast Internal | 12.4M | 78.5% |
| Aruba Networks | 4.2M | 65.3% |
| Cisco Systems | 3.8M | 82.1% |
| Huawei | 2.9M | 54.2% |
| ZTE Corp | 2.1M | 48.8% |

### Key Risks
1. **Scale**: At 30M certs, even small % non-compliance = millions of vulnerable devices
2. **Auto-renewal gap**: Only 45% of IoT certs have ACME auto-renewal
3. **Firmware constraints**: Many IoT devices can't support key rotation without OTA update
4. **Partner dependency**: 5 partners control 83% of IoT cert issuance

**Recommendations**:
- Mandate ACME enrollment for all new IoT provisioning
- Prioritize Huawei and ZTE IoT fleet for key rotation
- Implement certificate pinning for critical infrastructure IoT`;

SEED_CACHE['devices:Streaming'] = `## Streaming Device Certificate Analysis

Streaming devices hold **8.5M certificates** (17% of inventory) supporting video delivery infrastructure.

### Compliance Profile
| Metric | Value |
|---|---|
| Total Certificates | 8.5M |
| Compliance Rate | 79.4% |
| Self-Signed | 200K (2.4%) |
| Expired | 180K (2.1%) |
| Weak Key | 1.1M (12.9%) |

### By Region
| Region | Streaming Certs | Compliance |
|---|---|---|
| NA | 4.1M | 81.2% |
| EU | 2.3M | 79.8% |
| APAC | 1.4M | 75.6% |
| LATAM | 700K | 72.1% |

**Key Insight**: Streaming has relatively good compliance (79.4%) but the weak key issue (12.9%) is concerning — streaming requires 4096-bit RSA per policy for content protection. The 1.1M certs with 2048-bit keys need rotation to 4096-bit.

**Recommendations**:
1. Bulk re-issue streaming certs with 4096-bit RSA keys
2. Prioritize CDN edge nodes (highest traffic)
3. Auto-renewal coverage is already 72% — push to 95%`;

// === PARTNERS PAGE SEEDS (top few likely clicks) ===

SEED_CACHE['partners:Aruba Networks'] = `## Aruba Networks Certificate Compliance

| Metric | Value |
|---|---|
| Total Certificates | 4.2M |
| Compliance Rate | 65.3% |
| Non-Compliant | 1.46M |
| Self-Signed | 340K |
| Tier | SILVER |
| Industry | Networking |

### Violation Breakdown
| Violation Type | Count | % |
|---|---|---|
| Weak Key Size (1024-bit) | 680K | 46.6% |
| Self-Signed | 340K | 23.3% |
| SHA-1 Signature | 290K | 19.9% |
| Expired | 150K | 10.3% |

### Affected Device Types
| Device | Certs | Compliance |
|---|---|---|
| IoT | 2.8M | 62.1% |
| Gateway | 980K | 71.4% |
| Partner | 420K | 68.9% |

**Root Cause**: Aruba's IoT provisioning system defaults to 1024-bit RSA keys. Their firmware v7.x doesn't support 2048-bit without an upgrade. Migration to v8.x is underway but only 35% deployed.

**Remediation Priority**:
1. Accelerate firmware v8.x rollout to remaining 65% of fleet
2. Re-issue all 1024-bit certificates with 2048-bit keys post-upgrade
3. Enroll all Aruba devices in ACME auto-renewal
4. Target: 80% compliance by Q3 2026`;

// === FORECAST PAGE SEEDS ===

SEED_CACHE['forecast:NA'] = `## North America 14-Day Expiry Forecast

The ML model predicts **~630K certificates** will expire in NA over the next 14 days.

### Daily Breakdown (Next 7 Days)
| Day | Predicted | Confidence Range |
|---|---|---|
| Day 1 | 89K | 82K – 96K |
| Day 2 | 91K | 84K – 98K |
| Day 3 | 87K | 80K – 94K |
| Day 4 | 93K | 86K – 100K |
| Day 5 | 88K | 81K – 95K |
| Day 6 | 90K | 83K – 97K |
| Day 7 | 92K | 85K – 99K |

### Most Affected Partners
| Partner | Expiring (7d) | Auto-Renewal % |
|---|---|---|
| Aruba Networks | 124K | 42% |
| Cisco Systems | 98K | 78% |
| Comcast Internal | 210K | 85% |
| DigiCert | 67K | 91% |

### Capacity Planning
- **Peak day**: ~93K expirations (Day 4)
- **ACME capacity needed**: 65K renewals/day (current capacity: 80K ✓)
- **Manual renewal queue**: ~28K/day (current team capacity: 15K ⚠️)

**Action Required**: Manual renewal capacity is under-provisioned for the forecasted peak. Recommend:
1. Temporarily scale renewal team or authorize batch auto-approval
2. Pre-approve Aruba Networks bulk renewal (124K certs, low risk)
3. Alert Cisco partner team to ensure their 78% auto-renewal covers critical infra`;

SEED_CACHE['forecast:EU'] = `## EU Region 14-Day Expiry Forecast

The ML model predicts **~380K certificates** will expire in EU over the next 14 days.

### Daily Predictions
Average: **~27K/day** with peak of **31K** on Day 6.

### Top Expiring Partners
| Partner | Expiring (7d) | Compliance |
|---|---|---|
| Nokia | 89K | 74.2% |
| DigiCert | 52K | 94.1% |
| Ericsson | 41K | 81.3% |

### Data Residency Note
All EU certificate renewals are processed within EU data centers (Frankfurt, Amsterdam, Dublin) per GDPR data residency requirements. No certificate metadata leaves the EU region.

**Recommendations**:
1. Nokia's 89K expiring certs need attention — only 61% have auto-renewal
2. Pre-stage renewal capacity in Frankfurt DC for peak Day 6
3. Verify GDPR-compliant renewal pipeline for all EU partner certs`;

// === LIFECYCLE PAGE SEEDS ===

SEED_CACHE['lifecycle:EXPIRING'] = `## Certificates in EXPIRING State

**~2.0M certificates** are currently in the EXPIRING state (validity_end within 30 days).

### Transition Triggers
| Trigger | Count | % |
|---|---|---|
| 30-day threshold crossed | 1.4M | 70% |
| Partner notification sent | 380K | 19% |
| Manual review flagged | 220K | 11% |

### By Device Type
| Device | Expiring | Auto-Renewal Configured |
|---|---|---|
| IoT | 1.2M | 45% |
| Streaming | 380K | 72% |
| Gateway | 220K | 68% |
| Server | 120K | 91% |
| Partner | 80K | 35% |

### Expected State Transitions (Next 7 Days)
- **→ RENEWED**: ~850K (auto-renewal will process)
- **→ EXPIRED**: ~340K (no renewal configured, manual action needed)
- **Remaining EXPIRING**: ~810K (will transition in days 8-30)

**Critical**: 340K certificates will expire without renewal in the next 7 days. These require immediate intervention — primarily IoT devices (220K) and Partner devices (65K) without ACME enrollment.`;

SEED_CACHE['lifecycle:EXPIRED'] = `## Certificates in EXPIRED State

**~1.3M certificates** have expired and not been renewed.

### Age Distribution
| Expired Since | Count | Risk Level |
|---|---|---|
| < 7 days | 180K | HIGH |
| 7-30 days | 420K | HIGH |
| 30-90 days | 480K | CRITICAL |
| > 90 days | 220K | CRITICAL |

### By Device Type
| Device | Expired | % of Fleet |
|---|---|---|
| IoT | 780K | 2.6% |
| Partner | 240K | 12.0% |
| Gateway | 160K | 2.7% |
| Streaming | 80K | 0.9% |
| Server | 40K | 1.1% |

**Key Concern**: 700K certificates have been expired for over 30 days — these represent devices actively communicating with expired credentials, which is a security vulnerability.

**Recommended Actions**:
1. Force-revoke certificates expired > 90 days (220K) — likely abandoned devices
2. Initiate emergency renewal for < 7 day expired certs (180K)
3. Quarantine devices with 30-90 day expired certs pending investigation`;

// === CHAINS PAGE SEEDS ===

SEED_CACHE['chains:Comcast Internal CA G2'] = `## Chain Investigation: Comcast Internal CA G2

This intermediate CA is the **primary internal issuer** for Comcast's certificate fleet.

| Attribute | Value |
|---|---|
| Issuing Organization | Comcast Corporation |
| Root CA | Comcast Root CA |
| Trust Store | Internal + Mozilla NSS |
| Total Chains | 18.2K |
| Valid Chains | 17.8K (97.8%) |
| Revocation Rate | 0.8% |

### Issued Certificate Profile
- **Device Types**: Primarily IoT (65%) and Gateway (20%)
- **Key Algorithms**: RSA 2048 (72%), RSA 4096 (18%), ECDSA P-256 (10%)
- **Average Validity**: 365 days
- **Auto-Renewal**: 82% ACME coverage

### Chain Validity Issues (400 invalid)
| Issue | Count |
|---|---|
| Intermediate expired | 180 |
| CRL unreachable | 120 |
| Path length constraint | 100 |

**Assessment**: This is a healthy CA with 97.8% validity. The 400 invalid chains are primarily due to CRL distribution point issues during scheduled maintenance windows. No immediate action required — monitor CRL availability.`;

export default SEED_CACHE;
