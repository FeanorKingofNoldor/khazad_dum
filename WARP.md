# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Commands

### Running the System
```bash
# Main trading pipeline (complete workflow)
python main.py

# Enhanced professional monitor (recommended) ⭐
python khazad_monitor/enhanced_monitor.py

# Monitor system (cyberpunk-style real-time monitoring)
python khazad_monitor/cyberpunk_monitor.py

# Simple monitoring interface
python khazad_monitor/simple_monitor.py
```

### Development & Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test suites
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run integration tests without IBKR
python -m pytest tests/integration/test_without_ibkr.py

# Test individual components
python khazad_monitor/test_monitor.py
python khazad_monitor/test_charts.py
```

### TradingAgents Library
```bash
# TradingAgents CLI (in tradingagents_lib/)
cd tradingagents_lib && python -m cli.main

# Direct TradingAgents usage
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate('AAPL', '2024-05-10')
print(decision)
"
```

### Quick Analysis
```bash
# Batch process specific stocks
python -c "
from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor
from src.data_pipeline.storage.database_manager import DatabaseManager
db = DatabaseManager()
processor = BatchProcessor(db)
processor.process_batch(['AAPL', 'MSFT', 'GOOGL'])
"
```

## Architecture Overview

### Core System Flow
The system implements a sophisticated 6-stage algorithmic trading pipeline:

1. **Market Regime Detection** (`src/core/market_analysis/`) - Uses CNN Fear & Greed Index to classify market conditions
2. **Stock Screening** (`src/core/stock_screening/`) - Multi-layer filtering from S&P 500 universe  
3. **AI Analysis** (`tradingagents_lib/`) - TradingAgents framework provides fundamental/technical research
4. **Pattern Recognition** (`src/core/pattern_recognition/`) - Historical pattern learning and memory injection
5. **Portfolio Construction** (`src/core/portfolio_management/`) - Regime-aware position sizing and risk management
6. **Performance Observation** - Continuous feedback loops for system improvement

### Key Components

**Market Regime System**: 
- Classifies markets into 5 regimes (extreme fear → extreme greed)
- Adjusts position sizing and filtering strictness by regime
- Different strategies: buy fear (1.5x position), sell greed (0.5x position)

**Pattern Learning Engine**:
- Tracks performance of historical trade patterns
- Injects successful patterns as "memories" into TradingAgents
- Dynamically adjusts stops/targets based on pattern effectiveness
- Weekly pattern analysis runs on Sundays

**TradingAgents Integration**:
- Multi-agent LLM framework simulating trading firm roles
- Fundamental, sentiment, news, and technical analysts
- Bullish/bearish researchers engage in structured debates  
- Risk management and portfolio approval workflow

**Position Management**:
- Maximum 5 simultaneous positions, 20% max position size
- Dynamic stop losses based on volatility (1.5-3.0x ATR)
- Regime-adaptive position sizing with Kelly criterion influence

## Configuration

### Critical Files
- `config/settings/base_config.py` - Master configuration (all settings in one place)
- `tradingagents_lib/.env` - API keys (OpenAI, Finnhub, etc.)
- `config/data/databases/khazad_dum.db` - SQLite database for all system data

### Key Configuration Areas

**API Requirements**:
- OpenAI API (required for TradingAgents LLM analysis)
- Finnhub API (required for market data)  
- Optional: Polygon, Alpha Vantage, Reddit APIs

**Trading Parameters**:
- Regime thresholds, position multipliers, filter percentiles all configurable
- Pattern system settings (confidence thresholds, memory injection rules)
- Risk management (max positions, stop loss multipliers, risk per trade)

**TradingAgents Config**:
- LLM models: `gpt-4o-mini` for cost efficiency vs `o1-preview` for deep analysis
- Debate rounds: More rounds = deeper analysis but higher API costs
- Online tools: Enable for real-time data vs cached TradingDB data

## Development Patterns

### Adding New Filters
Extend `src/core/stock_screening/stock_filter.py`:
```python
def apply_custom_filter(self, stocks, regime):
    # Filter logic here
    return filtered_stocks
```

### Adding New Patterns  
Extend `src/core/pattern_recognition/pattern_classifier.py`:
```python
def classify_custom_pattern(self, metrics):
    # Pattern identification logic
    return pattern_type
```

### Database Schema
The system uses SQLite with key tables:
- `stock_metrics` - Raw market data
- `tradingagents_analysis_results` - AI analysis results  
- `position_tracking` - Live positions and performance
- `pattern_performance` - Pattern effectiveness tracking
- `pipeline_decisions` - Full decision audit trail

### Testing Strategy
- Unit tests for individual components in `tests/unit/`
- Integration tests including mock broker tests in `tests/integration/`
- Component-specific tests in `khazad_monitor/test_*.py`
- Test without IBKR using `test_without_ibkr.py` for development

## Environment Setup

### Python Dependencies
- Core: `pandas`, `numpy`, `yfinance`, `requests`, `beautifulsoup4`
- Database: `sqlalchemy` 
- IBKR: `ib_async`
- Monitoring: `rich`, `plotext`
- AI: TradingAgents framework (included in `tradingagents_lib/`)

### Database Initialization
Database auto-initializes on first run. Schema includes pattern tracking, position management, and full pipeline observability.

## Monitoring & Observability

### Real-time Monitoring
- `khazad_monitor/enhanced_monitor.py` - Professional TUI with real database integration ⭐
- `khazad_monitor/cyberpunk_monitor.py` - Cyberpunk-themed real-time dashboard
- `khazad_monitor/simple_monitor.py` - Clean monitoring interface
- Rich terminal displays with live position tracking, P&L, and regime status

### Performance Tracking
- `src/core/portfolio_management/performance_observer.py` - Records all pipeline decisions
- Pattern performance analysis with win rates, expectancy, momentum tracking
- Regime-based performance analysis (how well strategies work in each market condition)

### Logging
- Main system logs in `logs/` directory
- Database-driven decision audit trail
- Pattern learning and memory injection logging

This system represents a sophisticated quantitative trading platform combining traditional technical analysis with modern AI techniques and comprehensive risk management.

<citations>
<document>
    <document_type>WARP_DOCUMENTATION</document_type>
    <document_id>getting-started/quickstart-guide/coding-in-warp</document_id>
</document>
</citations>