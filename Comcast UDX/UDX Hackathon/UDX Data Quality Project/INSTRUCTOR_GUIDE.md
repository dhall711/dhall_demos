# UDX AI-Powered Data Quality Hackathon
## Instructor Guide

---

**Empowering the Next Generation of AI-Powered Data Quality Professionals**

This instructor guide provides comprehensive support for delivering the UDX AI-Powered Data Quality Hackathon curriculum, featuring cutting-edge technologies including **Snowflake Agents**, **Intelligence**, **Semantic Models**, and **Multimodal AI**.

---

## 📋 **Pre-Session Preparation Checklist**

### **Technical Setup (Complete 1 week before)**
- [ ] **Snowflake Environment Setup**
  - Enterprise account with Cortex AI enabled
  - Adequate compute credits allocated (recommend 500+ credits)
  - User accounts created for all participants
  - Sample UDX theme park data loaded and verified
  
- [ ] **Instructor Account Preparation**
  - Admin access to monitor participant progress
  - All lab exercises tested and validated
  - Screenshot examples captured from actual Snowsight interface
  - Backup solutions prepared for common issues

### **Content Preparation (Complete 3 days before)**
- [ ] **Lab Materials Review**
  - All SQL exercises tested with current data
  - Function permissions verified
  - AI model access confirmed
  - Expected results documented
  
- [ ] **Presentation Materials**
  - Opening presentation ready (architecture overview)
  - Demo scenarios prepared and tested
  - Closing presentation ready (business value summary)

### **Logistics Setup (Complete 1 day before)**
- [ ] **Participant Communication**
  - Login credentials distributed
  - Student guide shared
  - Prerequisites communicated
  - Slack/Teams channel setup for support

---

## 🎯 **Learning Objectives & Assessment Criteria**

### **Primary Learning Outcomes**
By the end of this hackathon, participants should demonstrate:

| **Learning Outcome** | **Assessment Method** | **Success Criteria** |
|---------------------|----------------------|---------------------|
| **Foundation Data Quality** | Lab completion + Quiz | 90% accuracy on quality dimensions |
| **AI Technology Integration** | Hands-on demonstration | Working Cortex AI functions |
| **Semantic Model Creation** | Practical implementation | Business-friendly semantic views |
| **Conversational Analytics** | Interactive demo | Natural language queries working |
| **Autonomous Agents** | Live deployment | Functioning agent workflows |
| **Business Value Articulation** | Final presentation | Clear ROI demonstration |

### **Skill Development Progression**
```
Beginner → Intermediate → Advanced → Expert
   ↓            ↓           ↓         ↓
 Labs 1-3    Labs 4-6    Labs 7-8   Labs 9-10
```

---

## ⏰ **Detailed Timing Guide & Teaching Notes**

### **Phase 1: Foundation (2 hours)**

#### **Lab 01: Setup & Data Foundation (30 minutes)**
**🎯 Instructor Focus:** Ensure all participants can access Snowflake successfully

**Key Teaching Points:**
- Emphasize importance of data quality foundation
- Explain UDX theme park business context
- Set expectations for AI capabilities to come

**⚠️ Common Issues:**
- **Login problems**: Have backup accounts ready
- **Warehouse not starting**: Check credit allocation
- **Database/schema confusion**: Create visual diagram

**📚 Extension Activity for Fast Finishers:**
```sql
-- Explore data relationships
SELECT p.park_name, COUNT(g.guest_id) as total_guests
FROM PARKS p
LEFT JOIN GUESTS g ON p.park_id = g.park_id
GROUP BY p.park_name
ORDER BY total_guests DESC;
```

#### **Lab 02: Data Quality Fundamentals (45 minutes)**
**🎯 Instructor Focus:** Build solid understanding of quality dimensions

**Key Teaching Points:**
1. **Six Dimensions of Data Quality** (15 minutes)
   - Use real examples from theme park operations
   - Connect each dimension to business impact
   - Explain why automation is necessary

2. **Validation Rules** (20 minutes)
   - Emphasize reusability and scalability
   - Show how functions reduce code duplication
   - Discuss business rule importance

3. **Quality Metrics Framework** (10 minutes)
   - Explain the importance of consistent measurement
   - Show how metrics drive decision-making
   - Connect to upcoming AI capabilities

**🔍 What to Look For:**
- Students successfully creating functions
- Understanding of pass/fail criteria
- Recognition of business impact

**💡 Teaching Tips:**
- Walk around during exercises to check progress
- Use participant examples to explain concepts
- Encourage questions about business context

**🎪 Real-World Connection:**
*"Imagine you're a park manager and 20% of guest emails are missing. How does this impact your marketing campaigns during peak season?"*

#### **Lab 03: Advanced Data Validation (45 minutes)**
**🎯 Instructor Focus:** Bridge traditional analysis with AI preparation

**Key Teaching Points:**
1. **Statistical Methods** (20 minutes)
   - Explain Z-scores in business terms
   - Show IQR method practical applications
   - Connect outliers to operational issues

2. **Cross-Table Validation** (15 minutes)
   - Emphasize data relationships
   - Show business rule violations
   - Discuss impact propagation

3. **Pattern Recognition** (10 minutes)
   - Prepare foundation for AI pattern detection
   - Show manual vs. automated approaches
   - Set stage for intelligent analysis

**⚠️ Watch for Student Confusion:**
- Statistical concepts may be challenging
- Help translate math into business value
- Use visual examples when possible

---

### **Phase 2: AI Intelligence (2 hours)**

#### **Lab 04: Basic Cortex AI Integration (30 minutes)**
**🎯 Instructor Focus:** First AI "wow moment" - show immediate value

**Key Teaching Points:**
1. **AI Function Introduction** (10 minutes)
   - Start with simple COMPLETE() examples
   - Show natural language generation
   - Emphasize practical applications

2. **Model Selection Strategy** (10 minutes)
   - Explain when to use different models
   - Show cost vs. capability trade-offs
   - Demonstrate performance differences

3. **Business Context Integration** (10 minutes)
   - Connect AI outputs to business decisions
   - Show how AI explains data quality issues
   - Prepare for semantic integration

**📸 Key Screenshots to Capture:**
- Cortex AI function execution
- Different model outputs comparison
- Business-friendly AI explanations

**🎯 Success Indicator:**
Students should be able to generate natural language explanations of data quality issues using AI.

#### **Lab 05: Semantic Models & Views (45 minutes)**
**🎯 Instructor Focus:** Bridge technical data with business understanding

**Key Teaching Points:**
1. **Business Abstraction Concept** (15 minutes)
   - Explain why technical schemas confuse business users
   - Show before/after examples
   - Emphasize AI's need for context

2. **Semantic View Creation** (20 minutes)
   - Guide through dimension definitions
   - Show metric calculations
   - Emphasize sample values and descriptions

3. **AI-Ready Structures** (10 minutes)
   - Connect to upcoming Intelligence features
   - Show how context improves AI responses
   - Prepare for conversational analytics

**💡 Pro Teaching Tip:**
Have students define semantic views using business language first, then translate to SQL. This reinforces the abstraction concept.

**🔍 Quality Check:**
Can students explain their semantic view to a non-technical business user?

#### **Lab 06: Snowflake Intelligence (45 minutes)**
**🎯 Instructor Focus:** The "magic moment" - natural language data conversations

**Key Teaching Points:**
1. **Conversational Analytics Revolution** (15 minutes)
   - Demo natural language queries
   - Show business user empowerment
   - Explain governance and security

2. **Role-Based Analytics** (20 minutes)
   - Show different user experiences
   - Demonstrate personalization
   - Explain context awareness

3. **Self-Service Enablement** (10 minutes)
   - Show how business users can explore independently
   - Discuss impact on data team efficiency
   - Connect to autonomous capabilities coming next

**🎪 Demo Scenarios:**
- Executive asking about safety risks
- Park manager inquiring about operational efficiency
- Data analyst exploring quality trends

**✅ Success Criteria:**
Students can demonstrate natural language queries that produce business-relevant insights.

---

### **Phase 3: Autonomous Operations (2 hours)**

#### **Lab 07: AI Agents Basics (45 minutes)**
**🎯 Instructor Focus:** Introduction to autonomous AI systems

**Key Teaching Points:**
1. **Autonomous AI Concept** (15 minutes)
   - Explain agent vs. traditional automation
   - Show decision-making capabilities
   - Discuss human-AI collaboration

2. **Agent Creation and Configuration** (20 minutes)
   - Guide through first agent creation
   - Explain instruction design principles
   - Show tool integration

3. **Monitoring and Management** (10 minutes)
   - Demonstrate agent execution tracking
   - Show performance metrics
   - Explain governance controls

**⚠️ Common Student Concerns:**
- "Will AI replace human judgment?"
  - **Answer**: Emphasize augmentation, not replacement
  - Show escalation and approval mechanisms
  - Discuss human oversight importance

**🎯 Hands-On Goal:**
Each student should have a working monitoring agent by end of lab.

#### **Lab 08: Advanced Agent Orchestration (75 minutes)**
**🎯 Instructor Focus:** Enterprise-scale autonomous systems

**Key Teaching Points:**
1. **Multi-Agent Coordination** (25 minutes)
   - Show agent specialization benefits
   - Demonstrate workflow orchestration
   - Explain resource allocation

2. **Learning and Adaptation** (25 minutes)
   - Show how agents improve over time
   - Demonstrate pattern recognition
   - Explain feedback loops

3. **Enterprise Integration** (25 minutes)
   - Show cross-park coordination
   - Demonstrate scalability
   - Discuss governance frameworks

**🏆 Advanced Challenge:**
Have teams design agent networks for different business scenarios.

---

### **Phase 4: Advanced AI (2 hours)**

#### **Lab 09: Multimodal AI with Cortex AISQL (75 minutes)**
**🎯 Instructor Focus:** Showcase comprehensive AI intelligence

**Key Teaching Points:**
1. **Multimodal Concept** (25 minutes)
   - Show limitations of single-modal analysis
   - Demonstrate cross-modal correlation
   - Explain comprehensive intelligence

2. **Image and Document Analysis** (25 minutes)
   - Show ride inspection photo analysis
   - Demonstrate document intelligence
   - Connect to data quality validation

3. **Text and Sentiment Integration** (25 minutes)
   - Show guest feedback analysis
   - Demonstrate social media integration
   - Connect to operational decisions

**🎪 Wow Factor Demos:**
- Photo analysis revealing data inconsistencies
- Document intelligence finding quality issues
- Social sentiment predicting operational problems

#### **Lab 10: Complete Autonomous Assistant (45 minutes)**
**🎯 Instructor Focus:** Integration and business value demonstration

**Key Teaching Points:**
1. **System Integration** (15 minutes)
   - Show how all components work together
   - Demonstrate end-to-end workflows
   - Explain enterprise architecture

2. **Business Value Realization** (15 minutes)
   - Calculate ROI with real numbers
   - Show efficiency improvements
   - Demonstrate competitive advantages

3. **Future Roadmap** (15 minutes)
   - Discuss next-generation capabilities
   - Show industry trends
   - Inspire continued learning

---

## 🎯 **Assessment & Evaluation Guidelines**

### **Continuous Assessment Throughout Labs**

**Lab 02-03: Foundation Mastery**
- ✅ Can create quality validation rules
- ✅ Understands business impact of quality issues
- ✅ Successfully implements monitoring frameworks

**Lab 04-06: AI Integration Skills**
- ✅ Demonstrates Cortex AI function usage
- ✅ Creates meaningful semantic models
- ✅ Successfully enables conversational analytics

**Lab 07-08: Autonomous Systems**
- ✅ Deploys working AI agents
- ✅ Implements agent coordination
- ✅ Shows understanding of enterprise scale

**Lab 09-10: Advanced Integration**
- ✅ Demonstrates multimodal capabilities
- ✅ Integrates all components successfully
- ✅ Articulates clear business value

### **Final Presentation Rubric**

| **Criteria** | **Excellent (4)** | **Good (3)** | **Satisfactory (2)** | **Needs Improvement (1)** |
|--------------|-------------------|--------------|----------------------|---------------------------|
| **Technical Implementation** | All components working seamlessly | Most components functional | Basic functionality achieved | Major technical issues |
| **AI Innovation** | Creative and advanced AI usage | Good AI integration | Basic AI implementation | Minimal AI utilization |
| **Business Value** | Clear ROI with quantified benefits | Good business case | Some business value shown | Unclear value proposition |
| **Presentation Quality** | Engaging and professional | Well organized | Adequate communication | Poor presentation skills |

---

## 🔧 **Technical Troubleshooting Guide**

### **Environment Issues**

**Problem**: Students can't access Snowflake
**Quick Fix**: 
1. Check account status and user permissions
2. Verify warehouse is running
3. Confirm correct URL and credentials
4. Use backup accounts if needed

**Problem**: Cortex AI functions not available
**Quick Fix**:
1. Verify account has Cortex AI enabled
2. Check region availability
3. Confirm sufficient credits
4. Try different model if specific model unavailable

**Problem**: Agent creation fails
**Quick Fix**:
1. Check agent creation permissions
2. Verify semantic view exists and is accessible
3. Simplify agent instructions for testing
4. Use basic tools first, add complexity later

### **Student Progress Issues**

**Slow Students:**
- Pair with faster partners
- Focus on core concepts, skip advanced features
- Provide pre-written code snippets
- Offer one-on-one assistance

**Fast Students:**
- Provide extension challenges
- Have them help others
- Give additional business scenarios
- Encourage creative AI applications

### **Common SQL Errors**

**Function Creation Errors:**
```sql
-- Common fix: Check schema and permissions
GRANT CREATE FUNCTION ON SCHEMA PUBLIC TO ROLE STUDENT_ROLE;
```

**Data Access Issues:**
```sql
-- Verify data exists
SELECT COUNT(*) FROM GUESTS;
SELECT * FROM GUESTS LIMIT 5;
```

**Agent Permission Errors:**
```sql
-- Grant necessary permissions
GRANT USAGE ON SEMANTIC VIEW udx_data_quality_semantic_view TO ROLE AGENT_ROLE;
```

---

## 💡 **Advanced Teaching Strategies**

### **Interactive Learning Techniques**

**1. Peer Learning Sessions**
- Pair students with different skill levels
- Have advanced students mentor beginners
- Create collaborative problem-solving opportunities

**2. Business Scenario Role-Playing**
- Assign roles: Park Manager, Data Engineer, Executive
- Have students defend decisions from their role perspective
- Show how different stakeholders benefit from AI

**3. Live Problem-Solving**
- Introduce real-time "data quality emergencies"
- Have students respond using their AI systems
- Demonstrate autonomous response capabilities

### **Gamification Elements**

**Lab Completion Badges:**
- 🏗️ **Foundation Master**: Complete Labs 1-3
- 🧠 **AI Integrator**: Complete Labs 4-6  
- 🤖 **Agent Commander**: Complete Labs 7-8
- 🌟 **AI Innovator**: Complete Labs 9-10

**Team Challenges:**
- Best business value demonstration
- Most creative AI application
- Fastest lab completion
- Best presentation

---

## 📊 **Success Metrics & KPIs**

### **Student Engagement Metrics**
- Lab completion rate: Target >95%
- Time to complete each lab: Track against estimates
- Question frequency: Indicator of engagement level
- Peer helping instances: Shows collaborative learning

### **Learning Effectiveness**
- Pre/post assessment scores
- Hands-on demonstration success rate
- Business value articulation quality
- Technical implementation accuracy

### **Business Impact Understanding**
- ROI calculation accuracy
- Real-world application examples
- Stakeholder value articulation
- Future implementation planning

---

## 🎉 **Session Wrap-Up & Follow-Up**

### **Closing Session (30 minutes)**

**1. Key Takeaways Review (10 minutes)**
- Summarize revolutionary capabilities learned
- Highlight transformation from traditional to AI-powered
- Emphasize competitive advantages gained

**2. Implementation Planning (10 minutes)**
- Discuss real-world deployment considerations
- Share best practices and lessons learned
- Provide roadmap for continued learning

**3. Network Building (10 minutes)**
- Facilitate participant connections
- Share contact information
- Establish ongoing collaboration opportunities

### **Post-Session Follow-Up**

**Within 24 Hours:**
- [ ] Send session recording links
- [ ] Distribute additional resources
- [ ] Share participant contact list
- [ ] Send feedback survey

**Within 1 Week:**
- [ ] Compile and share best solutions
- [ ] Create participant showcase
- [ ] Schedule follow-up Q&A session
- [ ] Share industry updates and new features

**Ongoing Support:**
- [ ] Monthly community calls
- [ ] Slack/Teams channel maintenance
- [ ] Resource library updates
- [ ] Advanced workshop opportunities

---

## 📚 **Additional Instructor Resources**

### **Technical Documentation**
- [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Semantic Views Reference](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [Agent Framework Guide](https://docs.snowflake.com/en/user-guide/ai-agents)

### **Business Context Materials**
- Theme park industry overview
- Data quality ROI calculators
- Case study examples
- Industry benchmark data

### **Continued Learning Paths**
- Advanced AI workshops
- Certification program information
- Conference and event recommendations
- Community resource links

---

**🎓 Ready to Inspire the Next Generation of AI-Powered Data Quality Leaders!**

This instructor guide provides everything needed to deliver an exceptional learning experience that transforms participants into AI-powered data quality innovators. Focus on hands-on learning, real business value, and the revolutionary potential of autonomous AI systems.

**Remember**: Your enthusiasm for the technology will inspire students to push boundaries and imagine new possibilities in their own organizations.

---

*Last Updated: November 2024*  
*Version: 2.0 - Enhanced AI Curriculum Edition* 