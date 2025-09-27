# KHAZAD_DUM Documentation Standards

> **📝 Comprehensive guide for inline documentation, headers, and docstring standards**

## 🎯 Overview

This document defines the documentation standards for KHAZAD_DUM to ensure:
- **Consistent code documentation** across all modules
- **Automatic API documentation** generation via Sphinx
- **Professional presentation** with proper attribution
- **Easy maintenance** and onboarding for developers

---

## 🏷️ File Headers

Every Python file must include the standard KHAZAD_DUM header. Use this template:

```python
#!/usr/bin/env python3
"""
███████╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗
██╔════╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║
██║     ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║
██║     ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║
╚██████╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝

🏔️ ALGORITHMIC TRADING SYSTEM - "They delved too greedily and too deep..."

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 MODULE: [YOUR_MODULE_NAME]                                                       │
│ 📄 FILE: [YOUR_FILE_NAME].py                                                       │
│ 📅 CREATED: [DATE]                                                                 │
│ 👑 AUTHOR: FeanorKingofNoldor                                                      │
│ 🔗 REPOSITORY: https://github.com/FeanorKingofNoldor/khazad_dum                   │
│ 📧 CONTACT: [Your Contact Info]                                                    │
│                                                                                     │
│ 🎯 PURPOSE:                                                                        │
│ [Brief description of what this file does]                                         │
│                                                                                     │
│ 🔧 DEPENDENCIES:                                                                   │
│ - [List key dependencies]                                                          │
│                                                                                     │
│ 📈 TRADING PIPELINE STAGE: [Which stage this belongs to]                          │
│ └── 1. Market Regime Detection                                                     │
│ └── 2. Stock Screening                                                             │
│ └── 3. AI Analysis (TradingAgents)                                                 │
│ └── 4. Pattern Recognition                                                         │
│ └── 5. Portfolio Construction                                                      │
│ └── 6. Performance Observation                                                     │
│                                                                                     │
│ ⚠️  CRITICAL NOTES:                                                                │
│ - [Any important warnings or considerations]                                       │
│                                                                                     │
│ 📊 PERFORMANCE NOTES:                                                              │
│ - [Performance considerations, if any]                                             │
│                                                                                     │
│ 🧪 TESTING:                                                                        │
│ - Unit Tests: tests/unit/test_[module_name].py                                     │
│ - Integration Tests: tests/integration/test_[module_name]_integration.py           │
│                                                                                     │
│ 📚 DOCUMENTATION:                                                                  │
│ - API Docs: Auto-generated from docstrings                                        │
│ - Usage Guide: docs/guides/[MODULE_NAME]_USAGE.md                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

Licensed under MIT License - See LICENSE file for details
Copyright (c) 2024 FeanorKingofNoldor

"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare..."
"""
```

### Header Fields to Customize:
- `[YOUR_MODULE_NAME]`: e.g., "Market Analysis", "Pattern Recognition"
- `[YOUR_FILE_NAME]`: e.g., "regime_detector", "pattern_classifier"  
- `[DATE]`: Creation date in YYYY-MM-DD format
- `[Your Contact Info]`: Your preferred contact method
- `🎯 PURPOSE`: 1-2 sentence description of the file's purpose
- `🔧 DEPENDENCIES`: Key external dependencies
- `📈 TRADING PIPELINE STAGE`: Which of the 6 stages this belongs to
- `⚠️ CRITICAL NOTES`: Important warnings or considerations
- `📊 PERFORMANCE NOTES`: Any performance considerations

---

## 📖 Docstring Standards

KHAZAD_DUM uses **Google-style docstrings** for all classes, functions, and modules.

### Module Docstrings

```python
"""
Market regime detection using CNN Fear & Greed Index.

This module implements the first stage of the KHAZAD_DUM trading pipeline,
classifying market conditions based on sentiment indicators to inform
subsequent trading decisions.

The regime detector classifies markets into 5 categories:
- Extreme Fear (0-25): Aggressive buying opportunity
- Fear (25-45): Moderate buying opportunity  
- Neutral (45-55): Standard position sizing
- Greed (55-75): Reduced position sizing
- Extreme Greed (75-100): Minimal exposure

Example:
    >>> from src.core.market_analysis.regime_detector import RegimeDetector
    >>> detector = RegimeDetector()
    >>> current_regime = detector.get_current_regime()
    >>> print(f"Market regime: {current_regime}")

Attributes:
    CNN_FEED_URL (str): URL for CNN Fear & Greed Index data
    REGIME_THRESHOLDS (Dict[str, int]): Numerical thresholds for regime classification
    
Note:
    This module requires an active internet connection to fetch the CNN F&G Index.
    Cached values are used as fallback when the feed is unavailable.
    
Warning:
    Market regime classification is a simplification of complex market conditions.
    Always combine with other analysis methods for trading decisions.
"""
```

### Class Docstrings

```python
class RegimeDetector:
    """
    Detect and classify market regimes using sentiment indicators.
    
    The RegimeDetector analyzes market sentiment data to classify the current
    market environment into one of five distinct regimes. This classification
    drives position sizing and risk management decisions throughout the
    KHAZAD_DUM trading pipeline.
    
    Attributes:
        config (Dict[str, Any]): Configuration parameters for regime detection
        cache_timeout (int): Seconds to cache regime data (default: 300)
        last_update (datetime): Timestamp of last regime update
        current_regime (str): Most recently detected regime
        confidence_score (float): Confidence in current regime classification
        
    Example:
        >>> detector = RegimeDetector(config={'cache_timeout': 600})
        >>> regime = detector.get_current_regime()
        >>> if regime == 'extreme_fear':
        ...     print("Market in extreme fear - consider aggressive buying")
        
    Note:
        The detector automatically handles caching and error recovery.
        Failed API calls fall back to cached data or neutral regime.
        
    Warning:
        Regime changes can be rapid during volatile market conditions.
        Consider the confidence_score when making trading decisions.
    """
```

### Function Docstrings

```python
def get_current_regime(self, 
                      use_cache: bool = True,
                      timeout: Optional[int] = None) -> str:
    """
    Get the current market regime classification.
    
    Fetches the latest CNN Fear & Greed Index and classifies the current
    market environment into one of five predefined regimes. Results are
    cached to minimize API calls and improve performance.
    
    Args:
        use_cache (bool, optional): Whether to use cached regime data when
            available. Improves performance but may use slightly stale data.
            Defaults to True.
        timeout (Optional[int], optional): Timeout in seconds for API calls.
            If None, uses the instance's configured timeout. Must be positive
            integer. Defaults to None.
            
    Returns:
        str: Current market regime classification. One of:
            - 'extreme_fear': F&G Index 0-25, aggressive buying opportunity
            - 'fear': F&G Index 25-45, moderate buying opportunity
            - 'neutral': F&G Index 45-55, standard position sizing
            - 'greed': F&G Index 55-75, reduced position sizing  
            - 'extreme_greed': F&G Index 75-100, minimal exposure
            
    Raises:
        ConnectionError: If unable to connect to CNN API and no cached data available
        ValueError: If timeout parameter is negative or zero
        RegimeDetectionError: If unable to parse Fear & Greed Index data
        
    Example:
        >>> detector = RegimeDetector()
        >>> regime = detector.get_current_regime(use_cache=False, timeout=30)
        >>> print(f"Current market regime: {regime}")
        Current market regime: fear
        
        >>> # Get regime with caching (faster)
        >>> cached_regime = detector.get_current_regime()
        >>> print(f"Cached regime: {cached_regime}")
        Cached regime: fear
        
    Note:
        This method is thread-safe and can be called concurrently.
        Cache expiration is handled automatically based on cache_timeout.
        
    Performance:
        - With cache: ~1ms response time
        - Without cache: ~200-500ms (network dependent)
        - Recommended to use caching for frequent calls
        
    See Also:
        get_regime_confidence(): Get confidence score for current regime
        get_regime_history(): Get historical regime data
    """
```

### Property Docstrings

```python
@property
def confidence_score(self) -> float:
    """
    Confidence score for the current regime classification.
    
    Returns a value between 0.0 and 1.0 indicating how confident the
    regime detector is in the current classification. Higher values
    indicate more reliable regime detection.
    
    Returns:
        float: Confidence score between 0.0 (no confidence) and 1.0 (maximum confidence)
        
    Note:
        Confidence scores below 0.7 suggest regime transitions or unclear conditions.
        Consider using neutral regime assumptions when confidence is low.
    """
```

### Private Method Docstrings

```python
def _parse_cnn_data(self, raw_data: str) -> Dict[str, Any]:
    """
    Parse raw CNN Fear & Greed Index HTML data.
    
    Internal method that extracts the numerical Fear & Greed Index value
    and associated metadata from the CNN website HTML response.
    
    Args:
        raw_data (str): Raw HTML response from CNN F&G Index page
        
    Returns:
        Dict[str, Any]: Parsed data containing:
            - 'index_value': Numerical F&G Index (0-100)
            - 'classification': Text classification from CNN
            - 'timestamp': Data timestamp
            - 'previous_value': Previous index value
            
    Raises:
        ValueError: If HTML parsing fails or required data not found
    """
```

---

## 🔧 Type Annotations

All functions must include comprehensive type hints:

```python
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from datetime import datetime
import pandas as pd

def process_market_data(
    symbols: List[str],
    start_date: datetime,
    end_date: Optional[datetime] = None,
    config: Dict[str, Any] = None,
    callback: Optional[Callable[[str], None]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Process market data with comprehensive type annotations."""
```

### Common Type Patterns

```python
# Basic types
symbol: str
price: float
volume: int
is_valid: bool

# Collections
symbols: List[str]
prices: Dict[str, float]
config: Dict[str, Any]
optional_data: Optional[List[str]]

# Union types
price_or_none: Union[float, None]  # or Optional[float]
numeric_value: Union[int, float]

# Complex types
market_data: pd.DataFrame
callback: Callable[[str], bool]
date_range: Tuple[datetime, datetime]

# Custom types (define at module level)
MarketRegime = Literal['extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed']
PatternType = Literal['reversal', 'breakout', 'continuation', 'risk']
```

---

## 📝 Import Organization

Organize imports in the following order:

```python
# Standard library imports
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

# Third-party imports
import pandas as pd
import numpy as np
import requests
from sqlalchemy import create_engine

# Local application imports
from config.settings.base_config import *
from src.utils.logging_utils import get_logger
from src.core.exceptions import RegimeDetectionError

# Module-level logger
logger = get_logger(__name__)
```

---

## 🏗️ Code Structure Standards

### Constants and Module Variables

```python
# Module-level constants (UPPER_CASE)
DEFAULT_TIMEOUT: int = 30
"""Default timeout in seconds for API requests."""

CNN_FEED_URL: str = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
"""URL endpoint for CNN Fear & Greed Index data."""

REGIME_THRESHOLDS: Dict[str, Tuple[int, int]] = {
    'extreme_fear': (0, 25),
    'fear': (25, 45),
    'neutral': (45, 55),
    'greed': (55, 75),
    'extreme_greed': (75, 100)
}
"""Numerical ranges defining each market regime classification."""
```

### Exception Handling

```python
def risky_operation(self, data: Any) -> Any:
    """
    Perform operation that might fail with proper error handling.
    
    Args:
        data: Input data to process
        
    Returns:
        Processed data result
        
    Raises:
        ValidationError: If input data is invalid
        ProcessingError: If processing fails
        ConnectionError: If external service unavailable
    """
    try:
        # Validate input
        if not self._validate_input(data):
            raise ValidationError("Input data validation failed")
            
        # Process data
        result = self._process_data(data)
        
        logger.info(f"Successfully processed data: {type(result)}")
        return result
        
    except requests.RequestException as e:
        logger.error(f"Network error during processing: {e}")
        raise ConnectionError(f"Failed to connect to external service: {e}") from e
        
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}", exc_info=True)
        raise ProcessingError(f"Data processing failed: {e}") from e
```

---

## 🧪 Example Usage in Docstrings

Include comprehensive examples that can be run directly:

```python
def analyze_stock(self, symbol: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze a stock symbol through the complete pipeline.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL')
        config (Dict[str, Any], optional): Analysis configuration
        
    Returns:
        Dict[str, Any]: Complete analysis results
        
    Example:
        Basic analysis:
        
        >>> analyzer = StockAnalyzer()
        >>> results = analyzer.analyze_stock('AAPL')
        >>> print(f"Recommendation: {results['recommendation']}")
        Recommendation: BUY
        
        Custom configuration:
        
        >>> config = {
        ...     'lookback_days': 60,
        ...     'use_ai_analysis': True,
        ...     'confidence_threshold': 0.8
        ... }
        >>> results = analyzer.analyze_stock('MSFT', config=config)
        >>> print(f"Confidence: {results['confidence']:.2f}")
        Confidence: 0.85
        
        Batch processing:
        
        >>> symbols = ['AAPL', 'MSFT', 'GOOGL']
        >>> all_results = {}
        >>> for symbol in symbols:
        ...     all_results[symbol] = analyzer.analyze_stock(symbol)
        >>> print(f"Analyzed {len(all_results)} stocks")
        Analyzed 3 stocks
    """
```

---

## 📊 Performance Documentation

Document performance characteristics for critical methods:

```python
def batch_process_symbols(self, symbols: List[str]) -> Dict[str, Any]:
    """
    Process multiple stock symbols in parallel.
    
    Performance:
        - Typical processing time: ~50ms per symbol
        - Memory usage: ~2MB per 100 symbols
        - Optimal batch size: 50-100 symbols
        - Network calls: 1 per symbol (cacheable)
        - CPU usage: Moderate (parallel processing)
        
    Scaling:
        - Linear time complexity: O(n) where n = number of symbols
        - Parallel processing reduces wall-clock time by ~70%
        - Memory usage scales linearly with batch size
        
    Benchmarks (tested on AWS c5.xlarge):
        - 10 symbols: ~500ms total, ~50ms per symbol
        - 100 symbols: ~3.2s total, ~32ms per symbol  
        - 1000 symbols: ~28s total, ~28ms per symbol
        
    Args:
        symbols: List of stock symbols to process
        
    Returns:
        Processing results for all symbols
    """
```

---

## 🔄 Documentation Generation

### Automatic Generation with Sphinx

1. **Install Sphinx** (add to requirements.txt):
```bash
sphinx>=7.0.0
sphinx-rtd-theme>=1.3.0
sphinxcontrib-napoleon>=0.7
```

2. **Generate documentation**:
```bash
cd docs/api
sphinx-build -b html . _build
```

3. **View documentation**:
```bash
# Open docs/api/_build/index.html in browser
firefox docs/api/_build/index.html
```

### Manual Documentation Updates

Update the API documentation index when adding new modules:

```rst
.. automodule:: src.core.new_module.new_component
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## ✅ Quality Checklist

Before committing code, ensure:

### File Headers
- [ ] ASCII art header included
- [ ] All placeholder values filled in
- [ ] Purpose clearly described
- [ ] Dependencies listed
- [ ] Pipeline stage identified
- [ ] Testing files referenced

### Docstrings
- [ ] Module docstring with overview and examples
- [ ] All public classes documented
- [ ] All public functions documented
- [ ] All parameters documented with types
- [ ] Return values documented with types  
- [ ] Exceptions documented
- [ ] Examples that can be run
- [ ] Performance notes for critical methods

### Type Annotations
- [ ] All function parameters have types
- [ ] All function return values have types
- [ ] Complex types properly imported
- [ ] Optional parameters clearly marked

### Code Quality
- [ ] Imports organized properly
- [ ] Constants documented
- [ ] Exception handling documented
- [ ] Logging statements included

---

## 🛠️ VS Code Setup for Documentation

Add these VS Code snippets for consistent documentation:

```json
{
    "KHAZAD Header": {
        "prefix": "kh-header",
        "body": [
            "#!/usr/bin/env python3",
            "\"\"\"",
            "███████╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗",
            "██╔════╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║",
            "██║     ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║",
            "██║     ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║",
            "╚██████╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║",
            " ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝",
            "",
            "📈 ALGORITHMIC TRADING SYSTEM - \"They delved too greedily and too deep...\"",
            "",
            "MODULE: ${1:Module Name}",
            "FILE: ${TM_FILENAME_BASE}",
            "CREATED: ${CURRENT_YEAR}-${CURRENT_MONTH}-${CURRENT_DATE}",
            "AUTHOR: FeanorKingofNoldor",
            "\"\"\"",
            "",
            "from typing import Dict, List, Optional, Any",
            "from src.utils.logging_utils import get_logger",
            "",
            "logger = get_logger(__name__)",
            "",
            "$0"
        ]
    },
    
    "Function Docstring": {
        "prefix": "kh-doc-func",
        "body": [
            "\"\"\"",
            "${1:Brief function description}.",
            "",
            "${2:Longer description if needed}",
            "",
            "Args:",
            "    ${3:param_name} (${4:type}): ${5:Description}",
            "",
            "Returns:",
            "    ${6:return_type}: ${7:Return description}",
            "",
            "Raises:",
            "    ${8:ExceptionType}: ${9:When this exception is raised}",
            "",
            "Example:",
            "    >>> ${10:example_usage}",
            "    ${11:expected_output}",
            "\"\"\""
        ]
    }
}
```

---

*🎯 **Remember**: Good documentation is not just comments—it's a commitment to code clarity, maintainability, and professional presentation of your work!*