"""
██╗  ██╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗
██║ ██╔╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║
█████╔╝ ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║
██╔═██╗ ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║
██║  ██╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝

🏔️ ALGORITHMIC TRADING SYSTEM - "They delved too greedily and too deep..."

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 MODULE: Security & Input Validation                                          │
│ 📄 FILE: input_validator.py                                                     │
│ 📅 CREATED: 2024-12-21                                                             │
│ 👑 AUTHOR: FeanorKingofNoldor                                                      │
│ 🔗 REPOSITORY: https://github.com/FeanorKingofNoldor/khazad_dum                   │
│ 📧 CONTACT: [Your Contact Info]                                                    │
│                                                                                     │
│ 🎯 PURPOSE:                                                                        │
│ Comprehensive input validation & sanitization to prevent injection attacks         │
│                                                                                     │
│ 🔧 DEPENDENCIES:                                                                   │
│ - bleach (HTML/XSS sanitization)                                                   │
│ - decimal (precise numeric validation)                                             │
│ - regex patterns for injection detection                                           │
│ - structured logging for security events                                           │
│                                                                                     │
│ 📈 TRADING PIPELINE STAGE: Security Layer (All Stages)                          │
│ └── 1. Market Regime Detection                                                     │
│ └── 2. Stock Screening                                                             │
│ └── 3. AI Analysis (TradingAgents)                                                 │
│ └── 4. Pattern Recognition                                                         │
│ └── 5. Portfolio Construction                                                      │
│ └── 6. Performance Observation                                                     │
│                                                                                     │
│ ⚠️  CRITICAL NOTES:                                                                │
│ - ALL external inputs MUST pass through validation                                │
│ - Security violations are logged and blocked immediately                           │
│ - Uses both pattern matching and content sanitization                             │
│                                                                                     │
│ 📊 PERFORMANCE NOTES:                                                              │
│ - Input validation: ~1-5ms per validation call                                   │
│ - Regex pattern matching optimized for speed                                      │
│ - Sanitization preserves data integrity while ensuring security                   │
│                                                                                     │
│ 🧪 TESTING:                                                                        │
│ - Unit Tests: tests/unit/test_input_validator.py                                  │
│ - Security Tests: tests/security/test_injection_prevention.py                    │
│                                                                                     │
│ 📚 DOCUMENTATION:                                                                  │
│ - API Docs: Auto-generated from docstrings                                        │
│ - Security Guide: docs/guides/SECURITY_VALIDATION.md                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

Licensed under MIT License - See LICENSE file for details
Copyright (c) 2024 FeanorKingofNoldor

"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare..."
"""

import re
import logging
from typing import Any, Dict, List, Union, Optional, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import bleach
from config.logging.logging_config import log_security_event

logger = logging.getLogger('security.input_validator')


class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass


class SecurityViolationError(Exception):
    """Custom exception for potential security violations"""
    pass


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # SQL injection and XSS patterns
    SQL_INJECTION_PATTERNS = [
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT|JAVASCRIPT)\b',
        r'[;\'\"]',  # SQL terminators and quotes
        r'--',      # SQL comments
        r'/\*.*?\*/',  # SQL block comments
        r'\bOR\s+\d+\s*=\s*\d+',  # Classic OR 1=1 injection
        r'\bAND\s+\d+\s*=\s*\d+', # Classic AND 1=1 injection
        r'<script[^>]*>',  # XSS scripts (opening tag)
        r'</script>',      # XSS scripts (closing tag)
        r'javascript:',    # JavaScript execution
        r'vbscript:',      # VBScript execution
        r'<img[^>]+onerror[^>]*>',  # Image XSS
        r'<iframe[^>]*>',  # Iframe injection
        r'alert\s*\(',     # Alert function calls
        r'eval\s*\(',      # Eval function calls
    ]
    
    # Allowed characters for different input types  
    SYMBOL_PATTERN = re.compile(r'^[A-Z][A-Z0-9]{0,4}$')  # Stock symbols (start with letter, can contain numbers)
    DECIMAL_PATTERN = re.compile(r'^\d+\.?\d*$')  # Decimal numbers
    INTEGER_PATTERN = re.compile(r'^\d+$')        # Integers
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # YYYY-MM-DD
    
    # Maximum string lengths
    MAX_STRING_LENGTHS = {
        'symbol': 10,
        'regime': 50,
        'pattern_id': 100,
        'batch_id': 100,
        'decision': 50,
        'exit_reason': 100,
        'analysis_summary': 10000,  # Longer for analysis text
        'general_string': 1000
    }
    
    # Numeric ranges
    NUMERIC_RANGES = {
        'price': (0.01, 1000000),      # $0.01 to $1M
        'percentage': (-100, 100),      # -100% to +100%
        'volume': (0, 1000000000),      # 0 to 1B shares
        'quantity': (1, 1000000),       # 1 to 1M shares
        'market_cap': (1000000, 10000000000000),  # $1M to $10T
        'rsi': (0, 100),               # RSI range
        'fear_greed': (0, 100),        # Fear & Greed index
        'conviction': (0, 1),          # Conviction score
        'position_size_pct': (0, 100), # Position size percentage
    }
    
    @classmethod
    def detect_injection_attempt(cls, input_value: str) -> Optional[str]:
        """
        Detect potential injection attacks in input
        Returns attack type if detected, None if clean
        """
        if not isinstance(input_value, str):
            return None
        
        input_lower = input_value.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return f"potential_injection_pattern: {pattern}"
        
        # Check for excessive length (potential buffer overflow)
        if len(input_value) > 50000:
            return "excessive_length_attack"
        
        # Check for null bytes
        if '\x00' in input_value:
            return "null_byte_injection"
        
        # Check for path traversal
        if '../' in input_value or '..\\' in input_value:
            return "path_traversal_attempt"
        
        return None
    
    @classmethod
    def sanitize_string(cls, value: Any, max_length: int = None, field_type: str = 'general_string') -> str:
        """
        Sanitize string input with security checks
        """
        if value is None:
            return ""
        
        # Convert to string if not already
        str_value = str(value).strip()
        
        # Check for injection attempts
        injection_type = cls.detect_injection_attempt(str_value)
        if injection_type:
            log_security_event(
                'input_validation_violation',
                f"Potential injection detected in {field_type}: {injection_type}",
                {'input_sample': str_value[:100], 'injection_type': injection_type}
            )
            raise SecurityViolationError(f"Security violation detected: {injection_type}")
        
        # Use bleach to clean HTML/JS
        cleaned = bleach.clean(str_value, tags=[], strip=True)
        
        # Apply length limits
        max_len = max_length or cls.MAX_STRING_LENGTHS.get(field_type, cls.MAX_STRING_LENGTHS['general_string'])
        if len(cleaned) > max_len:
            logger.warning(f"String truncated from {len(cleaned)} to {max_len} characters")
            cleaned = cleaned[:max_len]
        
        return cleaned
    
    @classmethod
    def validate_symbol(cls, symbol: Any) -> str:
        """Validate stock symbol format"""
        if not symbol:
            raise ValidationError("Symbol cannot be empty")
        
        cleaned_symbol = cls.sanitize_string(symbol, field_type='symbol')
        
        if not cls.SYMBOL_PATTERN.match(cleaned_symbol):
            raise ValidationError(f"Invalid symbol format: {cleaned_symbol}")
        
        return cleaned_symbol
    
    @classmethod
    def validate_decimal(cls, value: Any, field_name: str) -> Decimal:
        """Validate and convert decimal values"""
        if value is None:
            raise ValidationError(f"{field_name} cannot be None")
        
        try:
            # Handle string inputs
            if isinstance(value, str):
                # Check for injection first
                injection_type = cls.detect_injection_attempt(value)
                if injection_type:
                    raise SecurityViolationError(f"Security violation in {field_name}: {injection_type}")
                
                # Validate format
                if not cls.DECIMAL_PATTERN.match(value.strip()):
                    raise ValidationError(f"Invalid decimal format for {field_name}: {value}")
            
            decimal_value = Decimal(str(value))
            
            # Check ranges if defined
            if field_name in cls.NUMERIC_RANGES:
                min_val, max_val = cls.NUMERIC_RANGES[field_name]
                if not (min_val <= float(decimal_value) <= max_val):
                    raise ValidationError(
                        f"{field_name} value {decimal_value} outside valid range [{min_val}, {max_val}]"
                    )
            
            return decimal_value
            
        except InvalidOperation:
            raise ValidationError(f"Cannot convert {field_name} to decimal: {value}")
    
    @classmethod
    def validate_integer(cls, value: Any, field_name: str, allow_zero: bool = True) -> int:
        """Validate integer values"""
        if value is None:
            raise ValidationError(f"{field_name} cannot be None")
        
        try:
            # Handle string inputs
            if isinstance(value, str):
                injection_type = cls.detect_injection_attempt(value)
                if injection_type:
                    raise SecurityViolationError(f"Security violation in {field_name}: {injection_type}")
                
                if not cls.INTEGER_PATTERN.match(value.strip()):
                    raise ValidationError(f"Invalid integer format for {field_name}: {value}")
            
            int_value = int(value)
            
            if not allow_zero and int_value == 0:
                raise ValidationError(f"{field_name} cannot be zero")
            
            if int_value < 0:
                raise ValidationError(f"{field_name} cannot be negative: {int_value}")
            
            # Check ranges if defined
            if field_name in cls.NUMERIC_RANGES:
                min_val, max_val = cls.NUMERIC_RANGES[field_name]
                if not (min_val <= int_value <= max_val):
                    raise ValidationError(
                        f"{field_name} value {int_value} outside valid range [{min_val}, {max_val}]"
                    )
            
            return int_value
            
        except ValueError:
            raise ValidationError(f"Cannot convert {field_name} to integer: {value}")
    
    @classmethod
    def validate_date(cls, value: Any, field_name: str) -> date:
        """Validate date values"""
        if value is None:
            raise ValidationError(f"{field_name} cannot be None")
        
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            # Security check
            injection_type = cls.detect_injection_attempt(value)
            if injection_type:
                raise SecurityViolationError(f"Security violation in {field_name}: {injection_type}")
            
            # Format check
            if not cls.DATE_PATTERN.match(value.strip()):
                raise ValidationError(f"Invalid date format for {field_name}. Expected YYYY-MM-DD: {value}")
            
            try:
                return datetime.strptime(value.strip(), '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(f"Invalid date value for {field_name}: {value}")
        
        raise ValidationError(f"Unsupported date type for {field_name}: {type(value)}")
    
    @classmethod
    def validate_stock_metrics(cls, metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete stock metrics dictionary"""
        validated = {}
        
        # Required fields
        required_fields = ['symbol', 'price', 'volume']
        for field in required_fields:
            if field not in metrics_dict:
                raise ValidationError(f"Required field missing: {field}")
        
        # Validate each field
        try:
            validated['symbol'] = cls.validate_symbol(metrics_dict['symbol'])
            validated['price'] = cls.validate_decimal(metrics_dict['price'], 'price')
            validated['volume'] = cls.validate_integer(metrics_dict['volume'], 'volume')
            
            # Optional fields
            if 'market_cap' in metrics_dict:
                validated['market_cap'] = cls.validate_integer(metrics_dict['market_cap'], 'market_cap')
            
            if 'rsi_2' in metrics_dict:
                validated['rsi_2'] = cls.validate_decimal(metrics_dict['rsi_2'], 'rsi')
            
            if 'rsi_14' in metrics_dict:
                validated['rsi_14'] = cls.validate_decimal(metrics_dict['rsi_14'], 'rsi')
            
            if 'volume_ratio' in metrics_dict:
                validated['volume_ratio'] = cls.validate_decimal(metrics_dict['volume_ratio'], 'percentage')
            
            if 'price_change_pct' in metrics_dict:
                validated['price_change_pct'] = cls.validate_decimal(metrics_dict['price_change_pct'], 'percentage')
            
            if 'fear_greed_index' in metrics_dict:
                validated['fear_greed_index'] = cls.validate_integer(metrics_dict['fear_greed_index'], 'fear_greed')
            
            if 'regime' in metrics_dict:
                validated['regime'] = cls.sanitize_string(metrics_dict['regime'], field_type='regime')
            
            return validated
            
        except (ValidationError, SecurityViolationError) as e:
            logger.error(f"Validation failed for stock metrics {metrics_dict.get('symbol', 'unknown')}: {e}")
            raise
    
    @classmethod
    def validate_trading_decision(cls, decision_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trading decision dictionary"""
        validated = {}
        
        # Required fields
        required_fields = ['symbol', 'decision']
        for field in required_fields:
            if field not in decision_dict:
                raise ValidationError(f"Required field missing: {field}")
        
        try:
            validated['symbol'] = cls.validate_symbol(decision_dict['symbol'])
            
            # Validate decision type
            decision = cls.sanitize_string(decision_dict['decision'], field_type='decision')
            allowed_decisions = ['BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL']
            if decision not in allowed_decisions:
                raise ValidationError(f"Invalid decision: {decision}. Must be one of {allowed_decisions}")
            validated['decision'] = decision
            
            # Optional fields with validation
            if 'conviction_score' in decision_dict:
                validated['conviction_score'] = cls.validate_decimal(decision_dict['conviction_score'], 'conviction')
            
            if 'entry_price' in decision_dict:
                validated['entry_price'] = cls.validate_decimal(decision_dict['entry_price'], 'price')
            
            if 'target_price' in decision_dict:
                validated['target_price'] = cls.validate_decimal(decision_dict['target_price'], 'price')
            
            if 'stop_loss' in decision_dict:
                validated['stop_loss'] = cls.validate_decimal(decision_dict['stop_loss'], 'price')
            
            if 'position_size_pct' in decision_dict:
                validated['position_size_pct'] = cls.validate_decimal(decision_dict['position_size_pct'], 'position_size_pct')
            
            if 'analysis_date' in decision_dict:
                validated['analysis_date'] = cls.validate_date(decision_dict['analysis_date'], 'analysis_date')
            
            if 'batch_id' in decision_dict:
                validated['batch_id'] = cls.sanitize_string(decision_dict['batch_id'], field_type='batch_id')
            
            if 'analysis_summary' in decision_dict:
                validated['analysis_summary'] = cls.sanitize_string(decision_dict['analysis_summary'], field_type='analysis_summary')
            
            return validated
            
        except (ValidationError, SecurityViolationError) as e:
            logger.error(f"Validation failed for trading decision {decision_dict.get('symbol', 'unknown')}: {e}")
            raise
    
    @classmethod
    def validate_position_data(cls, position_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate position tracking data"""
        validated = {}
        
        # Required fields
        required_fields = ['symbol', 'entry_price', 'quantity', 'position_size_dollars']
        for field in required_fields:
            if field not in position_dict:
                raise ValidationError(f"Required field missing: {field}")
        
        try:
            validated['symbol'] = cls.validate_symbol(position_dict['symbol'])
            validated['entry_price'] = cls.validate_decimal(position_dict['entry_price'], 'price')
            validated['quantity'] = cls.validate_integer(position_dict['quantity'], 'quantity', allow_zero=False)
            validated['position_size_dollars'] = cls.validate_decimal(position_dict['position_size_dollars'], 'price')
            
            # Optional fields
            if 'exit_price' in position_dict and position_dict['exit_price'] is not None:
                validated['exit_price'] = cls.validate_decimal(position_dict['exit_price'], 'price')
            
            if 'stop_loss' in position_dict and position_dict['stop_loss'] is not None:
                validated['stop_loss'] = cls.validate_decimal(position_dict['stop_loss'], 'price')
            
            if 'target_price' in position_dict and position_dict['target_price'] is not None:
                validated['target_price'] = cls.validate_decimal(position_dict['target_price'], 'price')
            
            if 'entry_date' in position_dict:
                validated['entry_date'] = cls.validate_date(position_dict['entry_date'], 'entry_date')
            
            if 'exit_date' in position_dict and position_dict['exit_date'] is not None:
                validated['exit_date'] = cls.validate_date(position_dict['exit_date'], 'exit_date')
            
            if 'pnl_dollars' in position_dict and position_dict['pnl_dollars'] is not None:
                validated['pnl_dollars'] = cls.validate_decimal(position_dict['pnl_dollars'], 'price')
            
            if 'pnl_pct' in position_dict and position_dict['pnl_pct'] is not None:
                validated['pnl_pct'] = cls.validate_decimal(position_dict['pnl_pct'], 'percentage')
            
            if 'exit_reason' in position_dict:
                validated['exit_reason'] = cls.sanitize_string(position_dict['exit_reason'], field_type='exit_reason')
            
            # Validate status
            if 'status' in position_dict:
                status = cls.sanitize_string(position_dict['status'], field_type='decision')
                allowed_statuses = ['OPEN', 'CLOSED', 'CANCELLED']
                if status not in allowed_statuses:
                    raise ValidationError(f"Invalid status: {status}. Must be one of {allowed_statuses}")
                validated['status'] = status
            
            return validated
            
        except (ValidationError, SecurityViolationError) as e:
            logger.error(f"Validation failed for position data {position_dict.get('symbol', 'unknown')}: {e}")
            raise
    
    @classmethod
    def validate_batch_input(cls, input_list: List[Dict[str, Any]], validator_func) -> List[Dict[str, Any]]:
        """Validate a batch of input records"""
        validated_records = []
        errors = []
        
        for i, record in enumerate(input_list):
            try:
                validated_record = validator_func(record)
                validated_records.append(validated_record)
            except (ValidationError, SecurityViolationError) as e:
                error_msg = f"Record {i}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        if errors:
            # Log security events if we found violations
            for error in errors:
                if 'security violation' in error.lower():
                    log_security_event(
                        'batch_validation_security_violation',
                        f"Security violations in batch validation: {len([e for e in errors if 'security' in e.lower()])} violations",
                        {'total_errors': len(errors), 'batch_size': len(input_list)}
                    )
        
        # Return validated records even if some failed
        # Let caller decide whether to proceed with partial data
        return validated_records


# Convenience functions for common validations
def validate_symbol_list(symbols: List[str]) -> List[str]:
    """Validate a list of stock symbols"""
    return [InputValidator.validate_symbol(symbol) for symbol in symbols]


def validate_price_data(price: Any, field_name: str = 'price') -> Decimal:
    """Validate price data with standard checks"""
    return InputValidator.validate_decimal(price, field_name)


def validate_user_input(user_input: str, max_length: int = 1000) -> str:
    """Validate general user input with security checks"""
    return InputValidator.sanitize_string(user_input, max_length=max_length)


# Security audit function
def audit_input_validation(record_count: int, validation_errors: int, security_violations: int):
    """Log input validation audit information"""
    log_security_event(
        'input_validation_audit',
        f"Input validation audit: {record_count} records, {validation_errors} errors, {security_violations} security violations",
        {
            'record_count': record_count,
            'validation_errors': validation_errors,
            'security_violations': security_violations,
            'error_rate': validation_errors / record_count if record_count > 0 else 0,
            'security_violation_rate': security_violations / record_count if record_count > 0 else 0
        }
    )