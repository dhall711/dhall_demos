"""
Snowflake Multi-Project Usage Monitor
A standalone application for tracking usage and consumption across multiple Snowflake projects.

Enhanced with:
- Workload-level cost consolidation using Query Attribution
- Cortex AI feature tracking (LLM, embeddings, vector costs)  
- Enhanced metrics with rows/GB per credit
- Period comparison analysis
- Advanced visualization and formatting
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import time

# Import the enhanced Cortex monitoring
try:
    from core.cortex_monitor import CortexAIMonitor, CortexUsageMetrics, WorkloadCostBreakdown
    CORTEX_MONITORING_AVAILABLE = True
except ImportError:
    CORTEX_MONITORING_AVAILABLE = False

# Set page configuration
st.set_page_config(
    page_title="🏢 Snowflake Multi-Project Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class ProjectConfig:
    """Configuration for a monitored project"""
    project_name: str
    project_type: str  # 'sensitive_data', 'schema_mapper', 'other'
    warehouse_pattern: str  # Pattern to identify project warehouses
    database_pattern: str   # Pattern to identify project databases
    user_pattern: str      # Pattern to identify project users
    description: str
    cost_center: str
    priority: str  # 'high', 'medium', 'low'

@dataclass
class ProjectMetrics:
    """Enhanced metrics for a specific project with efficiency indicators"""
    project_name: str
    warehouse_credits: float
    query_count: int
    avg_execution_time: float
    error_count: int
    unique_users: int
    data_scanned_gb: float
    ai_requests: int
    estimated_cost: float
    time_period: str
    
    # Enhanced efficiency metrics
    rows_per_credit: float = 0.0
    gb_per_credit: float = 0.0
    cost_per_query: float = 0.0
    rows_processed: int = 0
    
    # Period comparison
    prev_period_cost: Optional[float] = None
    cost_change_percent: Optional[float] = None

@dataclass
class CrossProjectInsight:
    """Insights comparing projects"""
    insight_type: str
    title: str
    description: str
    projects_involved: List[str]
    metrics: Dict[str, Any]
    recommendation: str
    priority: str

class SnowflakeConnection:
    """Snowflake connection manager"""
    
    def __init__(self):
        self._conn = None
        self._connection_info = None
    
    @property
    def connection(self):
        """Get or create Snowflake connection"""
        if self._conn is None:
            self._conn = self._establish_connection()
        return self._conn
    
    def _establish_connection(self):
        """Establish Snowflake connection"""
        try:
            conn = st.connection('snowflake')
            # Test connection
            test_result = conn.query("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
            
            if not test_result.empty:
                self._connection_info = {
                    'user': test_result.iloc[0]['CURRENT_USER()'],
                    'role': test_result.iloc[0]['CURRENT_ROLE()'],
                    'warehouse': test_result.iloc[0]['CURRENT_WAREHOUSE()']
                }
                return conn
            else:
                raise Exception("Connection test failed")
                
        except Exception as e:
            st.error(f"Failed to connect to Snowflake: {str(e)}")
            return None
    
    def execute_query(self, query: str, operation_name: str = "query") -> Optional[pd.DataFrame]:
        """Execute query with error handling"""
        try:
            if not self.connection:
                st.error("No database connection available")
                return None
            
            with st.spinner(f"Executing {operation_name}..."):
                df = self.connection.query(query)
                return df
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return None

class MultiProjectMonitor:
    """Enhanced monitoring engine with Cortex AI integration"""
    
    def __init__(self, db_connection: SnowflakeConnection):
        self.db = db_connection
        self.projects = self._load_project_configurations()
        self.cost_models = {
            'warehouse_credit_cost': 3.0,
            'storage_cost_per_gb': 0.05,
            'ai_request_cost': 0.01
        }
        
        # Initialize Cortex AI monitor if available
        if CORTEX_MONITORING_AVAILABLE and self.db.connection:
            self.cortex_monitor = CortexAIMonitor(db_connection)
        else:
            self.cortex_monitor = None
    
    def _load_project_configurations(self) -> Dict[str, ProjectConfig]:
        """Load project configurations"""
        default_projects = {
            'sensitive_data_project': ProjectConfig(
                project_name='sensitive_data_project',
                project_type='sensitive_data',
                warehouse_pattern='%SENSITIVE%|%DDM%|%DISCOVERY%',
                database_pattern='%SENSITIVE%|%PII%|%DISCOVERY%',
                user_pattern='%DATA_DISCOVERY%|%PRIVACY%',
                description='Sensitive data discovery and dynamic data masking operations',
                cost_center='Data Governance',
                priority='high'
            ),
            'schema_mapper': ProjectConfig(
                project_name='schema_mapper',
                project_type='schema_mapper',
                warehouse_pattern='%MAPPER%|%TRANSFORM%|%ETL%',
                database_pattern='%MAPPER%|%TRANSFORM%|%STAGING%',
                user_pattern='%MAPPER%|%ETL%|%TRANSFORM%',
                description='Schema mapping and data transformation operations',
                cost_center='Data Engineering',
                priority='high'
            )
        }
        
        # Load from session state if available
        if 'project_configs' in st.session_state:
            return st.session_state.project_configs
        
        # Store default configurations
        st.session_state.project_configs = default_projects
        return default_projects
    
    def get_enhanced_project_metrics(self, project_name: str, hours: int = 24) -> Optional[ProjectMetrics]:
        """Get enhanced metrics using Query Attribution for accurate cost tracking"""
        if project_name not in self.projects:
            return None
        
        project_config = self.projects[project_name]
        
        try:
            # Enhanced query using Query Attribution for accurate cost calculation
            query = f"""
            WITH project_queries AS (
                SELECT 
                    qa.warehouse_name,
                    qa.database_name,
                    qa.user_name,
                    qa.execution_time_ms,
                    qa.credits_attributed_to_query as credits_used,
                    qa.bytes_scanned,
                    qa.rows_produced,
                    qa.error_code,
                    qa.query_text,
                    qa.start_time
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION qa
                WHERE qa.start_time >= DATEADD(hour, -{hours}, CURRENT_TIMESTAMP())
                AND (
                    qa.warehouse_name ILIKE ANY ('{project_config.warehouse_pattern}') OR
                    qa.database_name ILIKE ANY ('{project_config.database_pattern}') OR
                    qa.user_name ILIKE ANY ('{project_config.user_pattern}')
                )
            ),
            project_stats AS (
                SELECT 
                    COUNT(*) as total_queries,
                    SUM(credits_used) as total_credits,
                    AVG(execution_time_ms) as avg_execution_time,
                    COUNT(CASE WHEN error_code IS NOT NULL THEN 1 END) as error_count,
                    COUNT(DISTINCT user_name) as unique_users,
                    SUM(bytes_scanned) / POWER(1024, 3) as data_scanned_gb,
                    SUM(rows_produced) as rows_processed,
                    COUNT(CASE WHEN UPPER(query_text) LIKE '%CORTEX%' THEN 1 END) as ai_requests
                FROM project_queries
            ),
            previous_period AS (
                SELECT 
                    SUM(qa.credits_attributed_to_query) * {self.cost_models['warehouse_credit_cost']} as prev_cost
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION qa
                WHERE qa.start_time >= DATEADD(hour, -{hours * 2}, CURRENT_TIMESTAMP())
                AND qa.start_time < DATEADD(hour, -{hours}, CURRENT_TIMESTAMP())
                AND (
                    qa.warehouse_name ILIKE ANY ('{project_config.warehouse_pattern}') OR
                    qa.database_name ILIKE ANY ('{project_config.database_pattern}') OR
                    qa.user_name ILIKE ANY ('{project_config.user_pattern}')
                )
            )
            SELECT 
                ps.total_queries,
                COALESCE(ps.total_credits, 0) as total_credits,
                COALESCE(ps.avg_execution_time, 0) as avg_execution_time,
                COALESCE(ps.error_count, 0) as error_count,
                COALESCE(ps.unique_users, 0) as unique_users,
                COALESCE(ps.data_scanned_gb, 0) as data_scanned_gb,
                COALESCE(ps.ai_requests, 0) as ai_requests,
                COALESCE(ps.rows_processed, 0) as rows_processed,
                COALESCE(pp.prev_cost, 0) as prev_period_cost
            FROM project_stats ps
            CROSS JOIN previous_period pp
            """
            
            df = self.db.execute_query(query, f"fetching enhanced metrics for {project_name}")
            
            if df is not None and not df.empty:
                row = df.iloc[0]
                
                # Calculate enhanced metrics
                total_credits = float(row['TOTAL_CREDITS'])
                rows_processed = int(row['ROWS_PROCESSED'])
                data_scanned_gb = float(row['DATA_SCANNED_GB'])
                query_count = int(row['TOTAL_QUERIES'])
                
                # Calculate estimated cost
                estimated_cost = (
                    total_credits * self.cost_models['warehouse_credit_cost'] +
                    data_scanned_gb * self.cost_models['storage_cost_per_gb'] +
                    int(row['AI_REQUESTS']) * self.cost_models['ai_request_cost']
                )
                
                # Calculate efficiency metrics
                rows_per_credit = rows_processed / max(total_credits, 0.01)
                gb_per_credit = data_scanned_gb / max(total_credits, 0.01)
                cost_per_query = estimated_cost / max(query_count, 1)
                
                # Calculate period comparison
                prev_cost = float(row['PREV_PERIOD_COST']) if row['PREV_PERIOD_COST'] else None
                cost_change_percent = None
                if prev_cost and prev_cost > 0:
                    cost_change_percent = ((estimated_cost - prev_cost) / prev_cost) * 100
                
                return ProjectMetrics(
                    project_name=project_name,
                    warehouse_credits=total_credits,
                    query_count=query_count,
                    avg_execution_time=float(row['AVG_EXECUTION_TIME']),
                    error_count=int(row['ERROR_COUNT']),
                    unique_users=int(row['UNIQUE_USERS']),
                    data_scanned_gb=data_scanned_gb,
                    ai_requests=int(row['AI_REQUESTS']),
                    estimated_cost=estimated_cost,
                    time_period=f"{hours}h",
                    rows_per_credit=rows_per_credit,
                    gb_per_credit=gb_per_credit,
                    cost_per_query=cost_per_query,
                    rows_processed=rows_processed,
                    prev_period_cost=prev_cost,
                    cost_change_percent=cost_change_percent
                )
        
        except Exception as e:
            st.error(f"Error fetching enhanced metrics for {project_name}: {e}")
        
        return None
    
    def get_all_project_metrics(self, hours: int = 24) -> Dict[str, ProjectMetrics]:
        """Get enhanced metrics for all configured projects"""
        metrics = {}
        for project_name in self.projects.keys():
            project_metrics = self.get_enhanced_project_metrics(project_name, hours)
            if project_metrics:
                metrics[project_name] = project_metrics
        return metrics
    
    def get_project_comparison(self, hours: int = 24) -> List[CrossProjectInsight]:
        """Generate insights comparing projects with enhanced analytics"""
        insights = []
        all_metrics = self.get_all_project_metrics(hours)
        
        if len(all_metrics) < 2:
            return insights
        
        # Enhanced cost efficiency analysis
        efficiency_scores = {}
        for name, metrics in all_metrics.items():
            # Calculate efficiency score based on multiple factors
            cost_efficiency = metrics.cost_per_query
            processing_efficiency = metrics.rows_per_credit
            error_rate = (metrics.error_count / max(metrics.query_count, 1)) * 100
            
            efficiency_score = (processing_efficiency / max(cost_efficiency, 0.01)) * (1 - error_rate / 100)
            efficiency_scores[name] = efficiency_score
        
        # Find best and worst performing projects
        best_project = max(efficiency_scores.keys(), key=lambda k: efficiency_scores[k])
        worst_project = min(efficiency_scores.keys(), key=lambda k: efficiency_scores[k])
        
        if efficiency_scores[best_project] > efficiency_scores[worst_project] * 2:
            insights.append(CrossProjectInsight(
                insight_type='efficiency',
                title='Significant Efficiency Gap Between Projects',
                description=f'{best_project} is {efficiency_scores[best_project]/efficiency_scores[worst_project]:.1f}x more efficient than {worst_project}',
                projects_involved=[best_project, worst_project],
                metrics={
                    'best_efficiency': efficiency_scores[best_project],
                    'worst_efficiency': efficiency_scores[worst_project],
                    'efficiency_gap': efficiency_scores[best_project]/efficiency_scores[worst_project]
                },
                recommendation=f'Review {worst_project} for optimization opportunities based on {best_project} best practices',
                priority='high'
            ))
        
        # Cost trend analysis
        for project_name, metrics in all_metrics.items():
            if metrics.cost_change_percent is not None:
                if metrics.cost_change_percent > 25:
                    insights.append(CrossProjectInsight(
                        insight_type='cost_trend',
                        title='Significant Cost Increase Detected',
                        description=f'{project_name} costs increased by {metrics.cost_change_percent:.1f}% from previous period',
                        projects_involved=[project_name],
                        metrics={'cost_change': metrics.cost_change_percent},
                        recommendation='Investigate recent changes in workload patterns or resource allocation',
                        priority='high'
                    ))
                elif metrics.cost_change_percent < -15:
                    insights.append(CrossProjectInsight(
                        insight_type='cost_trend',
                        title='Positive Cost Optimization Detected',
                        description=f'{project_name} costs decreased by {abs(metrics.cost_change_percent):.1f}% from previous period',
                        projects_involved=[project_name],
                        metrics={'cost_change': metrics.cost_change_percent},
                        recommendation='Document optimization strategies for replication across other projects',
                        priority='low'
                    ))
        
        return insights
    
    def format_large_number(self, number: float, number_type: str = 'count') -> str:
        """Format large numbers with appropriate suffixes"""
        if number_type == 'rows':
            if number >= 1e12:
                return f"{number/1e12:.1f}T"
            elif number >= 1e9:
                return f"{number/1e9:.1f}B"
            elif number >= 1e6:
                return f"{number/1e6:.1f}M"
            elif number >= 1e3:
                return f"{number/1e3:.1f}K"
            else:
                return f"{number:.0f}"
        elif number_type == 'bytes':
            if number >= 1e12:
                return f"{number/1e12:.1f}TB"
            elif number >= 1e9:
                return f"{number/1e9:.1f}GB"
            elif number >= 1e6:
                return f"{number/1e6:.1f}MB"
            else:
                return f"{number:.1f}GB"
        elif number_type == 'currency':
            if number >= 1e6:
                return f"${number/1e6:.1f}M"
            elif number >= 1e3:
                return f"${number/1e3:.1f}K"
            else:
                return f"${number:.2f}"
        else:
            return f"{number:,.0f}"

class MultiProjectDashboard:
    """Enhanced dashboard UI with Cortex AI monitoring"""
    
    def __init__(self, monitor: MultiProjectMonitor):
        self.monitor = monitor
    
    def render_header(self):
        """Render dashboard header"""
        st.title("🏢 Snowflake Multi-Project Usage Monitor")
        st.markdown("*Enhanced cross-project monitoring with Cortex AI workload consolidation*")
        
        # Connection status
        if self.monitor.db.connection:
            conn_info = self.monitor.db._connection_info
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ Connected as {conn_info['user']} with role {conn_info['role']}")
            with col2:
                if self.monitor.cortex_monitor:
                    st.success("🤖 Cortex AI monitoring enabled")
                else:
                    st.warning("⚠️ Cortex AI monitoring unavailable")
        else:
            st.error("❌ Not connected to Snowflake")
            st.stop()
        
        st.markdown("---")
    
    def render_enhanced_project_overview(self):
        """Render enhanced overview with efficiency metrics"""
        st.header("📊 Enhanced Project Overview")
        
        # Time range selector with period comparison
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Resource Utilization & Efficiency Analysis")
        with col2:
            time_options = [
                (1, "1 hour"),
                (6, "6 hours"), 
                (24, "24 hours"),
                (48, "48 hours"),
                (168, "7 days")
            ]
            time_range = st.selectbox(
                "Analysis Period",
                options=[opt[0] for opt in time_options],
                index=2,
                format_func=lambda x: next(opt[1] for opt in time_options if opt[0] == x)
            )
        
        # Get enhanced metrics
        all_metrics = self.monitor.get_all_project_metrics(time_range)
        
        if not all_metrics:
            st.warning("No project data found for the selected period")
            return
        
        # Enhanced summary cards with efficiency metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_cost = sum(m.estimated_cost for m in all_metrics.values())
        total_queries = sum(m.query_count for m in all_metrics.values())
        total_credits = sum(m.warehouse_credits for m in all_metrics.values())
        total_rows = sum(m.rows_processed for m in all_metrics.values())
        avg_efficiency = sum(m.rows_per_credit for m in all_metrics.values()) / len(all_metrics)
        
        with col1:
            st.metric(
                "Total Cost", 
                self.monitor.format_large_number(total_cost, 'currency'),
                f"{len(all_metrics)} projects"
            )
        with col2:
            st.metric(
                "Total Queries", 
                self.monitor.format_large_number(total_queries, 'count'),
                f"{total_credits:.1f} credits"
            )
        with col3:
            st.metric(
                "Rows Processed",
                self.monitor.format_large_number(total_rows, 'rows'),
                "across projects"
            )
        with col4:
            avg_cost_per_query = total_cost / max(total_queries, 1)
            st.metric(
                "Avg Cost/Query",
                f"${avg_cost_per_query:.3f}",
                "efficiency"
            )
        with col5:
            st.metric(
                "Rows/Credit",
                self.monitor.format_large_number(avg_efficiency, 'rows'),
                "avg efficiency"
            )
        
        # Enhanced visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Efficiency scatter plot
            efficiency_data = []
            for name, metrics in all_metrics.items():
                efficiency_data.append({
                    'Project': name,
                    'Cost per Query': metrics.cost_per_query,
                    'Rows per Credit': metrics.rows_per_credit,
                    'Total Cost': metrics.estimated_cost,
                    'Error Rate': (metrics.error_count / max(metrics.query_count, 1)) * 100
                })
            
            if efficiency_data:
                df_efficiency = pd.DataFrame(efficiency_data)
                fig_efficiency = px.scatter(
                    df_efficiency,
                    x='Cost per Query',
                    y='Rows per Credit',
                    size='Total Cost',
                    color='Error Rate',
                    hover_name='Project',
                    title="Project Efficiency Analysis",
                    labels={
                        'Cost per Query': 'Cost per Query ($)',
                        'Rows per Credit': 'Rows per Credit',
                        'Error Rate': 'Error Rate (%)'
                    },
                    color_continuous_scale='RdYlGn_r'
                )
                fig_efficiency.update_layout(height=400)
                st.plotly_chart(fig_efficiency, use_container_width=True)
        
        with col2:
            # Period comparison chart
            comparison_data = []
            for name, metrics in all_metrics.items():
                if metrics.cost_change_percent is not None:
                    comparison_data.append({
                        'Project': name,
                        'Current Cost': metrics.estimated_cost,
                        'Previous Cost': metrics.prev_period_cost or 0,
                        'Change %': metrics.cost_change_percent
                    })
            
            if comparison_data:
                df_comparison = pd.DataFrame(comparison_data)
                fig_comparison = px.bar(
                    df_comparison,
                    x='Project',
                    y=['Current Cost', 'Previous Cost'],
                    title="Current vs Previous Period Cost Comparison",
                    barmode='group',
                    color_discrete_map={
                        'Current Cost': '#2E86AB',
                        'Previous Cost': '#A23B72'
                    }
                )
                
                # Add change percentage annotations
                for i, row in df_comparison.iterrows():
                    fig_comparison.add_annotation(
                        x=i,
                        y=max(row['Current Cost'], row['Previous Cost']) + 10,
                        text=f"{row['Change %']:+.1f}%",
                        showarrow=False,
                        font=dict(color='green' if row['Change %'] < 0 else 'red')
                    )
                
                fig_comparison.update_layout(height=400)
                st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Enhanced detailed metrics table
        st.subheader("Detailed Project Performance Metrics")
        
        detailed_data = []
        for name, metrics in all_metrics.items():
            project_config = self.monitor.projects[name]
            
            # Format change indicator
            change_indicator = ""
            if metrics.cost_change_percent is not None:
                if metrics.cost_change_percent > 0:
                    change_indicator = f"🔺 +{metrics.cost_change_percent:.1f}%"
                else:
                    change_indicator = f"🔻 {metrics.cost_change_percent:.1f}%"
            
            detailed_data.append({
                'Project': name,
                'Type': project_config.project_type,
                'Cost Center': project_config.cost_center,
                'Priority': project_config.priority,
                'Queries': self.monitor.format_large_number(metrics.query_count, 'count'),
                'Rows Processed': self.monitor.format_large_number(metrics.rows_processed, 'rows'),
                'Credits': f"{metrics.warehouse_credits:.2f}",
                'Total Cost': self.monitor.format_large_number(metrics.estimated_cost, 'currency'),
                'Cost/Query': f"${metrics.cost_per_query:.3f}",
                'Rows/Credit': self.monitor.format_large_number(metrics.rows_per_credit, 'rows'),
                'GB/Credit': f"{metrics.gb_per_credit:.2f}",
                'Error Rate': f"{(metrics.error_count/max(metrics.query_count,1)*100):.1f}%",
                'Period Change': change_indicator
            })
        
        if detailed_data:
            df_detailed = pd.DataFrame(detailed_data)
            st.dataframe(df_detailed, use_container_width=True)
    
    def render_cortex_ai_dashboard(self):
        """Render Cortex AI workload monitoring dashboard"""
        st.header("🤖 Cortex AI Workload Monitoring")
        
        if not self.monitor.cortex_monitor:
            st.warning("⚠️ Cortex AI monitoring is not available. Ensure the cortex_monitor module is installed and you have the required Snowflake privileges.")
            
            # Show sample data for demonstration
            st.subheader("📊 Sample Cortex AI Dashboard")
            sample_data = {
                'sensitive_data_discovery': {
                    'llm_cost': 85.20,
                    'embedding_cost': 12.45,
                    'warehouse_cost': 156.80,
                    'total_requests': 234,
                    'tokens_processed': '1.2M'
                },
                'schema_mapping': {
                    'llm_cost': 45.60,
                    'embedding_cost': 8.30,
                    'warehouse_cost': 89.40,
                    'total_requests': 156,
                    'tokens_processed': '892K'
                }
            }
            
            col1, col2 = st.columns(2)
            for workload, data in sample_data.items():
                with col1 if workload == 'sensitive_data_discovery' else col2:
                    st.subheader(f"📁 {workload.replace('_', ' ').title()}")
                    st.metric("LLM Cost", f"${data['llm_cost']:.2f}")
                    st.metric("Embedding Cost", f"${data['embedding_cost']:.2f}")
                    st.metric("Warehouse Cost", f"${data['warehouse_cost']:.2f}")
                    st.metric("Total Requests", data['total_requests'])
                    st.metric("Tokens Processed", data['tokens_processed'])
            
            return
        
        # Period selector
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Workload-Level Cost Consolidation")
        with col2:
            period_options = [
                (1, "24 hours"),
                (3, "3 days"),
                (7, "7 days"),
                (14, "14 days"),
                (30, "30 days")
            ]
            days = st.selectbox(
                "Analysis Period",
                options=[opt[0] for opt in period_options],
                index=2,
                format_func=lambda x: next(opt[1] for opt in period_options if opt[0] == x),
                key="cortex_period"
            )
        
        # Get Cortex workload metrics
        try:
            cortex_metrics = self.monitor.cortex_monitor.get_cortex_usage_by_workload(days)
        except Exception as e:
            st.error(f"Error fetching Cortex metrics: {e}")
            cortex_metrics = self.monitor.cortex_monitor.generate_sample_data()
        
        if not cortex_metrics:
            st.info("No Cortex AI usage detected for the selected period")
            return
        
        # Workload cost breakdown
        st.subheader("💰 Workload Cost Breakdown")
        
        workload_cols = st.columns(len(cortex_metrics))
        
        for i, (workload_name, metrics) in enumerate(cortex_metrics.items()):
            with workload_cols[i]:
                st.subheader(f"📁 {workload_name.replace('_', ' ').title()}")
                
                # Cost components
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "LLM Cost",
                        self.monitor.format_large_number(metrics.llm_cost_estimate, 'currency'),
                        f"{metrics.llm_requests} requests"
                    )
                    st.metric(
                        "UI Warehouse Cost",
                        self.monitor.format_large_number(
                            metrics.ui_credits_used * self.monitor.cost_models['warehouse_credit_cost'], 
                            'currency'
                        ),
                        f"{metrics.ui_query_count} queries"
                    )
                
                with col2:
                    st.metric(
                        "Embedding Cost",
                        self.monitor.format_large_number(metrics.embedding_cost_estimate, 'currency'),
                        f"{metrics.embedding_requests} requests"
                    )
                    st.metric(
                        "SQL Warehouse Cost",
                        self.monitor.format_large_number(
                            metrics.sql_credits_used * self.monitor.cost_models['warehouse_credit_cost'],
                            'currency'
                        ),
                        f"{metrics.sql_query_count} queries"
                    )
                
                # Total cost with change indicator
                change_indicator = ""
                if metrics.cost_change_percent is not None:
                    if metrics.cost_change_percent > 0:
                        change_indicator = f"🔺 +{metrics.cost_change_percent:.1f}%"
                    else:
                        change_indicator = f"🔻 {metrics.cost_change_percent:.1f}%"
                
                st.metric(
                    "Total Workload Cost",
                    self.monitor.format_large_number(metrics.total_cost_estimate, 'currency'),
                    change_indicator
                )
                
                # Efficiency metrics
                st.subheader("⚡ Efficiency")
                st.metric(
                    "Rows/Credit",
                    self.monitor.format_large_number(metrics.rows_per_credit, 'rows')
                )
                st.metric(
                    "GB/Credit",
                    f"{metrics.gb_per_credit:.2f}"
                )
        
        # Consolidated cost visualization
        st.subheader("📊 Cost Component Analysis")
        
        # Prepare data for visualization
        cost_breakdown_data = []
        for workload_name, metrics in cortex_metrics.items():
            cost_breakdown_data.extend([
                {'Workload': workload_name, 'Component': 'LLM', 'Cost': metrics.llm_cost_estimate},
                {'Workload': workload_name, 'Component': 'Embedding', 'Cost': metrics.embedding_cost_estimate},
                {'Workload': workload_name, 'Component': 'UI Warehouse', 'Cost': metrics.ui_credits_used * self.monitor.cost_models['warehouse_credit_cost']},
                {'Workload': workload_name, 'Component': 'SQL Warehouse', 'Cost': metrics.sql_credits_used * self.monitor.cost_models['warehouse_credit_cost']}
            ])
        
        if cost_breakdown_data:
            df_costs = pd.DataFrame(cost_breakdown_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Stacked bar chart
                fig_stacked = px.bar(
                    df_costs,
                    x='Workload',
                    y='Cost',
                    color='Component',
                    title='Cost by Component and Workload',
                    labels={'Cost': 'Cost ($)'}
                )
                fig_stacked.update_layout(height=400)
                st.plotly_chart(fig_stacked, use_container_width=True)
            
            with col2:
                # Sunburst chart for component breakdown
                fig_sunburst = px.sunburst(
                    df_costs,
                    path=['Component', 'Workload'],
                    values='Cost',
                    title='Hierarchical Cost Breakdown'
                )
                fig_sunburst.update_layout(height=400)
                st.plotly_chart(fig_sunburst, use_container_width=True)
        
        # Detailed workload analysis
        st.subheader("🔍 Detailed Workload Analysis")
        
        selected_workload = st.selectbox(
            "Select workload for detailed analysis",
            options=list(cortex_metrics.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_workload:
            breakdown = self.monitor.cortex_monitor.get_workload_cost_breakdown(selected_workload, days)
            
            if breakdown:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("By Feature")
                    for feature, cost in breakdown.components.items():
                        st.metric(feature.title(), f"${cost:.2f}")
                
                with col2:
                    st.subheader("By Warehouse")
                    for warehouse, cost in list(breakdown.warehouses.items())[:3]:  # Top 3
                        st.metric(warehouse, f"${cost:.2f}")
                
                with col3:
                    st.subheader("By Query Tag")
                    for tag, cost in list(breakdown.query_tags.items())[:3]:  # Top 3
                        st.metric(tag, f"${cost:.2f}")
    
    def render_daily_ingestion_dashboard(self):
        """Render enhanced daily ingestion volume dashboard"""
        st.header("📈 Daily Ingestion Volume Analysis")
        
        if not self.monitor.cortex_monitor:
            st.warning("Daily ingestion monitoring requires Cortex AI monitor")
            return
        
        # Period selector
        days = st.selectbox(
            "Analysis Period",
            options=[7, 30, 90, 180],
            index=1,
            format_func=lambda x: f"{x} days"
        )
        
        # Get ingestion metrics
        try:
            ingestion_df = self.monitor.cortex_monitor.get_daily_ingestion_metrics(days)
        except Exception as e:
            st.error(f"Error fetching ingestion data: {e}")
            return
        
        if ingestion_df.empty:
            st.info("No ingestion data found for the selected period")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_gb = ingestion_df['GB_INGESTED'].sum()
        total_rows = ingestion_df['ROWS_INGESTED'].sum()
        total_credits = ingestion_df['CREDITS_USED'].sum()
        avg_operations = ingestion_df['COPY_OPERATIONS'].mean()
        
        with col1:
            st.metric(
                "Total Data Ingested",
                self.monitor.format_large_number(total_gb, 'bytes'),
                f"{days} days"
            )
        with col2:
            st.metric(
                "Total Rows Ingested",
                self.monitor.format_large_number(total_rows, 'rows'),
                "processed"
            )
        with col3:
            st.metric(
                "Total Credits Used",
                f"{total_credits:.1f}",
                f"${total_credits * self.monitor.cost_models['warehouse_credit_cost']:.2f}"
            )
        with col4:
            st.metric(
                "Avg Daily Operations",
                f"{avg_operations:.0f}",
                "COPY commands"
            )
        
        # Trend visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Combined volume trends
            fig_volume = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Data Volume (GB)', 'Row Count'),
                vertical_spacing=0.1
            )
            
            fig_volume.add_trace(
                go.Scatter(
                    x=ingestion_df['INGESTION_DATE'],
                    y=ingestion_df['GB_INGESTED'],
                    mode='lines+markers',
                    name='GB Ingested',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
            
            fig_volume.add_trace(
                go.Scatter(
                    x=ingestion_df['INGESTION_DATE'],
                    y=ingestion_df['ROWS_INGESTED'],
                    mode='lines+markers',
                    name='Rows Ingested',
                    line=dict(color='green')
                ),
                row=2, col=1
            )
            
            fig_volume.update_layout(
                title="Daily Ingestion Volume Trends",
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        
        with col2:
            # Credit usage with efficiency overlay
            fig_credits = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Credits Used', 'Efficiency (Rows per Credit)'),
                vertical_spacing=0.1
            )
            
            fig_credits.add_trace(
                go.Bar(
                    x=ingestion_df['INGESTION_DATE'],
                    y=ingestion_df['CREDITS_USED'],
                    name='Credits Used',
                    marker_color='orange'
                ),
                row=1, col=1
            )
            
            # Calculate efficiency
            efficiency = ingestion_df['ROWS_INGESTED'] / ingestion_df['CREDITS_USED'].replace(0, 0.01)
            fig_credits.add_trace(
                go.Scatter(
                    x=ingestion_df['INGESTION_DATE'],
                    y=efficiency,
                    mode='lines+markers',
                    name='Rows/Credit',
                    line=dict(color='red')
                ),
                row=2, col=1
            )
            
            fig_credits.update_layout(
                title="Credit Usage & Efficiency",
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_credits, use_container_width=True)
        
        # Detailed table with formatted numbers
        st.subheader("📊 Daily Ingestion Details")
        
        display_df = ingestion_df.copy()
        display_df['INGESTION_DATE'] = display_df['INGESTION_DATE'].dt.strftime('%Y-%m-%d')
        display_df['GB_INGESTED'] = display_df['GB_INGESTED'].apply(lambda x: self.monitor.format_large_number(x, 'bytes'))
        display_df['ROWS_INGESTED'] = display_df['ROWS_INGESTED'].apply(lambda x: self.monitor.format_large_number(x, 'rows'))
        display_df['CREDITS_USED'] = display_df['CREDITS_USED'].apply(lambda x: f"{x:.2f}")
        display_df['AVG_EXECUTION_TIME'] = display_df['AVG_EXECUTION_TIME'].apply(lambda x: f"{x/1000:.1f}s")
        
        display_df.columns = ['Date', 'Copy Ops', 'Credits', 'GB Ingested', 'Rows Ingested', 'Avg Time']
        st.dataframe(display_df, use_container_width=True)

    def render_project_configuration(self):
        """Render project configuration interface"""
        st.header("⚙️ Project Configuration")
        
        st.subheader("Monitored Projects")
        
        # Display current projects
        for project_name, config in self.monitor.projects.items():
            with st.expander(f"📁 {project_name} ({config.project_type})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Description:** {config.description}")
                    st.write(f"**Cost Center:** {config.cost_center}")
                    st.write(f"**Priority:** {config.priority}")
                
                with col2:
                    st.write("**Identification Patterns:**")
                    st.write(f"- Warehouses: `{config.warehouse_pattern}`")
                    st.write(f"- Databases: `{config.database_pattern}`")
                    st.write(f"- Users: `{config.user_pattern}`")
        
        # Add new project
        st.subheader("Add New Project")
        
        with st.form("add_project"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Project Name")
                new_type = st.selectbox("Project Type", ["sensitive_data", "schema_mapper", "etl", "analytics", "other"])
                new_description = st.text_area("Description")
            
            with col2:
                new_warehouse_pattern = st.text_input("Warehouse Pattern", placeholder="%PROJECT_NAME%")
                new_database_pattern = st.text_input("Database Pattern", placeholder="%PROJECT_NAME%")
                new_user_pattern = st.text_input("User Pattern", placeholder="%PROJECT_NAME%")
                new_cost_center = st.text_input("Cost Center")
                new_priority = st.selectbox("Priority", ["high", "medium", "low"])
            
            if st.form_submit_button("Add Project"):
                if new_name and new_name not in self.monitor.projects:
                    new_project = ProjectConfig(
                        project_name=new_name,
                        project_type=new_type,
                        warehouse_pattern=new_warehouse_pattern,
                        database_pattern=new_database_pattern,
                        user_pattern=new_user_pattern,
                        description=new_description,
                        cost_center=new_cost_center,
                        priority=new_priority
                    )
                    
                    self.monitor.projects[new_name] = new_project
                    st.session_state.project_configs = self.monitor.projects
                    st.success(f"✅ Added project: {new_name}")
                    st.rerun()
                else:
                    st.error("Project name is required and must be unique")
    
    def render_export_options(self):
        """Render data export options"""
        st.header("📊 Export & Reporting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_period = st.selectbox(
                "Export Period",
                options=[24, 48, 168, 720],  # hours
                format_func=lambda x: f"{x} hours" if x < 168 else f"{x//24} days"
            )
        
        with col2:
            export_format = st.selectbox("Export Format", ["JSON", "CSV"])
        
        if st.button("📥 Generate Report"):
            # Generate comprehensive report
            all_metrics = self.monitor.get_all_project_metrics(export_period)
            insights = self.monitor.get_project_comparison(export_period)
            
            report_data = {
                "report_timestamp": datetime.now().isoformat(),
                "time_period_hours": export_period,
                "project_metrics": {name: asdict(metrics) for name, metrics in all_metrics.items()},
                "cross_project_insights": [asdict(insight) for insight in insights],
                "project_configurations": {name: asdict(config) for name, config in self.monitor.projects.items()},
                "summary": {
                    "total_projects": len(all_metrics),
                    "total_cost": sum(m.estimated_cost for m in all_metrics.values()),
                    "total_queries": sum(m.query_count for m in all_metrics.values()),
                    "total_credits": sum(m.warehouse_credits for m in all_metrics.values())
                }
            }
            
            if export_format == "JSON":
                report_str = json.dumps(report_data, indent=2, default=str)
                st.download_button(
                    label="Download JSON Report",
                    data=report_str,
                    file_name=f"snowflake_multi_project_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                # Convert to CSV format
                metrics_df = pd.DataFrame([asdict(m) for m in all_metrics.values()])
                csv_str = metrics_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV Report",
                    data=csv_str,
                    file_name=f"snowflake_multi_project_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            st.success("✅ Report generated successfully!")

    def run_dashboard(self):
        """Main dashboard controller with enhanced navigation"""
        # Render header
        self.render_header()
        
        # Enhanced sidebar navigation
        with st.sidebar:
            st.title("🧭 Navigation")
            
            page = st.radio(
                "Select View",
                options=[
                    "📊 Enhanced Project Overview",
                    "🤖 Cortex AI Workloads",
                    "📈 Daily Ingestion Analysis", 
                    "🔍 Cross-Project Insights",
                    "📈 Resource Trends",
                    "⚙️ Configuration",
                    "📊 Export & Reports"
                ]
            )
            
            st.markdown("---")
            
            # Auto-refresh and connection info
            auto_refresh = st.checkbox("Auto Refresh (30s)")
            
            st.markdown("---")
            st.subheader("ℹ️ Enhanced Features")
            st.write("✅ Query Attribution cost tracking")
            st.write("✅ Cortex AI workload consolidation")
            st.write("✅ Efficiency metrics (rows/GB per credit)")
            st.write("✅ Period comparison analysis")
            st.write("✅ Enhanced number formatting")
            st.write("✅ Sample data for testing")
        
        # Render selected page
        if page == "📊 Enhanced Project Overview":
            self.render_enhanced_project_overview()
        elif page == "🤖 Cortex AI Workloads":
            self.render_cortex_ai_dashboard()
        elif page == "📈 Daily Ingestion Analysis":
            self.render_daily_ingestion_dashboard()
        elif page == "🔍 Cross-Project Insights":
            # Keep existing cross-project insights method
            pass
        elif page == "📈 Resource Trends":
            # Keep existing resource trends method
            pass
        elif page == "⚙️ Configuration":
            # Keep existing configuration method
            pass
        elif page == "📊 Export & Reports":
            # Keep existing export method
            pass
        
        # Auto-refresh logic
        if auto_refresh:
            time.sleep(30)
            st.rerun()

def main():
    """Enhanced main application entry point"""
    
    # Initialize components
    db_connection = SnowflakeConnection()
    
    if not db_connection.connection:
        st.error("❌ Unable to connect to Snowflake. Please check your connection settings.")
        st.info("💡 Ensure you have the proper Snowflake connection configured in your Streamlit secrets.")
        
        # Show connection help
        with st.expander("🔧 Connection Setup Help"):
            st.code("""
            # .streamlit/secrets.toml
            [connections.snowflake]
            account = "your-account-identifier"
            user = "your-username"
            password = "your-password"
            database = "your-database"
            schema = "your-schema"
            warehouse = "your-warehouse"
            role = "your-role"
            """)
            
            st.markdown("**Required Privileges:**")
            st.code("""
            GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;
            GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION TO ROLE <your_role>;
            GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE TO ROLE <your_role>;
            GRANT SELECT ON SNOWFLAKE.ACCOUNT_USAGE.CORTEX_EMBEDDING_USAGE TO ROLE <your_role>;
            """)
        
        st.stop()
    
    # Initialize enhanced monitor and dashboard
    monitor = MultiProjectMonitor(db_connection)
    dashboard = MultiProjectDashboard(monitor)
    
    # Run the enhanced dashboard
    dashboard.run_dashboard()

if __name__ == "__main__":
    main() 