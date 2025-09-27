"""
Unit tests for DatabaseManager - critical data handling component
"""

import pytest
import pandas as pd
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.data_pipeline.storage.database_manager import DatabaseManager
from src.security.input_validator import ValidationError, SecurityViolationError


@pytest.fixture
def temp_db_path():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        yield tmp.name
    # Cleanup
    Path(tmp.name).unlink(missing_ok=True)

@pytest.fixture
def db_manager(temp_db_path):
    """Create DatabaseManager instance for testing"""
    return DatabaseManager(temp_db_path)


class TestDatabaseManager:
    """Test DatabaseManager functionality and security"""
    
    def test_database_initialization(self, temp_db_path):
        """Test database initialization and schema creation"""
        db = DatabaseManager(temp_db_path)
        
        # Verify database file exists
        assert Path(temp_db_path).exists()
        
        # Verify connection
        assert db.conn is not None
        
        # Verify schema version
        version = db._get_schema_version()
        assert version > 0
        
        # Verify core tables exist
        cursor = db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'schema_version', 'stock_metrics', 'regime_history',
            'tradingagents_analysis_results', 'position_tracking'
        ]
        
        for table in required_tables:
            assert table in tables
        
        db.close()
    
    def test_insert_stock_metrics_valid_data(self, db_manager):
        """Test inserting valid stock metrics"""
        # Create valid test data
        test_data = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT', 'GOOGL'],
            'price': [150.25, 280.50, 2500.0],
            'volume': [1000000, 500000, 200000],
            'market_cap': [2500000000, 2000000000, 1600000000],
            'rsi_2': [45.6, 67.3, 34.8]
        })
        
        rows_inserted = db_manager.insert_stock_metrics(test_data)
        assert rows_inserted == 3
        
        # Verify data was inserted
        latest_metrics = db_manager.get_latest_metrics()
        assert len(latest_metrics) == 3
        assert set(latest_metrics['symbol'].values) == {'AAPL', 'MSFT', 'GOOGL'}
    
    def test_insert_stock_metrics_empty_dataframe(self, db_manager):
        """Test inserting empty DataFrame"""
        empty_df = pd.DataFrame()
        rows_inserted = db_manager.insert_stock_metrics(empty_df)
        assert rows_inserted == 0
    
    def test_insert_stock_metrics_missing_required_columns(self, db_manager):
        """Test inserting data with missing required columns"""
        invalid_data = pd.DataFrame({
            'price': [150.25, 280.50],
            'volume': [1000000, 500000]
            # Missing 'symbol'
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            db_manager.insert_stock_metrics(invalid_data)
    
    def test_insert_stock_metrics_with_security_violations(self, db_manager):
        """Test handling of malicious input data"""
        malicious_data = pd.DataFrame({
            'symbol': ['AAPL', "EVIL'; DROP TABLE stock_metrics; --", 'MSFT'],
            'price': [150.25, 100.0, 280.50],
            'volume': [1000000, 1000, 500000]
        })
        
        # Should filter out malicious records but insert valid ones
        rows_inserted = db_manager.insert_stock_metrics(malicious_data)
        assert rows_inserted == 2  # Only AAPL and MSFT should be inserted
        
        # Verify malicious data was filtered out
        latest_metrics = db_manager.get_latest_metrics()
        symbols = set(latest_metrics['symbol'].values)
        assert 'AAPL' in symbols
        assert 'MSFT' in symbols
        assert "EVIL'; DROP TABLE stock_metrics; --" not in symbols
    
    def test_insert_stock_metrics_with_validation_errors(self, db_manager):
        """Test handling of validation errors"""
        invalid_data = pd.DataFrame({
            'symbol': ['AAPL', 'INVALID_SYMBOL_TOO_LONG', ''],
            'price': [150.25, -100.0, 280.50],  # Negative price should fail
            'volume': [1000000, 1000, 500000]
        })
        
        # Should only insert valid records
        rows_inserted = db_manager.insert_stock_metrics(invalid_data)
        assert rows_inserted == 1  # Only AAPL should pass validation
        
        latest_metrics = db_manager.get_latest_metrics()
        assert len(latest_metrics) == 1
        assert latest_metrics.iloc[0]['symbol'] == 'AAPL'
    
    def test_log_regime_valid(self, db_manager):
        """Test logging valid regime data"""
        regime_data = {
            'regime': 'neutral',
            'fear_greed_value': 50,
            'vix': 20.5,
            'strategy': 'balanced',
            'expected_win_rate': 0.55
        }
        
        result = db_manager.log_regime(regime_data)
        assert result is True
        
        # Verify data was inserted
        cursor = db_manager.conn.execute("SELECT * FROM regime_history ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        assert row is not None
        assert 'neutral' in str(row)
    
    def test_log_regime_missing_required_fields(self, db_manager):
        """Test logging regime data with missing required fields"""
        invalid_regime = {
            'vix': 20.5,
            'strategy': 'balanced'
            # Missing 'regime' and 'fear_greed_value'
        }
        
        result = db_manager.log_regime(invalid_regime)
        assert result is False
    
    def test_get_latest_metrics_no_data(self, db_manager):
        """Test getting latest metrics when no data exists"""
        metrics = db_manager.get_latest_metrics()
        assert metrics.empty
    
    def test_transaction_rollback_on_error(self, db_manager):
        """Test that transactions are rolled back on errors"""
        # Insert some initial data
        valid_data = pd.DataFrame({
            'symbol': ['AAPL'],
            'price': [150.25],
            'volume': [1000000]
        })
        db_manager.insert_stock_metrics(valid_data)
        
        initial_count = len(db_manager.get_latest_metrics())
        
        # Try to insert data that will cause an error during transaction
        with patch.object(db_manager.conn, 'commit', side_effect=sqlite3.Error("Simulated error")):
            with pytest.raises(sqlite3.Error):
                db_manager.insert_stock_metrics(valid_data)
        
        # Verify data wasn't partially inserted due to rollback
        final_count = len(db_manager.get_latest_metrics())
        assert final_count == initial_count
    
    def test_context_manager_usage(self, temp_db_path):
        """Test DatabaseManager as context manager"""
        with DatabaseManager(temp_db_path) as db:
            assert db.conn is not None
            
            # Use database
            test_data = pd.DataFrame({
                'symbol': ['AAPL'],
                'price': [150.25],
                'volume': [1000000]
            })
            rows_inserted = db.insert_stock_metrics(test_data)
            assert rows_inserted == 1
        
        # Connection should be closed after context exit
        assert db.conn is None
    
    def test_schema_version_tracking(self, db_manager):
        """Test schema version is properly tracked"""
        version = db_manager._get_schema_version()
        assert isinstance(version, int)
        assert version > 0
        
        # Verify version record exists
        cursor = db_manager.conn.execute("SELECT * FROM schema_version")
        versions = cursor.fetchall()
        assert len(versions) > 0
    
    def test_connection_info(self, db_manager):
        """Test getting connection information"""
        info = db_manager.get_connection_info()
        
        assert 'database_path' in info
        assert 'connected' in info
        assert 'schema_version' in info
        assert info['connected'] is True
        
        # Close and test again
        db_manager.close()
        info = db_manager.get_connection_info()
        assert info['connected'] is False
    
    def test_sql_injection_prevention(self, db_manager):
        """Test that SQL injection attacks are prevented"""
        # Try various SQL injection patterns
        malicious_symbols = [
            "'; DROP TABLE stock_metrics; --",
            "' OR 1=1; --",
            "'; INSERT INTO evil VALUES ('hacked'); --"
        ]
        
        for malicious_symbol in malicious_symbols:
            malicious_data = pd.DataFrame({
                'symbol': [malicious_symbol],
                'price': [150.25],
                'volume': [1000000]
            })
            
            # Should not raise database errors, should filter out malicious data
            rows_inserted = db_manager.insert_stock_metrics(malicious_data)
            assert rows_inserted == 0  # No malicious data should be inserted
        
        # Verify database structure is intact
        cursor = db_manager.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'stock_metrics' in tables  # Table should still exist
    
    def test_concurrent_access_simulation(self, db_manager):
        """Test behavior under simulated concurrent access"""
        # Simulate concurrent writes
        data_batches = [
            pd.DataFrame({
                'symbol': [f'SYM{i}'],
                'price': [100.0 + i],
                'volume': [1000000 + i * 1000]
            })
            for i in range(10)
        ]
        
        total_inserted = 0
        for batch in data_batches:
            rows_inserted = db_manager.insert_stock_metrics(batch)
            total_inserted += rows_inserted
        
        assert total_inserted == 10
        
        # Verify all data was inserted correctly
        latest_metrics = db_manager.get_latest_metrics()
        assert len(latest_metrics) == 10
        
        # Verify data integrity
        symbols = sorted(latest_metrics['symbol'].values)
        expected_symbols = sorted([f'SYM{i}' for i in range(10)])
        assert symbols == expected_symbols


class TestDatabaseManagerErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_database_path(self):
        """Test handling of invalid database paths"""
        # Try to create database in non-existent directory
        invalid_path = "/non/existent/directory/test.db"
        
        with pytest.raises(Exception):  # Should raise some kind of error
            DatabaseManager(invalid_path)
    
    def test_database_corruption_handling(self, temp_db_path):
        """Test handling of database corruption"""
        # Create a valid database first
        db = DatabaseManager(temp_db_path)
        db.close()
        
        # Corrupt the database file
        with open(temp_db_path, 'wb') as f:
            f.write(b"CORRUPTED DATABASE FILE")
        
        # Try to open corrupted database
        with pytest.raises(Exception):  # Should raise database error
            DatabaseManager(temp_db_path)
    
    def test_disk_space_simulation(self, temp_db_path):
        """Test behavior when disk space is limited"""
        db = DatabaseManager(temp_db_path)
        
        # Create very large data to simulate disk space issues
        large_data = pd.DataFrame({
            'symbol': ['AAPL'] * 1000,
            'price': [150.25] * 1000,
            'volume': [1000000] * 1000,
            'analysis_summary': ['X' * 1000] * 1000  # Large text field
        })
        
        # Should handle gracefully (may succeed or fail, but shouldn't crash)
        try:
            rows_inserted = db.insert_stock_metrics(large_data)
            # If it succeeds, verify some reasonable number was inserted
            assert rows_inserted >= 0
        except Exception as e:
            # If it fails, should be a controlled failure
            assert isinstance(e, (sqlite3.Error, OSError, IOError))
        
        db.close()


class TestDatabaseSecurity:
    """Test security-specific database behaviors"""
    
    def test_parameterized_queries(self, db_manager):
        """Test that parameterized queries are used to prevent injection"""
        # This test verifies our implementation uses parameterized queries
        # by checking that malicious input doesn't execute as SQL
        
        malicious_regime = {
            'regime': "'; DROP TABLE stock_metrics; --",
            'fear_greed_value': 50
        }
        
        # Should not crash or execute malicious SQL
        result = db_manager.log_regime(malicious_regime)
        # Depending on validation, this might succeed or fail, but shouldn't crash
        assert isinstance(result, bool)
        
        # Verify table still exists
        cursor = db_manager.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_metrics'")
        table_exists = cursor.fetchone() is not None
        assert table_exists
    
    def test_privilege_separation(self, db_manager):
        """Test that database operations have appropriate privileges"""
        # SQLite doesn't have user privileges, but we can test connection properties
        
        # Verify foreign keys are enabled (security best practice)
        cursor = db_manager.conn.execute("PRAGMA foreign_keys")
        foreign_keys_enabled = cursor.fetchone()[0]
        assert foreign_keys_enabled == 1
        
        # Verify WAL mode or similar optimizations don't compromise security
        cursor = db_manager.conn.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        # WAL mode is acceptable, DELETE mode is also fine
        assert journal_mode.upper() in ['DELETE', 'WAL', 'TRUNCATE']
    
    def test_data_sanitization_during_insert(self, db_manager):
        """Test that data is properly sanitized during database operations"""
        # Test various malicious payloads
        test_cases = [
            {
                'symbol': 'AAPL<script>alert(1)</script>',  # XSS attempt
                'price': 150.25,
                'volume': 1000000
            },
            {
                'symbol': 'MSFT\x00hidden',  # Null byte injection
                'price': 280.50,
                'volume': 500000
            },
            {
                'symbol': 'GOOGL../../../etc/passwd',  # Path traversal
                'price': 2500.0,
                'volume': 200000
            }
        ]
        
        for test_case in test_cases:
            test_df = pd.DataFrame([test_case])
            
            # Should either sanitize or reject the data
            rows_inserted = db_manager.insert_stock_metrics(test_df)
            
            if rows_inserted > 0:
                # If data was inserted, verify it was sanitized
                latest_metrics = db_manager.get_latest_metrics()
                inserted_symbol = latest_metrics.iloc[-1]['symbol']
                
                # Should not contain malicious content
                assert '<script>' not in inserted_symbol
                assert '\x00' not in inserted_symbol
                assert '../' not in inserted_symbol