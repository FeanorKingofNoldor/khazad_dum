"""
Unit tests for InputValidator - security-critical component
"""

import pytest
from decimal import Decimal
from datetime import date
import pandas as pd

from src.security.input_validator import (
    InputValidator,
    ValidationError,
    SecurityViolationError,
    validate_symbol_list,
    validate_price_data
)


class TestInputValidator:
    """Test input validation security and functionality"""
    
    def test_detect_sql_injection(self):
        """Test SQL injection detection"""
        # Clean inputs should pass
        assert InputValidator.detect_injection_attempt("AAPL") is None
        assert InputValidator.detect_injection_attempt("123.45") is None
        
        # SQL injection patterns should be detected
        assert InputValidator.detect_injection_attempt("AAPL'; DROP TABLE users;") is not None
        assert InputValidator.detect_injection_attempt("SELECT * FROM stock_metrics") is not None
        assert InputValidator.detect_injection_attempt("1 OR 1=1") is not None
        assert InputValidator.detect_injection_attempt("1 UNION SELECT") is not None
        
    def test_detect_xss_attempts(self):
        """Test XSS detection"""
        assert InputValidator.detect_injection_attempt("<script>alert('xss')</script>") is not None
        assert InputValidator.detect_injection_attempt("javascript:alert(1)") is not None
        assert InputValidator.detect_injection_attempt("vbscript:msgbox(1)") is not None
        
    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        # Normal string
        result = InputValidator.sanitize_string("AAPL", field_type='symbol')
        assert result == "AAPL"
        
        # String with whitespace
        result = InputValidator.sanitize_string("  MSFT  ", field_type='symbol')
        assert result == "MSFT"
        
        # Empty/None handling
        assert InputValidator.sanitize_string(None) == ""
        assert InputValidator.sanitize_string("") == ""
        
    def test_sanitize_string_security(self):
        """Test string sanitization security"""
        with pytest.raises(SecurityViolationError):
            InputValidator.sanitize_string("AAPL'; DROP TABLE users;")
        
        with pytest.raises(SecurityViolationError):
            InputValidator.sanitize_string("<script>alert('xss')</script>")
        
    def test_validate_symbol_valid(self):
        """Test valid symbol validation"""
        assert InputValidator.validate_symbol("AAPL") == "AAPL"
        assert InputValidator.validate_symbol("MSFT") == "MSFT"
        
    def test_validate_symbol_invalid(self):
        """Test invalid symbol validation"""
        with pytest.raises(ValidationError):
            InputValidator.validate_symbol("")  # Empty
        
        with pytest.raises(ValidationError):
            InputValidator.validate_symbol("TOOLONG")  # Too long
        
    def test_validate_decimal_valid(self):
        """Test valid decimal validation"""
        result = InputValidator.validate_decimal(123.45, 'price')
        assert result == Decimal('123.45')
        
        result = InputValidator.validate_decimal("456.78", 'price')
        assert result == Decimal('456.78')
        
        result = InputValidator.validate_decimal(100, 'price')
        assert result == Decimal('100')
        
    def test_validate_decimal_invalid(self):
        """Test invalid decimal validation"""
        with pytest.raises(ValidationError):
            InputValidator.validate_decimal(None, 'price')
        
        with pytest.raises(ValidationError):
            InputValidator.validate_decimal("abc", 'price')
        
        with pytest.raises(SecurityViolationError):
            InputValidator.validate_decimal("123.45'; DROP TABLE users;", 'price')
        
    def test_validate_decimal_ranges(self):
        """Test decimal range validation"""
        # Valid price range
        result = InputValidator.validate_decimal(50.0, 'price')
        assert result == Decimal('50.0')
        
        # Out of range - too low
        with pytest.raises(ValidationError):
            InputValidator.validate_decimal(0.001, 'price')  # Below $0.01 minimum
        
        # Out of range - too high  
        with pytest.raises(ValidationError):
            InputValidator.validate_decimal(2000000, 'price')  # Above $1M maximum
        
        # RSI range test
        result = InputValidator.validate_decimal(75.5, 'rsi')
        assert result == Decimal('75.5')
        
        with pytest.raises(ValidationError):
            InputValidator.validate_decimal(150, 'rsi')  # Above 100
        
    def test_validate_stock_metrics_valid(self):
        """Test valid stock metrics validation"""
        valid_metrics = {
            'symbol': 'AAPL',
            'price': 150.25,
            'volume': 1000000,
            'market_cap': 2500000000,
            'rsi_2': 45.6,
            'volume_ratio': 1.2,
            'fear_greed_index': 65,
            'regime': 'neutral'
        }
        
        result = InputValidator.validate_stock_metrics(valid_metrics)
        assert result['symbol'] == 'AAPL'
        assert result['price'] == Decimal('150.25')
        assert result['volume'] == 1000000
        
    def test_validate_stock_metrics_missing_required(self):
        """Test stock metrics with missing required fields"""
        invalid_metrics = {
            'price': 150.25,
            'volume': 1000000
            # Missing 'symbol'
        }
        
        with pytest.raises(ValidationError, match="Required field missing: symbol"):
            InputValidator.validate_stock_metrics(invalid_metrics)
        
    def test_validate_stock_metrics_security(self):
        """Test stock metrics security validation"""
        malicious_metrics = {
            'symbol': "AAPL'; DROP TABLE users;",
            'price': 150.25,
            'volume': 1000000
        }
        
        with pytest.raises(SecurityViolationError):
            InputValidator.validate_stock_metrics(malicious_metrics)
        
    def test_validate_trading_decision_valid(self):
        """Test valid trading decision validation"""
        valid_decision = {
            'symbol': 'AAPL',
            'decision': 'BUY',
            'conviction_score': 0.85,
            'entry_price': 150.25,
            'target_price': 165.00,
            'stop_loss': 140.00,
            'position_size_pct': 5.0
        }
        
        result = InputValidator.validate_trading_decision(valid_decision)
        assert result['symbol'] == 'AAPL'
        assert result['decision'] == 'BUY'
        assert result['conviction_score'] == Decimal('0.85')
        
    def test_validate_batch_input(self):
        """Test batch input validation"""
        batch_data = [
            {'symbol': 'AAPL', 'price': 150.25, 'volume': 1000000},
            {'symbol': 'MSFT', 'price': 280.50, 'volume': 500000},
            {'symbol': "EVIL'; DROP TABLE users;", 'price': 100, 'volume': 1000},  # Should be rejected
            {'symbol': 'GOOGL', 'price': 2500.0, 'volume': 200000}
        ]
        
        validated = InputValidator.validate_batch_input(
            batch_data, 
            InputValidator.validate_stock_metrics
        )
        
        # Should have 3 valid records (malicious one filtered out)
        assert len(validated) == 3
        assert all(record['symbol'] in ['AAPL', 'MSFT', 'GOOGL'] for record in validated)


class TestConvenienceFunctions:
    """Test convenience validation functions"""
    
    def test_validate_symbol_list(self):
        """Test symbol list validation"""
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        result = validate_symbol_list(symbols)
        assert result == symbols
        
    def test_validate_price_data(self):
        """Test price data validation convenience function"""
        result = validate_price_data(150.25)
        assert result == Decimal('150.25')
        
        with pytest.raises(ValidationError):
            validate_price_data(-10.0)  # Negative price


class TestSecurityScenarios:
    """Test various security attack scenarios"""
    
    def test_sql_injection_variations(self):
        """Test various SQL injection patterns"""
        injection_attempts = [
            "'; DROP TABLE stock_metrics; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO evil VALUES ('hacked'); --",
        ]
        
        for attempt in injection_attempts:
            with pytest.raises(SecurityViolationError):
                InputValidator.validate_symbol(attempt)
    
    def test_xss_variations(self):
        """Test various XSS patterns"""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(document.cookie)",
            "<iframe src=javascript:alert(1)></iframe>",
            "vbscript:msgbox('xss')"
        ]
        
        for attempt in xss_attempts:
            detected = InputValidator.detect_injection_attempt(attempt)
            assert detected is not None
    
    def test_buffer_overflow_protection(self):
        """Test protection against excessively long inputs"""
        very_long_string = "A" * 100000  # 100KB string
        
        detected = InputValidator.detect_injection_attempt(very_long_string)
        assert "excessive_length" in detected
    
    def test_null_byte_injection(self):
        """Test null byte injection detection"""
        null_byte_attempt = "AAPL\x00.txt"
        
        detected = InputValidator.detect_injection_attempt(null_byte_attempt)
        assert "null_byte" in detected