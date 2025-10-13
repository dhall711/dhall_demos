### UDX sensitive data requirements and challenges (Nick’s perspective)

## Context
- UDX operates a large Snowflake estate (~30k tables) across multiple business domains (consumer, team member/HR, vendor), geographies, and systems.
- Prior attempt at auto-tagging/masking had high false positives/negatives, weak logs, and used AI despite legal constraints—eroding trust.

### Core challenges
- **Accuracy issues**: False positives/negatives; lack of confidence thresholds and human-in-the-loop gating.
- **Domain nuance**: Same identifiers (e.g., email) have different governance depending on domain (consumer vs team member vs vendor) and geography.
- **Composite sensitivity**: Combinations (e.g., SSO + full name) elevate to highest tier.
- **Privacy safety**: Must ensure GDPR/CCPA actions don’t impact employee records sharing identifiers with consumers.
- **Scale & cost**: Efficient scanning of tens of thousands of tables; cost-aware operation.
- **Legal/AI limits**: Must operate with AI disabled until legal approvals; later enable with controls.

## Requirements

### Detection, classification, and confidence
- **Confidence thresholds**:
  - High confidence (e.g., ~98%): auto-tag/apply.
  - Mid confidence (e.g., ~60%): require manual review.
  - Below threshold: ignore until rules improve.
- **Multi-signal detection**: Column names, sample data patterns, comments, tags, custom rules; combine sources with rationales.
- **Domain-aware classification**: Distinguish consumer vs team member vs vendor; include geographic/system context.

### Domain/ontology and policy semantics
- **Domain inference**: From database/schema/table naming, source system tags, or explicit rules to assign domain and govern policy mapping.
- **Semantic roll-up**: Ability to categorize assets (e.g., prospect list → marketing domain → consumer PII expectations).

### Composite sensitivity and tiering
- **Tier elevation**: Detect and elevate risk when sensitive elements co-occur (e.g., SSO + full name → Tier 4).
- **Tier-specific actions**: Stricter masking/tokenization and approvals for Tier 4; differentiated from Tier 3/2.

### Workflow and governance
- **Staging-first**: Write all findings into a recommendations table; no direct auto-apply outside high-confidence threshold.
- **Bulk review**: Approve/reject/correct in batches with filters (domain/type/confidence); capture reviewer notes.
- **Learning loop**: Persist approvals/rejections to refine rules (positive/negative patterns).
- **Two-person control for Tier 4**: Optional dual approval before application.

### Masking, tagging, and access control
- **Tag → Masking → Access chain**: Use tags to drive dynamic masking and dynamic access consistently.
- **Policy variants by context**: Masking policy determined by sensitive_type + domain + tier; role sets differ by domain (e.g., ops can see team-member info but not consumer PII).
- **PCI/HIPAA handling**: Tokenization or external functions for PCI; healthcare-specific protections as needed.

### Privacy and compliance safeguards
- **Boundary enforcement**: Ensure consumer privacy requests cannot delete or obfuscate HR records (safe scoping by domain).
- **Impact preview**: Pre-execution checks highlighting overlaps (e.g., email present in HR) before any action.

### Scale, performance, and cost
- **Estate-wide efficiency**: Batch runs, concurrency controls, smart sampling, resumable scans.
- **Minimal viable toggles**: Ability to run lightweight, name/tag-only passes at scale; integrate Snowflake native auto-classification for bulk.
- **Scheduling and drift detection**: Detect new/changed assets; periodic re-scans.

### Observability, logging, and auditability
- **Structured logs**: Queryable logs for detections, rationales, reviewer decisions, and policy applications with timestamps and actors.
- **Cost and usage monitoring**: Track warehouse/AI costs, rate-limit AI when enabled, and alert on thresholds.

### Legal/AI constraints
- **AI-off mode**: Full rules-based operation with AI disabled; prominent control in settings.
- **Guardrails when AI-on**: Rate limiting, cost caps, and clear audit of AI usage.

## Success criteria
- Significant reduction in false positives/negatives with explainable rationales.
- Safe auto-application only for high-confidence results; no unintended impact on non-target domains.
- Efficient scanning at UDX scale with predictable cost.
- Clear audit trail and repeatable governance workflow.
- Ability to operate fully without AI; seamless upgrade to AI-assisted when permitted.

## Open questions for alignment
- What are the exact confidence thresholds for auto-apply vs review by domain/tier?
- Canonical mapping of databases/schemas/systems to domains and geographies?
- Tiering rules: formal definitions and composite triggers (e.g., SSO + name)?
- Required role sets per domain for unmasked access?
- Preferred tokenization approach for PCI (native vs external function)?
- Review SLAs, approver roles, and dual-control requirements for Tier 4?


