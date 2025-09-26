# Khazad-dûm Trading System

An advanced algorithmic trading system combining market regime detection, AI-powered analysis, and pattern recognition for systematic trading strategies.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Keys](#api-keys)
- [Trading Parameters](#trading-parameters)
- [Pattern System Settings](#pattern-system-settings)
- [Broker Configuration](#broker-configuration)
- [Usage](#usage)
- [System Components](#system-components)
- [Development](#development)
- [Testing](#testing)

## Overview

Khazad-dûm is a comprehensive trading system that combines multiple analytical approaches:
- Market regime detection using CNN Fear & Greed Index
- Multi-stage stock filtering pipeline
- AI-powered fundamental and technical analysis
- Pattern recognition and machine learning feedback loops
- Automated portfolio construction and risk management

## Features

### Core Capabilities
- **Market Regime Detection**: Real-time regime classification using market sentiment indicators
- **Smart Filtering**: Multi-stage filtering reducing S&P 500 to top candidates
- **AI Analysis**: TradingAgents integration for deep fundamental research
- **Pattern Learning**: Historical pattern recognition with performance tracking
- **Portfolio Management**: Automated position sizing and portfolio construction
- **Broker Integration**: Support for Interactive Brokers and mock trading

### Advanced Features
- Weekly pattern analysis and memory injection
- Performance observation and feedback loops
- Regime-adaptive position sizing
- Risk management with dynamic stop losses
- Batch processing for multiple stocks

## Project Structure

```
khazad_dum/
├── src/
│   ├── core/                           # Core business logic
│   │   ├── market_analysis/           # Market regime detection
│   │   │   ├── regime_detector.py     # CNN F&G based regime detection
│   │   │   └── cnn_feed_parser.py     # CNN Fear & Greed data fetcher
│   │   ├── stock_screening/           # Stock filtering system
│   │   │   └── stock_filter.py        # Multi-stage filtering logic
│   │   ├── pattern_recognition/       # Pattern-based trading
│   │   │   ├── pattern_classifier.py  # Pattern identification
│   │   │   ├── pattern_tracker.py     # Performance tracking
│   │   │   ├── pattern_database.py    # Pattern storage
│   │   │   └── memory_injector.py     # TradingAgents memory system
│   │   └── portfolio_management/      # Portfolio construction
│   │       ├── portfolio_constructor.py
│   │       ├── position_tracker.py
│   │       └── performance_observer.py
│   ├── data_pipeline/                 # Data fetching and storage
│   │   ├── market_data/              # Market data fetchers
│   │   ├── storage/                  # Database management
│   │   └── external_apis/            # API integrations
│   ├── trading_engines/              # Trading execution
│   │   ├── tradingagents_integration/  # AI analysis system
│   │   └── broker_connections/         # Broker interfaces
│   └── integrations/                 # System integrations
├── config/
│   └── settings/
│       └── base_config.py            # All configuration settings
├── scripts/
│   ├── daily_operations/            # Daily trading scripts
│   ├── maintenance/                 # System maintenance
│   └── setup/                      # Setup utilities
├── tests/                          # Test suites
├── tradingagents_lib/              # TradingAgents library
└── main.py                         # Main entry point
```

## Installation

### Prerequisites
- Python 3.8+
- Interactive Brokers account (optional, for live trading)
- API keys for OpenAI and Finnhub

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/FeanorKingofNoldor/khazad_dum.git
cd khazad_dum
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Initialize database:**
```bash
python scripts/setup/initialize_database.py
```

## Configuration

### API Keys

Create a `.env` file in the project root:

```env
# Required API Keys
OPENAI_API_KEY=sk-...your-key-here
FINNHUB_API_KEY=your-finnhub-key-here

# Optional API Keys
POLYGON_API_KEY=your-polygon-key
ALPHA_VANTAGE_KEY=your-alpha-vantage-key
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-secret
```

### Trading Parameters

Edit `config/settings/base_config.py`:

```python
# Market Regime Thresholds
FEAR_GREED_THRESHOLDS = {
    'extreme_fear': 25,
    'fear': 45,
    'neutral': 55,
    'greed': 75,
    'extreme_greed': 100
}

# Position Sizing
POSITION_SIZE_MULTIPLIERS = {
    'extreme_fear': 1.5,  # Increase size in fear
    'fear': 1.2,
    'neutral': 1.0,
    'greed': 0.8,
    'extreme_greed': 0.5  # Reduce size in greed
}

# Risk Management
MAX_POSITIONS = 10
MAX_POSITION_SIZE = 0.20  # 20% max per position
DEFAULT_STOP_LOSS = 0.08  # 8% stop loss
RISK_PER_TRADE = 0.02     # 2% risk per trade

# Filtering Parameters
FILTER_SETTINGS = {
    'min_volume': 1000000,      # Minimum daily volume
    'min_market_cap': 1e9,      # $1B minimum market cap
    'quality_score_threshold': 7.0,
    'max_stocks_per_regime': {
        'extreme_fear': 50,
        'fear': 30,
        'neutral': 20,
        'greed': 15,
        'extreme_greed': 10
    }
}
```

### Pattern System Settings

Configure pattern recognition thresholds:

```python
# Pattern Classification
PATTERN_RSI_THRESHOLDS = {
    'oversold': 30,
    'overbought': 70
}

PATTERN_VOLUME_THRESHOLDS = {
    'low': 0.5,      # Below 50% of average
    'high': 1.5,     # Above 150% of average
    'explosive': 2.5  # Above 250% of average
}

# Pattern Performance Tracking
MIN_PATTERN_TRADES = 10     # Minimum trades to consider pattern valid
CONFIDENCE_THRESHOLD = 0.7   # 70% confidence required
WEEKLY_ANALYSIS_DAY = 6      # Sunday = 6

# Memory Injection
MAX_MEMORIES_PER_PATTERN = 5
MEMORY_RELEVANCE_DAYS = 30
```

### Broker Configuration

Configure IBKR integration:

```python
# Interactive Brokers Settings
IBKR_ENABLED = False  # Set True to enable
IBKR_DEFAULT_PORT = 4002  # 4001=live, 4002=paper

# Account Settings
IBKR_ACCOUNT_ID = ""  # Your IB account ID
IBKR_CURRENCY = "USD"
IBKR_EXCHANGE = "SMART"

# Order Settings
ORDER_TIMEOUT_SECONDS = 60
USE_ADAPTIVE_ORDERS = True
```

### TradingAgents Configuration

Configure AI analysis settings:

```python
TRADINGAGENTS_CONFIG = {
    'llm_provider': 'openai',
    'backend_url': 'https://api.openai.com/v1',
    'deep_think_llm': 'gpt-4o-mini',
    'quick_think_llm': 'gpt-4o-mini',
    'temperature': 0.7,
    'max_debate_rounds': 2,
    'online_tools': True,
    'use_memory': True,
    'memory_top_k': 10
}
```

## Usage

### Basic Operation

Run the complete pipeline:

```bash
python main.py
```

### Daily Trading Workflow

1. **Morning Analysis:**
```bash
python scripts/daily_operations/morning_analysis.py
```

2. **Execute Trades:**
```bash
python scripts/daily_operations/execute_trades.py
```

3. **End of Day:**
```bash
python scripts/daily_operations/eod_analysis.py
```

### Pattern Learning

Run weekly pattern analysis (typically on weekends):

```bash
python scripts/maintenance/run_weekly_learning.py
```

View pattern performance:

```bash
python scripts/maintenance/pattern_dashboard.py
```

### Batch Processing

Analyze multiple stocks:

```bash
python -c "
from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor
from src.data_pipeline.storage.database_manager import DatabaseManager

db = DatabaseManager()
processor = BatchProcessor(db)
processor.process_batch(['AAPL', 'MSFT', 'GOOGL'])
"
```

## System Components

### 1. Market Regime Detection

The system uses CNN Fear & Greed Index combined with VIX to classify market regimes:
- Extreme Fear (0-25): High opportunity, increase position sizes
- Fear (26-45): Good opportunities, normal to increased sizing
- Neutral (46-55): Balanced approach
- Greed (56-75): Caution, reduced position sizes
- Extreme Greed (76-100): High risk, minimal positions

### 2. Stock Filtering Pipeline

Multi-stage filtering process:
1. **Universe Selection**: S&P 500 stocks
2. **Quality Filter**: Market cap, volume, price requirements
3. **Technical Filter**: RSI, momentum, volatility
4. **Regime Filter**: Top N stocks based on regime
5. **Final Selection**: Score-based ranking

### 3. TradingAgents Analysis

AI-powered analysis providing:
- Fundamental research
- Technical analysis
- Risk assessment
- Position sizing recommendations
- Entry/exit points

### 4. Pattern Recognition

Historical pattern tracking:
- Identifies recurring market patterns
- Tracks performance by pattern type
- Injects successful patterns as memories
- Adapts strategies based on pattern success

### 5. Portfolio Construction

Automated portfolio management:
- Position sizing based on conviction and regime
- Risk-balanced allocation
- Maximum position limits
- Correlation analysis

## Development

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test suite
python -m pytest tests/unit/core/
python -m pytest tests/integration/

# With coverage
python -m pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
pylint src/

# Type checking
mypy src/
```

### Database Migrations

```bash
# Apply new migration
python scripts/maintenance/apply_db_migration.py

# Check database status
python scripts/maintenance/check_database.py
```

## Advanced Configuration

### Custom Strategies

Add custom strategies by extending base classes:

```python
from src.core.pattern_recognition import PatternClassifier

class CustomPattern(PatternClassifier):
    def classify(self, metrics):
        # Your pattern logic
        pass
```

### Custom Filters

Add filtering criteria:

```python
from src.core.stock_screening import StockFilter

class CustomFilter(StockFilter):
    def apply_custom_filter(self, stocks):
        # Your filter logic
        pass
```

## Monitoring

### Performance Metrics

Monitor system performance:

```bash
# View current positions
python scripts/monitoring/view_positions.py

# Performance report
python scripts/monitoring/performance_report.py

# Pattern statistics
python scripts/maintenance/pattern_dashboard.py
```

### Logs

Logs are stored in:
- `logs/main.log` - Main system log
- `logs/trading.log` - Trading decisions
- `logs/errors.log` - Error tracking

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in PYTHONPATH
2. **API Key Issues**: Verify .env file is properly configured
3. **Database Errors**: Run migration scripts
4. **IBKR Connection**: Check IB Gateway is running

### Debug Mode

Enable debug logging:

```python
# In config/settings/base_config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

## License

Private repository - All rights reserved

## Contact

GitHub: [@FeanorKingofNoldor](https://github.com/FeanorKingofNoldor)

---

*"The Dwarves delved too greedily and too deep."* - But with proper risk management, we won't awaken any Balrogs.