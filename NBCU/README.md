# NBCUniversal - Snowflake Intelligence Semantic Models

## Overview

This collection of semantic model YAML files enables **Snowflake Cortex Analyst** to provide natural language analytics for NBCUniversal, supporting comprehensive business intelligence across all aspects of competitive media and entertainment operations.

## Created Models

### 1. **Competitive Analytics** (`nbcu_competitive_analytics.yaml`)
**Focus**: Advertising revenue tracking, competitor performance monitoring, and market share analysis

**Key Tables**:
- `competitor_profiles` - Media company profiles, market segments, and corporate information
- `advertising_revenue` - Quarterly advertising revenue data across platforms and demographics
- `market_intelligence` - Content investment, subscriber metrics, and pricing intelligence
- `performance_metrics` - Viewership data, engagement rates, and brand sentiment tracking

**Sample Questions**:
- "How did Disney pace in Q1 for advertising revenue and market share?"
- "Did NBCU grow market share against TelevisaUnivision in 2023?"
- "What's the revenue breakdown across competitors for the last 5 quarters?"
- "How are streaming platforms performing against traditional broadcasters?"
- "Which competitors are getting the best ROI on content investment?"



### Key Relationships
- **Competitive Intelligence**: `competitor_profiles` → `advertising_revenue` → `market_intelligence` → `performance_metrics`
- **Cross-platform Analysis**: All tables linked by `competitor_id` and time dimensions for comprehensive competitive tracking
- **Multi-dimensional Analytics**: Platform performance, content investment, and audience engagement metrics interconnected for holistic market analysis

## Business Context

### Key Business Metrics
- **Advertising Revenue per Million (ARPM)**
- **Market Share Percentage**
- **Quarter-over-Quarter Growth**
- **Year-over-Year Growth**
- **Content Investment ROI**
- **Subscriber Acquisition Cost**
- **Cost Per Mille (CPM)**
- **Brand Sentiment Score**
- **Viewership Engagement Rate**

### Competitor Segments
- **Traditional Broadcasters** - NBC, CBS, ABC, Fox networks
- **Cable Networks** - CNN, ESPN, Discovery, A+E Networks
- **Streaming Platforms** - Netflix, Disney+, Amazon Prime Video, Hulu
- **Digital Platforms** - YouTube TV, social media advertising
- **Hispanic Media** - TelevisaUnivision, Spanish-language content

### Platform Categories
- **Broadcast TV** - Prime time programming, news, sports
- **Cable TV** - Specialized content, niche audiences
- **Streaming** - On-demand content, original series
- **Connected TV** - Smart TV advertising, cord-cutting audience
- **Digital Display** - Online banner ads, programmatic advertising



## Analytical Capabilities

### Competitive Intelligence
- Market share analysis and competitive positioning
- Advertising revenue trend identification
- Platform performance comparison
- Content investment effectiveness
- Subscriber growth and retention analysis

### Revenue Optimization
- Cross-platform advertising strategy analysis
- Pricing premium assessment
- Seasonal revenue pattern identification
- Demographic targeting effectiveness
- ROI calculation for content investments

### Strategic Intelligence
- Content investment effectiveness analysis
- Platform performance optimization strategies
- Competitive positioning and market opportunity identification
- Audience engagement and retention analytics
- Advertising pricing and yield management

## Implementation Details

### Data Privacy & Security
- Competitor data sourced from public financial reports and industry analysis
- Proprietary financial data requires appropriate role-based access
- Audit trails maintained for all data access
- Compliance with media industry regulations and advertising standards
- Third-party data vendor agreements maintained for market intelligence sources

### Performance Optimization
- Clustered tables for large datasets (600+ records per table)
- Materialized views for complex cross-platform calculations
- Optimized join paths between competitor and performance tables
- Regular statistics updates for quarterly reporting cycles
- TIMESTAMP_NTZ for consistent timezone handling

## Usage Examples

### Business Executives
"What's our competitive position in streaming advertising revenue compared to Disney and Netflix?"

### Strategy Teams
"Which competitors are investing most heavily in content and what's their ROI?"

### Marketing Teams
"How do our advertising rates compare to competitors across different demographics?"

### Analytics Teams
"How do seasonal advertising trends affect our competitive positioning across different platforms?"

### Finance Teams
"What's our market share trend by platform type over the last 12 months?"

## Agent Configuration

### Sample Agent Questions by Role

**Executive Dashboard:**
- "What are our key competitive performance indicators this quarter?"
- "How are we performing against Disney and Warner Bros Discovery?"
- "Which business areas need immediate strategic attention?"

**Competitive Intelligence:**
- "What's the advertising revenue growth rate of our top 5 competitors?"
- "Which streaming platforms are gaining market share fastest?"
- "How effective are competitor content investment strategies?"

**Revenue Analysis:**
- "What are our highest revenue-generating platform types?"
- "Which advertising formats provide the best CPM rates?"
- "How do seasonal trends affect our competitive positioning?"

**Performance Analytics:**
- "What's our advertising performance compared to industry benchmarks?"
- "Which content categories drive the highest advertising premiums?"
- "Where are our market share growth opportunities by platform?"

**Strategic Planning:**
- "What are the emerging trends in streaming vs traditional TV advertising?"
- "Which competitor strategies should we consider adopting?"
- "What's our competitive advantage in premium content pricing?"

## Data Sources & Methodology

### Competitive Data Sources
- **Nielsen** - TV viewership and advertising measurement
- **ComScore** - Digital audience analytics
- **Kantar** - Media intelligence and market research
- **MoffettNathanson** - Media industry financial analysis
- **GroupM** - Global media investment insights
- **Magna Global** - Advertising market forecasts

### Internal Data Sources
- **Financial Reporting Systems** - Revenue tracking, pricing optimization, cost management
- **Audience Measurement Platforms** - Viewership analytics, engagement metrics
- **Content Management Systems** - Investment tracking, performance analytics
- **Advertising Operations** - Campaign performance, inventory management

### Data Quality Assurance
- **Edge Case Testing** - NULL values, extreme growth scenarios, zero revenue cases
- **Seasonal Validation** - Q4 holiday boost, Q1 post-holiday patterns
- **Relationship Integrity** - Foreign key validation across all tables
- **Realistic Distributions** - Industry-appropriate revenue scales and growth rates

## Troubleshooting

### Common Issues
1. **Slow query responses** - Check warehouse size for complex competitive analysis queries
2. **Unexpected growth rates** - Verify data freshness and handle NULL values properly
3. **Missing competitor data** - Confirm quarterly data pipeline execution and source availability
4. **Time dimension issues** - Ensure proper quarter-end date calculations

### Data Validation Queries
- **Seasonal Pattern Check**: Validate Q4 > Q2 > Q3 > Q1 revenue patterns
- **Growth Rate Bounds**: Ensure YoY growth within -35% to +85% realistic range
- **Market Share Logic**: Verify total market share doesn't exceed 100%
- **Foreign Key Integrity**: Confirm all competitor_id references are valid

### Support Resources
- Internal documentation: NBCUniversal Business Intelligence Portal
- Snowflake support: NBCU Data Platform Team
- Model maintenance: Competitive Intelligence & Analytics Team
- Data quality issues: Data Engineering Team

## Version History

### v1.0 (Current)
- ✅ Initial competitive analytics model with 4 core tables
- ✅ 600+ synthetic records with realistic business scenarios
- ✅ 5 verified business queries for executive reporting
- ✅ Comprehensive data type validation and edge case testing
- ✅ Time dimensions for quarterly analysis
- ✅ Enhanced synonyms for natural language processing

### Planned Enhancements (v1.1)
- 🔄 International market expansion data
- 🔄 Real-time advertising rate tracking
- 🔄 Advanced content investment ROI analytics
- 🔄 Programmatic advertising performance metrics
- 🔄 Cross-platform audience measurement integration

---

*Last updated: December 2024*
*Maintained by: NBCUniversal Competitive Intelligence Team*
*Version: 1.0*
*Contact: analytics-team@nbcuniversal.com*