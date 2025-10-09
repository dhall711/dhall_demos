"""
Cortex AI Monitoring Module
Handles workload-level cost consolidation for Snowflake Cortex AI features.

Tracks:
- LLM usage and token costs
- Vector embedding costs  
- UI warehouse costs
- SQL warehouse costs
- Query attribution for shared warehouses
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

@dataclass
class CortexUsageMetrics:
    """Cortex AI usage metrics by workload"""
    workload_name: str
    query_tag: str
    warehouse_name: str
    
    # LLM Costs
    llm_requests: int
    llm_tokens_processed: int
    llm_credits_used: float
    llm_cost_estimate: float
    
    # Vector Embedding Costs
    embedding_requests: int
    embedding_tokens: int
    embedding_credits_used: float
    embedding_cost_estimate: float
    
    # UI Warehouse Costs
    ui_query_count: int
    ui_credits_used: float
    ui_execution_time_ms: int
    
    # SQL Warehouse Costs
    sql_query_count: int
    sql_credits_used: float
    sql_execution_time_ms: int
    
    # Consolidated Metrics
    total_credits: float
    total_cost_estimate: float
    rows_per_credit: float
    gb_per_credit: float
    
    # Period comparison
    period: str
    prev_period_total_cost: Optional[float] = None
    cost_change_percent: Optional[float] = None

@dataclass
class WorkloadCostBreakdown:
    """Detailed cost breakdown for a workload"""
    workload_name: str
    time_period: str
    
    components: Dict[str, float]  # feature -> cost
    warehouses: Dict[str, float]  # warehouse -> cost
    query_tags: Dict[str, float]  # tag -> cost
    
    total_cost: float
    total_credits: float
    query_count: int
    
    # Efficiency metrics
    cost_per_query: float
    credits_per_query: float
    rows_processed: int
    gb_processed: float

class CortexAIMonitor:
    """Advanced monitoring for Cortex AI workloads with cost attribution"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.cost_models = {
            'llm_cost_per_token': 0.0001,  # Estimated cost per token
            'embedding_cost_per_token': 0.00005,
            'warehouse_credit_cost': 3.0
        }
        
        # Workload identification patterns
        self.workload_patterns = {
            'sensitive_data_discovery': {
                'query_tags': ['SIS_DISCOVERY', 'DDM_ANALYSIS', 'PRIVACY_SCAN'],
                'warehouses': ['%SENSITIVE%', '%DDM%', '%DISCOVERY%'],
                'cortex_functions': ['CLASSIFY_TEXT', 'EXTRACT_SEMANTIC_PATTERN']
            },
            'schema_mapping': {
                'query_tags': ['SCHEMA_MAP', 'ETL_TRANSFORM', 'MIGRATION'],
                'warehouses': ['%MAPPER%', '%TRANSFORM%', '%ETL%'],
                'cortex_functions': ['COMPLETE', 'SEMANTIC_SIMILARITY']
            }
        }
    
    def get_cortex_usage_by_workload(self, days: int = 7) -> Dict[str, CortexUsageMetrics]:
        """Get Cortex AI usage metrics consolidated by workload"""
        
        try:
            # Query that consolidates costs using Query Attribution view
            query = f"""
            WITH cortex_llm_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    model_name,
                    COUNT(*) as llm_requests,
                    SUM(total_tokens) as llm_tokens,
                    SUM(credits_used) as llm_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag, model_name
            ),
            
            cortex_embedding_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    model_name,
                    COUNT(*) as embedding_requests,
                    SUM(total_tokens) as embedding_tokens,
                    SUM(credits_used) as embedding_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_EMBEDDING_USAGE
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag, model_name
            ),
            
            query_attribution AS (
                SELECT 
                    DATE_TRUNC('day', start_time) as usage_date,
                    warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as query_count,
                    SUM(credits_attributed_to_query) as attributed_credits,
                    SUM(execution_time_ms) as total_execution_time,
                    SUM(bytes_scanned) as bytes_scanned,
                    SUM(rows_produced) as rows_produced,
                    -- Classify query types
                    SUM(CASE 
                        WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                             OR UPPER(query_text) LIKE '%UI%' 
                        THEN credits_attributed_to_query 
                        ELSE 0 
                    END) as ui_credits,
                    SUM(CASE 
                        WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                             AND UPPER(query_text) NOT LIKE '%UI%' 
                        THEN credits_attributed_to_query 
                        ELSE 0 
                    END) as sql_credits,
                    COUNT(CASE 
                        WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                             OR UPPER(query_text) LIKE '%UI%' 
                        THEN 1 
                    END) as ui_query_count,
                    COUNT(CASE 
                        WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                             AND UPPER(query_text) NOT LIKE '%UI%' 
                        THEN 1 
                    END) as sql_query_count
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
                WHERE start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                AND query_tag IS NOT NULL
                GROUP BY usage_date, warehouse_name, query_tag
            ),
            
            workload_consolidated AS (
                SELECT 
                    qa.usage_date,
                    qa.warehouse_name,
                    qa.query_tag,
                    
                    -- Determine workload from patterns
                    CASE 
                        WHEN qa.query_tag ILIKE ANY ('SIS_DISCOVERY', 'DDM_ANALYSIS', 'PRIVACY_SCAN')
                             OR qa.warehouse_name ILIKE ANY ('%SENSITIVE%', '%DDM%', '%DISCOVERY%')
                        THEN 'sensitive_data_discovery'
                        WHEN qa.query_tag ILIKE ANY ('SCHEMA_MAP', 'ETL_TRANSFORM', 'MIGRATION')
                             OR qa.warehouse_name ILIKE ANY ('%MAPPER%', '%TRANSFORM%', '%ETL%')
                        THEN 'schema_mapping'
                        ELSE 'other'
                    END as workload_name,
                    
                    -- Query Attribution Metrics
                    COALESCE(qa.query_count, 0) as total_queries,
                    COALESCE(qa.attributed_credits, 0) as warehouse_credits,
                    COALESCE(qa.ui_credits, 0) as ui_credits,
                    COALESCE(qa.sql_credits, 0) as sql_credits,
                    COALESCE(qa.ui_query_count, 0) as ui_queries,
                    COALESCE(qa.sql_query_count, 0) as sql_queries,
                    COALESCE(qa.total_execution_time, 0) as execution_time_ms,
                    COALESCE(qa.bytes_scanned, 0) as bytes_scanned,
                    COALESCE(qa.rows_produced, 0) as rows_produced,
                    
                    -- LLM Metrics
                    COALESCE(llm.llm_requests, 0) as llm_requests,
                    COALESCE(llm.llm_tokens, 0) as llm_tokens,
                    COALESCE(llm.llm_credits, 0) as llm_credits,
                    
                    -- Embedding Metrics
                    COALESCE(emb.embedding_requests, 0) as embedding_requests,
                    COALESCE(emb.embedding_tokens, 0) as embedding_tokens,
                    COALESCE(emb.embedding_credits, 0) as embedding_credits
                    
                FROM query_attribution qa
                LEFT JOIN cortex_llm_usage llm 
                    ON qa.usage_date = llm.usage_date 
                    AND qa.warehouse_name = llm.warehouse_name 
                    AND qa.query_tag = llm.query_tag
                LEFT JOIN cortex_embedding_usage emb 
                    ON qa.usage_date = emb.usage_date 
                    AND qa.warehouse_name = emb.warehouse_name 
                    AND qa.query_tag = emb.query_tag
            )
            
            SELECT 
                workload_name,
                query_tag,
                warehouse_name,
                SUM(llm_requests) as llm_requests,
                SUM(llm_tokens) as llm_tokens_processed,
                SUM(llm_credits) as llm_credits_used,
                SUM(embedding_requests) as embedding_requests,
                SUM(embedding_tokens) as embedding_tokens,
                SUM(embedding_credits) as embedding_credits_used,
                SUM(ui_queries) as ui_query_count,
                SUM(ui_credits) as ui_credits_used,
                SUM(sql_queries) as sql_query_count,
                SUM(sql_credits) as sql_credits_used,
                SUM(execution_time_ms) as total_execution_time_ms,
                SUM(warehouse_credits) as total_warehouse_credits,
                SUM(bytes_scanned) / POWER(1024, 3) as gb_processed,
                SUM(rows_produced) as rows_processed
            FROM workload_consolidated
            WHERE workload_name != 'other'
            GROUP BY workload_name, query_tag, warehouse_name
            ORDER BY workload_name, total_warehouse_credits DESC
            """
            
            df = self.db.execute_query(query, "fetching Cortex workload usage")
            
            if df is None or df.empty:
                return {}
            
            workload_metrics = {}
            
            for _, row in df.iterrows():
                workload_name = row['WORKLOAD_NAME']
                
                # Calculate cost estimates
                llm_cost = float(row['LLM_TOKENS_PROCESSED']) * self.cost_models['llm_cost_per_token']
                embedding_cost = float(row['EMBEDDING_TOKENS']) * self.cost_models['embedding_cost_per_token']
                warehouse_cost = float(row['TOTAL_WAREHOUSE_CREDITS']) * self.cost_models['warehouse_credit_cost']
                
                total_cost = llm_cost + embedding_cost + warehouse_cost
                total_credits = float(row['TOTAL_WAREHOUSE_CREDITS']) + float(row['LLM_CREDITS_USED']) + float(row['EMBEDDING_CREDITS_USED'])
                
                # Calculate efficiency metrics
                rows_per_credit = float(row['ROWS_PROCESSED']) / max(total_credits, 0.01)
                gb_per_credit = float(row['GB_PROCESSED']) / max(total_credits, 0.01)
                
                metrics = CortexUsageMetrics(
                    workload_name=workload_name,
                    query_tag=row['QUERY_TAG'],
                    warehouse_name=row['WAREHOUSE_NAME'],
                    llm_requests=int(row['LLM_REQUESTS']),
                    llm_tokens_processed=int(row['LLM_TOKENS_PROCESSED']),
                    llm_credits_used=float(row['LLM_CREDITS_USED']),
                    llm_cost_estimate=llm_cost,
                    embedding_requests=int(row['EMBEDDING_REQUESTS']),
                    embedding_tokens=int(row['EMBEDDING_TOKENS']),
                    embedding_credits_used=float(row['EMBEDDING_CREDITS_USED']),
                    embedding_cost_estimate=embedding_cost,
                    ui_query_count=int(row['UI_QUERY_COUNT']),
                    ui_credits_used=float(row['UI_CREDITS_USED']),
                    ui_execution_time_ms=int(row['TOTAL_EXECUTION_TIME_MS']),
                    sql_query_count=int(row['SQL_QUERY_COUNT']),
                    sql_credits_used=float(row['SQL_CREDITS_USED']),
                    sql_execution_time_ms=int(row['TOTAL_EXECUTION_TIME_MS']),
                    total_credits=total_credits,
                    total_cost_estimate=total_cost,
                    rows_per_credit=rows_per_credit,
                    gb_per_credit=gb_per_credit,
                    period=f"{days}d"
                )
                
                if workload_name not in workload_metrics:
                    workload_metrics[workload_name] = metrics
                else:
                    # Aggregate multiple entries for the same workload
                    existing = workload_metrics[workload_name]
                    workload_metrics[workload_name] = CortexUsageMetrics(
                        workload_name=workload_name,
                        query_tag=f"{existing.query_tag},{metrics.query_tag}",
                        warehouse_name=f"{existing.warehouse_name},{metrics.warehouse_name}",
                        llm_requests=existing.llm_requests + metrics.llm_requests,
                        llm_tokens_processed=existing.llm_tokens_processed + metrics.llm_tokens_processed,
                        llm_credits_used=existing.llm_credits_used + metrics.llm_credits_used,
                        llm_cost_estimate=existing.llm_cost_estimate + metrics.llm_cost_estimate,
                        embedding_requests=existing.embedding_requests + metrics.embedding_requests,
                        embedding_tokens=existing.embedding_tokens + metrics.embedding_tokens,
                        embedding_credits_used=existing.embedding_credits_used + metrics.embedding_credits_used,
                        embedding_cost_estimate=existing.embedding_cost_estimate + metrics.embedding_cost_estimate,
                        ui_query_count=existing.ui_query_count + metrics.ui_query_count,
                        ui_credits_used=existing.ui_credits_used + metrics.ui_credits_used,
                        ui_execution_time_ms=existing.ui_execution_time_ms + metrics.ui_execution_time_ms,
                        sql_query_count=existing.sql_query_count + metrics.sql_query_count,
                        sql_credits_used=existing.sql_credits_used + metrics.sql_credits_used,
                        sql_execution_time_ms=existing.sql_execution_time_ms + metrics.sql_execution_time_ms,
                        total_credits=existing.total_credits + metrics.total_credits,
                        total_cost_estimate=existing.total_cost_estimate + metrics.total_cost_estimate,
                        rows_per_credit=(existing.rows_per_credit + metrics.rows_per_credit) / 2,
                        gb_per_credit=(existing.gb_per_credit + metrics.gb_per_credit) / 2,
                        period=f"{days}d"
                    )
            
            # Get previous period for comparison
            for workload_name in workload_metrics:
                prev_cost = self._get_previous_period_cost(workload_name, days)
                if prev_cost:
                    current_cost = workload_metrics[workload_name].total_cost_estimate
                    change_percent = ((current_cost - prev_cost) / prev_cost) * 100
                    
                    # Update with comparison data
                    metrics = workload_metrics[workload_name]
                    workload_metrics[workload_name] = CortexUsageMetrics(
                        workload_name=metrics.workload_name,
                        query_tag=metrics.query_tag,
                        warehouse_name=metrics.warehouse_name,
                        llm_requests=metrics.llm_requests,
                        llm_tokens_processed=metrics.llm_tokens_processed,
                        llm_credits_used=metrics.llm_credits_used,
                        llm_cost_estimate=metrics.llm_cost_estimate,
                        embedding_requests=metrics.embedding_requests,
                        embedding_tokens=metrics.embedding_tokens,
                        embedding_credits_used=metrics.embedding_credits_used,
                        embedding_cost_estimate=metrics.embedding_cost_estimate,
                        ui_query_count=metrics.ui_query_count,
                        ui_credits_used=metrics.ui_credits_used,
                        ui_execution_time_ms=metrics.ui_execution_time_ms,
                        sql_query_count=metrics.sql_query_count,
                        sql_credits_used=metrics.sql_credits_used,
                        sql_execution_time_ms=metrics.sql_execution_time_ms,
                        total_credits=metrics.total_credits,
                        total_cost_estimate=metrics.total_cost_estimate,
                        rows_per_credit=metrics.rows_per_credit,
                        gb_per_credit=metrics.gb_per_credit,
                        period=metrics.period,
                        prev_period_total_cost=prev_cost,
                        cost_change_percent=change_percent
                    )
            
            return workload_metrics
            
        except Exception as e:
            st.error(f"Error fetching Cortex workload usage: {e}")
            return {}
    
    def _get_previous_period_cost(self, workload_name: str, current_days: int) -> Optional[float]:
        """Get cost for the previous period for comparison"""
        try:
            # Simple implementation - get the previous period of same length
            query = f"""
            SELECT SUM(
                COALESCE(credits_attributed_to_query, 0) * {self.cost_models['warehouse_credit_cost']}
            ) as prev_cost
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
            WHERE start_time >= DATEADD(day, -{current_days * 2}, CURRENT_TIMESTAMP())
            AND start_time < DATEADD(day, -{current_days}, CURRENT_TIMESTAMP())
            AND (
                query_tag ILIKE '%{workload_name.upper()}%' OR
                warehouse_name ILIKE '%{workload_name.upper()}%'
            )
            """
            
            df = self.db.execute_query(query, f"fetching previous period cost for {workload_name}")
            
            if df is not None and not df.empty and df.iloc[0]['PREV_COST'] is not None:
                return float(df.iloc[0]['PREV_COST'])
            
        except Exception:
            pass
        
        return None
    
    def get_workload_cost_breakdown(self, workload_name: str, days: int = 7) -> Optional[WorkloadCostBreakdown]:
        """Get detailed cost breakdown for a specific workload"""
        
        try:
            query = f"""
            WITH workload_costs AS (
                SELECT 
                    qa.warehouse_name,
                    qa.query_tag,
                    COUNT(*) as query_count,
                    SUM(qa.credits_attributed_to_query) as credits_used,
                    SUM(qa.bytes_scanned) / POWER(1024, 3) as gb_processed,
                    SUM(qa.rows_produced) as rows_processed,
                    
                    -- Classify by feature type
                    CASE 
                        WHEN UPPER(qa.query_text) LIKE '%CORTEX%LLM%' THEN 'llm'
                        WHEN UPPER(qa.query_text) LIKE '%CORTEX%EMBED%' THEN 'embedding'
                        WHEN UPPER(qa.query_text) LIKE '%STREAMLIT%' THEN 'ui'
                        ELSE 'sql'
                    END as feature_type
                    
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION qa
                WHERE qa.start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                AND (
                    qa.query_tag ILIKE '%{workload_name.upper()}%' OR
                    qa.warehouse_name ILIKE '%{workload_name.upper()}%'
                )
                GROUP BY qa.warehouse_name, qa.query_tag, feature_type
            )
            
            SELECT 
                feature_type,
                warehouse_name,
                query_tag,
                SUM(query_count) as total_queries,
                SUM(credits_used) as total_credits,
                SUM(gb_processed) as total_gb,
                SUM(rows_processed) as total_rows
            FROM workload_costs
            GROUP BY feature_type, warehouse_name, query_tag
            ORDER BY total_credits DESC
            """
            
            df = self.db.execute_query(query, f"fetching cost breakdown for {workload_name}")
            
            if df is None or df.empty:
                return None
            
            # Aggregate costs by different dimensions
            components = defaultdict(float)
            warehouses = defaultdict(float)
            query_tags = defaultdict(float)
            
            total_cost = 0
            total_credits = 0
            total_queries = 0
            total_rows = 0
            total_gb = 0
            
            for _, row in df.iterrows():
                feature_cost = float(row['TOTAL_CREDITS']) * self.cost_models['warehouse_credit_cost']
                
                components[row['FEATURE_TYPE']] += feature_cost
                warehouses[row['WAREHOUSE_NAME']] += feature_cost
                query_tags[row['QUERY_TAG']] += feature_cost
                
                total_cost += feature_cost
                total_credits += float(row['TOTAL_CREDITS'])
                total_queries += int(row['TOTAL_QUERIES'])
                total_rows += int(row['TOTAL_ROWS'])
                total_gb += float(row['TOTAL_GB'])
            
            return WorkloadCostBreakdown(
                workload_name=workload_name,
                time_period=f"{days}d",
                components=dict(components),
                warehouses=dict(warehouses),
                query_tags=dict(query_tags),
                total_cost=total_cost,
                total_credits=total_credits,
                query_count=total_queries,
                cost_per_query=total_cost / max(total_queries, 1),
                credits_per_query=total_credits / max(total_queries, 1),
                rows_processed=total_rows,
                gb_processed=total_gb
            )
            
        except Exception as e:
            st.error(f"Error fetching workload cost breakdown: {e}")
            return None
    
    def get_daily_ingestion_metrics(self, days: int = 30) -> pd.DataFrame:
        """Get daily ingestion volume metrics with enhanced formatting"""
        
        try:
            query = f"""
            SELECT 
                DATE_TRUNC('day', start_time) as ingestion_date,
                COUNT(*) as copy_operations,
                SUM(credits_attributed_to_query) as credits_used,
                SUM(bytes_scanned) / POWER(1024, 3) as gb_ingested,
                SUM(rows_produced) as rows_ingested,
                AVG(execution_time_ms) as avg_execution_time
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
            WHERE start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
            AND UPPER(query_text) LIKE '%COPY%'
            GROUP BY DATE_TRUNC('day', start_time)
            ORDER BY ingestion_date DESC
            """
            
            df = self.db.execute_query(query, "fetching daily ingestion metrics")
            
            if df is not None and not df.empty:
                # Convert dates and add formatting
                df['INGESTION_DATE'] = pd.to_datetime(df['INGESTION_DATE'])
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error fetching ingestion metrics: {e}")
            return pd.DataFrame()
    
    def format_large_numbers(self, number: float, metric_type: str = 'count') -> str:
        """Format large numbers with K, M, B, T suffixes"""
        
        if metric_type == 'rows':
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
        elif metric_type == 'bytes':
            if number >= 1e12:
                return f"{number/1e12:.1f}TB"
            elif number >= 1e9:
                return f"{number/1e9:.1f}GB"
            elif number >= 1e6:
                return f"{number/1e6:.1f}MB"
            elif number >= 1e3:
                return f"{number/1e3:.1f}KB"
            else:
                return f"{number:.0f}B"
        else:  # currency
            if number >= 1e6:
                return f"${number/1e6:.1f}M"
            elif number >= 1e3:
                return f"${number/1e3:.1f}K"
            else:
                return f"${number:.2f}"
    
    def generate_sample_data(self) -> Dict[str, CortexUsageMetrics]:
        """Generate sample data for testing when connection fails"""
        
        sample_data = {
            'sensitive_data_discovery': CortexUsageMetrics(
                workload_name='sensitive_data_discovery',
                query_tag='SIS_DISCOVERY,DDM_ANALYSIS',
                warehouse_name='SENSITIVE_WH,DDM_WH',
                llm_requests=145,
                llm_tokens_processed=28500,
                llm_credits_used=12.3,
                llm_cost_estimate=2.85,
                embedding_requests=67,
                embedding_tokens=13400,
                embedding_credits_used=5.2,
                embedding_cost_estimate=0.67,
                ui_query_count=234,
                ui_credits_used=8.9,
                ui_execution_time_ms=456000,
                sql_query_count=891,
                sql_credits_used=34.2,
                sql_execution_time_ms=1234000,
                total_credits=60.6,
                total_cost_estimate=185.45,
                rows_per_credit=15420.5,
                gb_per_credit=0.89,
                period='7d',
                prev_period_total_cost=168.20,
                cost_change_percent=10.25
            ),
            'schema_mapping': CortexUsageMetrics(
                workload_name='schema_mapping',
                query_tag='SCHEMA_MAP,ETL_TRANSFORM',
                warehouse_name='MAPPER_WH,TRANSFORM_WH',
                llm_requests=89,
                llm_tokens_processed=17800,
                llm_credits_used=7.8,
                llm_cost_estimate=1.78,
                embedding_requests=23,
                embedding_tokens=4600,
                embedding_credits_used=1.9,
                embedding_cost_estimate=0.23,
                ui_query_count=156,
                ui_credits_used=5.4,
                ui_execution_time_ms=298000,
                sql_query_count=567,
                sql_credits_used=22.1,
                sql_execution_time_ms=789000,
                total_credits=37.2,
                total_cost_estimate=112.85,
                rows_per_credit=22150.8,
                gb_per_credit=1.24,
                period='7d',
                prev_period_total_cost=125.60,
                cost_change_percent=-10.15
            )
        }
        
        return sample_data 