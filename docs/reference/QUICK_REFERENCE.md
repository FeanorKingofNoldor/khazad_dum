# KHAZAD_DUM Quick Reference

> **⚡ 5-Minute Project Refresh** - Everything you need to get back into KHAZAD_DUM quickly

## 🚀 Immediate Startup Commands

```bash
# Start production infrastructure (Database + Cache)
docker-compose up -d database redis

# Run main trading pipeline
python main.py

# Monitor system (cyberpunk style)
python khazad_monitor/cyberpunk_monitor.py

# Check system status
docker-compose ps
```

---

## 🔧 Environment Check

```bash
# Verify database connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://khazad_user:khazad_secure_2024!@localhost:5433/khazad_dum')
print('✓ PostgreSQL connected')
conn.close()
"

# Verify Redis connection  
python -c "
import redis
r = redis.Redis(host='localhost', port=6380, password='redis_secure_2024!')
print('✓ Redis connected:', r.ping())
"

# Check API keys
python -c "
from config.settings.base_config import OPENAI_API_KEY
print('✓ OpenAI key configured' if OPENAI_API_KEY else '❌ Missing OpenAI key')
"
```

---

## 📊 System Architecture (30-second overview)

```
Market Data → Regime Detection → Stock Screening → AI Analysis → Pattern Recognition → Portfolio Construction
     ↓              ↓                  ↓              ↓                ↓                    ↓
 [Finnhub]    [CNN F&G Index]    [S&P 500 Filter] [TradingAgents]  [Pattern Memory]   [Position Sizing]
```

**Data Flow:** Raw market data → Filtered candidates → AI research → Pattern-based decisions → Automated trades

---

## 🗄️ Database & Infrastructure

### Production Setup (Current)
```bash
# PostgreSQL (primary database)
Host: localhost:5433  
Database: khazad_dum
User: khazad_user
Password: khazad_secure_2024!

# Redis (caching)
Host: localhost:6380
Password: redis_secure_2024!

# Key Tables:
stock_metrics                    # Raw market data
tradingagents_analysis_results   # AI analysis results  
position_tracking                # Live positions & P&L
pattern_performance              # Pattern effectiveness
pipeline_decisions               # Full audit trail
```

### Development Setup (Alternative)
```bash
# SQLite (for quick dev work)
Database: config/data/databases/khazad_dum.db
# No password required, file-based
```

---

## 🤖 TradingAgents Integration

```bash
# Test TradingAgents directly
cd tradingagents_lib && python -m cli.main

# Quick analysis example
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate('AAPL', '2024-05-10')
print(decision)
"

# Batch process stocks
python -c "
from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor
from src.data_pipeline.storage.database_manager import DatabaseManager
db = DatabaseManager()
processor = BatchProcessor(db)
processor.process_batch(['AAPL', 'MSFT', 'GOOGL'])
"
```

---

## 🧪 Testing Commands

```bash
# Run all tests
python -m pytest tests/

# Test specific components
python -m pytest tests/unit/                              # Unit tests only
python -m pytest tests/integration/                       # Integration tests
python -m pytest tests/integration/test_without_ibkr.py   # No broker needed

# Test individual monitoring components
python khazad_monitor/test_monitor.py
python khazad_monitor/test_charts.py

# Database migration test
python scripts/migrate_to_postgres.py --test
```

---

## 🔍 Troubleshooting Quick Fixes

### Connection Issues
```bash
# Database connection refused
docker-compose restart database
docker-compose logs database

# Redis connection issues  
docker-compose restart redis
redis-cli -h localhost -p 6380 -a redis_secure_2024! ping

# Port conflicts
sudo netstat -tlnp | grep :5433  # Check if port is free
sudo netstat -tlnp | grep :6380  # Check if port is free
```

### API Issues
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models | head

# Check Finnhub API  
echo $FINNHUB_API_KEY
curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=$FINNHUB_API_KEY"
```

### Performance Issues
```bash
# Check system resources
docker stats khazad-database khazad-redis

# Check database performance
PGPASSWORD=khazad_secure_2024! psql -h localhost -p 5433 -U khazad_user -d khazad_dum -c "
SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del 
FROM pg_stat_user_tables ORDER BY n_tup_ins DESC LIMIT 10;
"

# Clear Redis cache
redis-cli -h localhost -p 6380 -a redis_secure_2024! FLUSHALL
```

---

## 📁 Key Configuration Files

```bash
# Main configuration (ALL settings here)
config/settings/base_config.py

# Environment variables (API keys, DB config)
.env

# Docker orchestration  
docker-compose.yml

# Dependencies
requirements.txt

# TradingAgents config
tradingagents_lib/.env
```

---

## 🎯 Market Regimes (Quick Reference)

| Regime | Fear & Greed Range | Position Multiplier | Strategy |
|--------|-------------------|-------------------|----------|
| **Extreme Fear** | 0-25 | 1.5x | Buy aggressively |
| **Fear** | 25-45 | 1.2x | Buy opportunities |  
| **Neutral** | 45-55 | 1.0x | Standard sizing |
| **Greed** | 55-75 | 0.8x | Reduce exposure |
| **Extreme Greed** | 75-100 | 0.5x | Minimal exposure |

---

## 💡 Pattern Types (Quick Reference)

```python
# Reversal patterns (buy signals)
REVERSAL_PATTERNS = [
    'oversold_bounce',      # RSI < 30, volume spike
    'support_hold',         # Price holds key support  
    'hammer_candle',        # Hammer/doji at support
    'gap_fill'              # Gap down then recovery
]

# Breakout patterns (momentum signals)  
BREAKOUT_PATTERNS = [
    'resistance_break',     # Clean break above resistance
    'volume_breakout',      # Volume confirms price move
    'consolidation_break',  # Break from tight range
    'earnings_gap'          # Post-earnings momentum
]

# Risk patterns (sell signals)
RISK_PATTERNS = [
    'failed_breakout',      # False break, quick reversal
    'volume_divergence',    # Price up, volume down  
    'overbought_stall',     # RSI > 70, momentum loss
    'support_break'         # Clean break below support
]
```

---

## 🔄 Quick Maintenance Commands

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Backup database
docker exec khazad-database pg_dump -U khazad_user khazad_dum > backup_$(date +%Y%m%d).sql

# Clean up Docker
docker system prune -f
docker volume prune -f

# Reset development database  
rm -f config/data/databases/khazad_dum.db
python scripts/setup/initialize_database.py

# View recent logs
docker-compose logs --tail=100 -f database
docker-compose logs --tail=100 -f redis
```

---

## 📞 Emergency Stops

```bash
# Stop all trading immediately
docker-compose stop trading-engine

# Stop all services
docker-compose down

# Emergency database backup before changes
docker exec khazad-database pg_dump -U khazad_user khazad_dum > emergency_backup.sql

# Kill all Python processes (if hanging)
pkill -f python
```

---

*💡 **Pro Tip**: Bookmark this page and keep it open in a browser tab when working on the project!*