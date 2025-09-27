"""
PostgreSQL Database Manager for KHAZAD_DUM Trading System
Production-ready database adapter with connection pooling and advanced features
"""

import logging
import psycopg2
from psycopg2 import sql, pool
from psycopg2.extras import RealDictCursor, Json
import pandas as pd
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from contextlib import contextmanager
from pathlib import Path
from decimal import Decimal
from urllib.parse import urlparse

# Import input validation for security
from src.security.input_validator import (
    InputValidator, 
    ValidationError, 
    SecurityViolationError,
    audit_input_validation
)

logger = logging.getLogger(__name__)


class PostgreSQLManager:
    """
    Production PostgreSQL Database Manager for KHAZAD_DUM
    Features: Connection pooling, JSON support, advanced queries, migrations
    """
    
    def __init__(self, database_url: Optional[str] = None, pool_size: int = 10):
        """
        Initialize PostgreSQL connection with pooling
        
        Args:
            database_url: PostgreSQL connection URL
            pool_size: Connection pool size
        """
        self.database_url = database_url or self._get_database_url()
        self.pool_size = pool_size
        self.connection_pool = None
        
        # Parse database URL
        self._parse_database_url()
        
        # Initialize connection pool
        self._init_connection_pool()
        
        # Verify connection and schema
        self._verify_connection()
        self._ensure_schema()
        
        logger.info(f"PostgreSQL Manager initialized with pool size {pool_size}")
    
    def _get_database_url(self) -> str:
        """Get database URL from environment or config"""
        # Try environment variable first
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url
        
        # Construct from individual components
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB', 'khazad_dum')
        username = os.getenv('POSTGRES_USER', 'khazad_user')
        password = os.getenv('POSTGRES_PASSWORD', 'secure_password_change_me')
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def _parse_database_url(self):
        """Parse database URL into components"""
        parsed = urlparse(self.database_url)
        
        self.db_config = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username,
            'password': parsed.password,
        }
        
        logger.debug(f"Database config: {parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}")
    
    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=self.pool_size,
                **self.db_config
            )
            logger.info("PostgreSQL connection pool initialized")
            
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise ConnectionError(f"Database connection failed: {e}")
    
    def _verify_connection(self):
        """Verify database connectivity"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                logger.info(f"Connected to PostgreSQL: {version}")
    
    def _ensure_schema(self):
        """Ensure database schema exists and is current"""
        try:
            current_version = self._get_schema_version()
            if current_version == 0:
                logger.info("Initializing database schema...")
                self._run_initial_schema()
            else:
                logger.info(f"Database schema version: {current_version}")
                
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            raise
    
    def _get_schema_version(self) -> int:
        """Get current schema version"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                    SELECT version FROM schema_version 
                    ORDER BY version DESC LIMIT 1
                    """)
                    result = cursor.fetchone()
                    return result[0] if result else 0
                    
        except psycopg2.Error:
            # Schema version table doesn't exist yet
            return 0
    
    def _run_initial_schema(self):
        """Run initial database schema creation"""
        schema_file = Path(__file__).parent.parent.parent.parent / "deploy/database/init.sql"
        
        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            return
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    with open(schema_file, 'r') as f:
                        schema_sql = f.read()
                    cursor.execute(schema_sql)
                    logger.info("Initial schema created successfully")
                    
        except Exception as e:
            logger.error(f"Failed to create initial schema: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with context management"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            conn.autocommit = False
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed, rolling back: {e}")
                raise
    
    def insert_stock_metrics(self, df: pd.DataFrame) -> int:
        """
        Bulk insert stock metrics with comprehensive validation
        
        Args:
            df: DataFrame with stock metrics
            
        Returns:
            Number of rows inserted
        """
        if df.empty:
            logger.warning("Attempted to insert empty DataFrame")
            return 0
        
        # Validate required columns
        required_columns = ['symbol']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Available columns that match our schema
        schema_columns = [
            'symbol', 'price', 'volume', 'dollar_volume', 'market_cap',
            'rsi_2', 'atr', 'sma_20', 'sma_50', 'avg_volume_20',
            'volume_ratio', 'change_1d', 'quality_score'
        ]
        
        available_columns = [col for col in schema_columns if col in df.columns]
        if not available_columns:
            raise ValueError("No valid columns found in DataFrame")
        
        try:
            # Filter DataFrame to available columns
            df_filtered = df[available_columns].copy()
            
            # Apply comprehensive input validation
            validated_records = []
            validation_errors = 0
            security_violations = 0
            
            for index, row in df_filtered.iterrows():
                try:
                    # Convert row to dict for validation
                    metrics_dict = row.to_dict()
                    
                    # Use input validator for comprehensive checks
                    validated_metrics = InputValidator.validate_stock_metrics(metrics_dict)
                    
                    # Add timestamp
                    validated_metrics['timestamp'] = datetime.now()
                    
                    validated_records.append(validated_metrics)
                    
                except SecurityViolationError as e:
                    security_violations += 1
                    logger.error(f"Security violation in row {index}: {e}")
                    
                except ValidationError as e:
                    validation_errors += 1
                    logger.warning(f"Validation error in row {index}: {e}")
                    
                except Exception as e:
                    validation_errors += 1
                    logger.error(f"Unexpected error validating row {index}: {e}")
            
            # Audit validation results
            audit_input_validation(
                record_count=len(df_filtered),
                validation_errors=validation_errors,
                security_violations=security_violations
            )
            
            if not validated_records:
                logger.warning("No valid records remaining after security validation")
                return 0
            
            # Convert to DataFrame and prepare for PostgreSQL
            df_validated = pd.DataFrame(validated_records)
            
            # Convert Decimal objects to float for JSON serialization
            for col in df_validated.columns:
                if df_validated[col].dtype == 'object':
                    if len(df_validated) > 0 and isinstance(df_validated[col].iloc[0], Decimal):
                        df_validated[col] = df_validated[col].astype(float)
            
            # Bulk insert with PostgreSQL
            rows_inserted = self._bulk_insert_stock_metrics(df_validated)
            
            logger.info(f"Successfully inserted {rows_inserted} validated stock metrics")
            
            # Log validation summary if needed
            if validation_errors > 0 or security_violations > 0:
                logger.warning(
                    f"Validation summary: {rows_inserted} inserted, "
                    f"{validation_errors} validation errors, "
                    f"{security_violations} security violations"
                )
            
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Failed to insert stock metrics: {e}")
            raise
    
    def _bulk_insert_stock_metrics(self, df: pd.DataFrame) -> int:
        """Perform bulk insert using PostgreSQL COPY"""
        try:
            with self.transaction() as conn:
                with conn.cursor() as cursor:
                    # Prepare column names and values
                    columns = list(df.columns)
                    
                    # Create INSERT statement with ON CONFLICT handling
                    insert_sql = sql.SQL("""
                    INSERT INTO stock_metrics ({})
                    VALUES ({})
                    ON CONFLICT (symbol, timestamp) 
                    DO UPDATE SET {}
                    """).format(
                        sql.SQL(', ').join(map(sql.Identifier, columns)),
                        sql.SQL(', ').join(sql.Placeholder() * len(columns)),
                        sql.SQL(', ').join([
                            sql.SQL('{} = EXCLUDED.{}').format(
                                sql.Identifier(col), sql.Identifier(col)
                            ) for col in columns if col not in ['symbol', 'timestamp']
                        ])
                    )
                    
                    # Execute batch insert
                    data = [tuple(row) for row in df.values]
                    cursor.executemany(insert_sql, data)
                    
                    return len(data)
                    
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise
    
    def get_latest_metrics(self) -> pd.DataFrame:
        """Get most recent stock metrics"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT * FROM stock_metrics
                WHERE timestamp = (SELECT MAX(timestamp) FROM stock_metrics)
                ORDER BY symbol
                """
                
                df = pd.read_sql(query, conn)
                logger.debug(f"Retrieved {len(df)} latest metrics")
                return df
                
        except Exception as e:
            logger.error(f"Failed to get latest metrics: {e}")
            return pd.DataFrame()
    
    def log_regime(self, regime_data: Dict) -> bool:
        """Log regime data with validation"""
        try:
            # Validate regime data
            required_fields = ['regime', 'fear_greed_value']
            for field in required_fields:
                if field not in regime_data:
                    raise ValueError(f"Missing required field: {field}")
            
            with self.transaction() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                    INSERT INTO regime_history 
                    (timestamp, regime, fear_greed_value, vix, strategy, expected_win_rate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (timestamp) 
                    DO UPDATE SET
                        regime = EXCLUDED.regime,
                        fear_greed_value = EXCLUDED.fear_greed_value,
                        vix = EXCLUDED.vix,
                        strategy = EXCLUDED.strategy,
                        expected_win_rate = EXCLUDED.expected_win_rate
                    """, (
                        datetime.now(),
                        regime_data['regime'],
                        regime_data['fear_greed_value'],
                        regime_data.get('vix'),
                        regime_data.get('strategy'),
                        regime_data.get('expected_win_rate')
                    ))
            
            logger.debug(f"Logged regime: {regime_data['regime']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log regime: {e}")
            return False
    
    def insert_tradingagents_analysis(self, analysis_results: List[Dict]) -> int:
        """Insert TradingAgents analysis results with JSON support"""
        if not analysis_results:
            return 0
        
        try:
            with self.transaction() as conn:
                with conn.cursor() as cursor:
                    insert_sql = """
                    INSERT INTO tradingagents_analysis_results (
                        batch_id, symbol, analysis_date, decision, conviction_score,
                        entry_price, target_price, stop_loss, position_size_pct,
                        analysis_summary, fundamental_analysis, technical_analysis,
                        sentiment_analysis, risk_analysis, regime
                    ) VALUES (
                        %(batch_id)s, %(symbol)s, %(analysis_date)s, %(decision)s, 
                        %(conviction_score)s, %(entry_price)s, %(target_price)s, 
                        %(stop_loss)s, %(position_size_pct)s, %(analysis_summary)s,
                        %(fundamental_analysis)s, %(technical_analysis)s,
                        %(sentiment_analysis)s, %(risk_analysis)s, %(regime)s
                    )
                    ON CONFLICT (batch_id, symbol) DO UPDATE SET
                        analysis_date = EXCLUDED.analysis_date,
                        decision = EXCLUDED.decision,
                        conviction_score = EXCLUDED.conviction_score,
                        analysis_summary = EXCLUDED.analysis_summary
                    """
                    
                    cursor.executemany(insert_sql, analysis_results)
                    return len(analysis_results)
                    
        except Exception as e:
            logger.error(f"Failed to insert analysis results: {e}")
            raise
    
    def get_active_positions(self) -> pd.DataFrame:
        """Get active trading positions"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT * FROM position_tracking
                WHERE status = 'OPEN'
                ORDER BY entry_date DESC
                """
                return pd.read_sql(query, conn)
                
        except Exception as e:
            logger.error(f"Failed to get active positions: {e}")
            return pd.DataFrame()
    
    def get_pattern_performance(self, limit: int = 100) -> pd.DataFrame:
        """Get pattern performance statistics"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT * FROM pattern_performance
                WHERE total_trades >= 5
                ORDER BY expectancy DESC, win_rate DESC
                LIMIT %s
                """
                return pd.read_sql(query, conn, params=[limit])
                
        except Exception as e:
            logger.error(f"Failed to get pattern performance: {e}")
            return pd.DataFrame()
    
    def execute_custom_query(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """Execute custom SQL query safely"""
        try:
            with self.get_connection() as conn:
                return pd.read_sql(query, conn, params=params or [])
                
        except Exception as e:
            logger.error(f"Custom query failed: {e}")
            return pd.DataFrame()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get database info
                    cursor.execute("""
                    SELECT 
                        version() as version,
                        current_database() as database,
                        current_user as user,
                        inet_server_addr() as host,
                        inet_server_port() as port
                    """)
                    db_info = dict(cursor.fetchone())
                    
                    # Get pool stats
                    pool_info = {
                        'pool_size': self.pool_size,
                        'active_connections': len(self.connection_pool._used),
                        'available_connections': len(self.connection_pool._pool),
                    }
                    
                    return {
                        'database_info': db_info,
                        'pool_info': pool_info,
                        'connected': True
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {'connected': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        try:
            start_time = datetime.now()
            
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Basic connectivity
                    cursor.execute("SELECT 1 as health_check")
                    health_result = cursor.fetchone()
                    
                    # Table counts
                    cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM stock_metrics) as stock_metrics_count,
                        (SELECT COUNT(*) FROM tradingagents_analysis_results) as analysis_count,
                        (SELECT COUNT(*) FROM position_tracking WHERE status = 'OPEN') as open_positions
                    """)
                    counts = dict(cursor.fetchone())
                    
                    # Recent activity
                    cursor.execute("""
                    SELECT MAX(timestamp) as last_stock_update,
                           MAX(created_at) as last_analysis
                    FROM stock_metrics, tradingagents_analysis_results
                    """)
                    activity = dict(cursor.fetchone())
                    
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'status': 'healthy',
                'latency_ms': latency,
                'table_counts': counts,
                'recent_activity': activity,
                'connection_pool': {
                    'active': len(self.connection_pool._used),
                    'available': len(self.connection_pool._pool)
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def close(self):
        """Close all connections and cleanup"""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                logger.info("PostgreSQL connection pool closed")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Factory function to get appropriate database manager
def get_database_manager(use_postgres: bool = None) -> Union[PostgreSQLManager, 'DatabaseManager']:
    """
    Get appropriate database manager based on environment
    
    Args:
        use_postgres: Force PostgreSQL usage (None = auto-detect)
        
    Returns:
        Database manager instance
    """
    # Auto-detect if not specified
    if use_postgres is None:
        # Use PostgreSQL if DATABASE_URL is set or we're in production
        use_postgres = (
            os.getenv('DATABASE_URL', '').startswith('postgresql://') or
            os.getenv('ENVIRONMENT', 'development') == 'production'
        )
    
    if use_postgres:
        logger.info("Using PostgreSQL database manager")
        return PostgreSQLManager()
    else:
        # Fall back to SQLite manager
        logger.info("Using SQLite database manager")
        from .database_manager import DatabaseManager
        return DatabaseManager()