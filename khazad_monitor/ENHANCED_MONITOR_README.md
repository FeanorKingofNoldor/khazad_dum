# Enhanced Monitor for Khazad-dûm Trading System

The Enhanced Monitor is a professional-grade Terminal User Interface (TUI) that provides real-time monitoring of the Khazad-dûm trading system with actual database integration and rich visual feedback.

## ✨ Features

- **Real Database Integration**: Direct connection to your production SQLite database
- **Live Portfolio Tracking**: Real-time position monitoring with P&L calculations
- **Interactive Charts**: Terminal-based portfolio performance charts using plotext
- **Market Regime Display**: Current market conditions and Fear & Greed index
- **Recent Signals**: Latest TradingAgents analysis results and decisions
- **Smart Fallback**: Automatic fallback to mock data if database unavailable
- **Interactive Controls**: Real-time data refresh and mode switching
- **Professional UI**: Rich terminal interface with color coding and panels

## 🚀 Quick Start

### Basic Usage

```bash
# Run with live database data (recommended)
python khazad_monitor/enhanced_monitor.py

# Run with mock data for testing
python khazad_monitor/enhanced_monitor.py --mock

# Custom refresh interval (default is 5 seconds)
python khazad_monitor/enhanced_monitor.py --refresh 10
```

### Using the Launcher (Recommended)

```bash
# Interactive launcher with presets
python khazad_monitor/run_enhanced.py --help

# Demo mode (mock data, fast refresh)
python khazad_monitor/run_enhanced.py --demo

# Live data with custom refresh
python khazad_monitor/run_enhanced.py --refresh 15
```

## 🖥️ Interface Overview

The monitor displays information in a structured layout:

```
┌─────────────────────────────────────────┐
│           🏔️ Trading System Status     │
│    Khazad-dûm Trading Monitor          │
│         2025-01-27 14:30:15             │
│      Market Regime: Neutral             │
│         Fear & Greed: 50/100            │
└─────────────────────────────────────────┘

┌─────────────────┐ ┌─────────────────────┐
│ 📊 Portfolio    │ │ 🎯 Recent Signals   │
│ Summary         │ │                     │
│                 │ │ Date Symbol Decision│
│ Total Pos: 3    │ │ 01/27 AAPL BUY_STR │
│ Open Pos:  3    │ │ 01/26 NVDA HOLD    │
│ Portfolio: 142k │ │ 01/25 SPY  BUY_WEAK│
│ Total P&L: +2.1k│ │                     │
│ Avg P&L: +1.5%  │ │                     │
└─────────────────┘ └─────────────────────┘

┌─────────────────────────────────────────┐
│        📈 Active Positions              │
│ Symbol Shares Entry Current P&L$ P&L%   │
│ AAPL   100   175.5  182.3  +680 +3.9%  │
│ NVDA    50   480.2  465.8  -722 -3.0%  │
│ SPY    200   452.1  458.8  +133 +1.5%  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│   📈 Portfolio Performance (30 days)    │
│      Portfolio value chart here         │
│      Generated using plotext            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Controls: q = quit, r = refresh,       │
│  m = toggle mock data                   │
│  Last updated: 14:30:15 | Refresh: 5s  │
│  Data source: Live                      │
└─────────────────────────────────────────┘
```

## ⌨️ Interactive Controls

While the monitor is running, you can use these keyboard shortcuts:

- **`q`** - Quit the monitor
- **`r`** - Force immediate data refresh (clears cache)
- **`m`** - Toggle between mock and live data modes

## 🗄️ Database Integration

The Enhanced Monitor integrates directly with your Khazad-dûm database:

### Live Data Sources
- `position_tracking` table for active positions
- `tradingagents_analysis_results` for recent signals
- `stock_metrics` for historical portfolio data
- Market regime detection system

### Fallback Behavior
If database connection fails:
1. Automatically switches to mock data mode
2. Displays warning message
3. Provides realistic sample data for testing
4. Can be toggled back to live mode with `m` key

## 📊 Data Display

### Portfolio Summary
- **Total Positions**: All tracked positions (including closed)
- **Open Positions**: Currently active positions only
- **Portfolio Value**: Current total value of open positions
- **Total P&L**: Unrealized gains/losses across all positions
- **Avg P&L %**: Average percentage gain/loss

### Position Details
Each active position shows:
- **Symbol**: Stock ticker
- **Shares**: Number of shares held
- **Entry/Current**: Entry price vs current market price
- **P&L $ / P&L %**: Dollar and percentage gains/losses
- **Stop Loss/Target**: Risk management levels (if set)

### Recent Signals
Latest TradingAgents analysis results:
- **Date**: Analysis date
- **Symbol**: Analyzed stock
- **Decision**: BUY_STRONG, BUY_WEAK, HOLD, SELL_WEAK, SELL_STRONG
- **Conviction**: Confidence score (0.0-1.0)
- **Price**: Entry/analysis price
- **Regime**: Market regime during analysis

## 🎨 Visual Features

### Color Coding
- **Green**: Positive P&L, bullish signals, good performance
- **Red**: Negative P&L, bearish signals, losses
- **Yellow**: Neutral conditions, warnings, holds
- **Cyan**: Headers, system information
- **Magenta**: Recent signals, important data

### Charts
- Real-time portfolio performance charts
- 30-day historical view by default
- ASCII-based charts using plotext library
- Automatic scaling and formatting

## 🛠️ Configuration

### Refresh Settings
```python
# Default refresh interval
refresh_interval = 5  # seconds

# Cache timeout (avoids excessive DB queries)
cache_timeout = 30  # seconds

# Chart timeframe
chart_days = 30  # days of history
```

### Customization
You can modify the monitor by editing:
- `enhanced_monitor.py` - Main UI logic
- `data_fetcher.py` - Database integration
- Color schemes and panel layouts
- Data refresh intervals and caching

## 🔧 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure project root is in Python path
export PYTHONPATH=/path/to/khazad_dum:$PYTHONPATH
```

**Database Connection Errors**
- Monitor automatically falls back to mock data
- Check database file exists: `config/data/databases/khazad_dum.db`
- Verify database permissions and schema

**Terminal Display Issues**
- Ensure terminal supports color output
- Minimum terminal size: 120x40 characters
- Rich library handles most terminal compatibility

**Performance Issues**
```bash
# Increase refresh interval to reduce load
python enhanced_monitor.py --refresh 15

# Use mock data for testing
python enhanced_monitor.py --mock
```

### Debug Mode
```python
# Add debug prints in enhanced_monitor.py
print(f"Debug: {variable}")

# Check data fetcher connection
from khazad_monitor.data_fetcher import DataFetcher
df = DataFetcher(use_mock=False)
print(df.init_db_connection())
```

## 🔄 Development

### Adding New Panels
1. Create panel method in `EnhancedMonitor` class
2. Update `create_layout()` to include new panel
3. Update `update_layout()` to refresh new panel

### Extending Data Sources
1. Add new methods to `DataFetcher` class
2. Include mock data fallbacks
3. Update caching logic as needed

### Custom Styling
```python
# Modify color schemes
regime_colors = {
    'extreme_fear': 'bold red',
    'fear': 'red',
    # ... customize as needed
}
```

## 📝 Dependencies

### Required
- `rich` - Terminal UI framework
- `plotext` - Terminal-based plotting
- `sqlite3` - Database connectivity (built-in)

### Optional
- `src.data_pipeline.storage.database_manager` - Database integration
- `src.core.market_analysis.regime_detector` - Market regime detection

## 🎯 Use Cases

### Development
- Monitor system behavior during development
- Test with mock data before deploying
- Debug trading logic and positions

### Production Monitoring  
- Real-time oversight of live trading
- Quick assessment of portfolio performance
- Monitor recent AI trading decisions

### Analysis
- Historical portfolio performance tracking
- Pattern recognition in trading signals
- Market regime correlation analysis

## 🔮 Future Enhancements

Potential improvements:
- Historical trade analysis views
- Alert system integration
- Export data to files
- Multiple timeframe charts
- Position-specific detail views
- Integration with broker APIs for real-time prices

---

The Enhanced Monitor represents a significant upgrade to the Khazad-dûm monitoring capabilities, providing professional-grade real-time oversight with both live data integration and robust fallback mechanisms.