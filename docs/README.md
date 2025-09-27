# KHAZAD_DUM Documentation

> **📚 Complete documentation for the KHAZAD_DUM algorithmic trading system**

## 🚀 Quick Start

**New to KHAZAD_DUM?** Start here:

1. **[Quick Reference](reference/QUICK_REFERENCE.md)** ⚡ - 5-minute project refresh
2. **[Docker Guide](guides/DOCKER_GUIDE.md)** 🐳 - Production deployment 
3. **[Development Guide](guides/DEVELOPMENT_GUIDE.md)** ⚙️ - Development workflows

---

## 📖 Documentation Structure

### 🔗 Reference Guides
- **[Quick Reference](reference/QUICK_REFERENCE.md)** - Essential commands, configs, and troubleshooting
- **[API Reference](reference/API_REFERENCE.md)** - Code documentation *(coming soon)*
- **[Configuration Reference](reference/CONFIG_REFERENCE.md)** - All settings explained *(coming soon)*

### 📋 How-To Guides  
- **[Docker Guide](guides/DOCKER_GUIDE.md)** - Complete production deployment with containers
- **[Development Guide](guides/DEVELOPMENT_GUIDE.md)** - Development workflows, testing, and debugging
- **[Deployment Guide](guides/DEPLOYMENT_GUIDE.md)** - Production deployment strategies *(coming soon)*

### 🏗️ Architecture Documentation
- **[System Architecture](architecture/SYSTEM_OVERVIEW.md)** - High-level system design *(coming soon)*
- **[Data Flow](architecture/DATA_FLOW.md)** - How data moves through the system *(coming soon)*
- **[Component Design](architecture/COMPONENTS.md)** - Individual component documentation *(coming soon)*

### 🚨 Troubleshooting
- **[Common Issues](troubleshooting/COMMON_ISSUES.md)** - Known problems and solutions *(coming soon)*
- **[Performance Tuning](troubleshooting/PERFORMANCE.md)** - Optimization guides *(coming soon)*
- **[Monitoring & Alerts](troubleshooting/MONITORING.md)** - System monitoring setup *(coming soon)*

---

## 🎯 Documentation by Use Case

### "I need to get back into this project quickly"
→ **[Quick Reference](reference/QUICK_REFERENCE.md)** - Everything in one page

### "I need to deploy this to production" 
→ **[Docker Guide](guides/DOCKER_GUIDE.md)** - Complete containerized deployment

### "I want to add new features or fix bugs"
→ **[Development Guide](guides/DEVELOPMENT_GUIDE.md)** - Development workflows

### "Something is broken and I need to fix it"
→ **[Quick Reference](reference/QUICK_REFERENCE.md)** (Troubleshooting section)

### "I need to understand how this system works"
→ Start with main **[README.md](../README.md)**, then dive into architecture docs

---

## 🔧 System Status & Health Checks

### Current Production Setup ✅
```bash
# Infrastructure Status
docker-compose ps                    # Check container health
docker stats khazad-database khazad-redis  # Resource usage

# Database Health  
PGPASSWORD=khazad_secure_2024! psql -h localhost -p 5433 -U khazad_user -d khazad_dum -c "SELECT version();"

# Redis Health
redis-cli -h localhost -p 6380 -a redis_secure_2024! ping

# Application Health
python -c "from src.data_pipeline.storage.database_manager import DatabaseManager; print(DatabaseManager().health_check())"
```

### Core Services
- **Database:** PostgreSQL 16 on port 5433 ✅
- **Cache:** Redis 7 on port 6380 ✅  
- **Network:** Docker bridge networking ✅
- **Volumes:** Persistent data storage ✅

---

## 📈 System Overview

**KHAZAD_DUM** is a 6-stage algorithmic trading pipeline:

```
Market Data → Regime Detection → Stock Screening → AI Analysis → Pattern Recognition → Portfolio Construction
```

### Key Technologies
- **Backend:** Python 3.11+
- **Database:** PostgreSQL 16 (production) / SQLite (development)
- **Cache:** Redis 7
- **AI:** TradingAgents framework + OpenAI GPT
- **Deployment:** Docker + Docker Compose
- **Monitoring:** Custom cyberpunk-style dashboards

### Data Sources
- **Primary:** Finnhub (market data)
- **Secondary:** Polygon, Alpha Vantage  
- **Sentiment:** CNN Fear & Greed Index
- **Optional:** Reddit sentiment analysis

---

## 🚦 Getting Help

### Debug Workflow
1. **Check service status** → `docker-compose ps`
2. **Review logs** → `docker-compose logs [service]`
3. **Test connections** → Use commands from [Quick Reference](reference/QUICK_REFERENCE.md)
4. **Check API keys** → Verify in `.env` file
5. **Still stuck?** → Check [troubleshooting section](reference/QUICK_REFERENCE.md#-troubleshooting-quick-fixes)

### Performance Issues
1. **Check resource usage** → `docker stats`
2. **Monitor database** → Check slow queries
3. **Profile code** → Use Python profiling tools
4. **Review configs** → Optimize settings in `base_config.py`

---

## 📝 Documentation Standards

### For Developers Adding Documentation

**Writing Guidelines:**
- Use clear, actionable headings
- Include copy-paste code examples
- Add troubleshooting for common issues
- Test all commands before documenting
- Use consistent formatting (see existing docs)

**File Organization:**
```
docs/
├── README.md              # This index
├── reference/             # Quick lookups
├── guides/               # Step-by-step tutorials  
├── architecture/         # System design docs
└── troubleshooting/      # Problem-solving guides
```

**Markdown Standards:**
- Use emoji headers for visual scanning
- Code blocks must be properly formatted
- Include both examples and explanations
- Add "copy-paste ready" command blocks

---

## 🔄 Documentation Maintenance

### Keeping Docs Updated
- **After system changes:** Update relevant guides
- **After config changes:** Update Quick Reference
- **After new features:** Add to Development Guide  
- **Performance improvements:** Update troubleshooting

### Regular Reviews
- **Monthly:** Verify all commands still work
- **After major releases:** Update architecture docs
- **When issues arise:** Enhance troubleshooting guides

---

*💡 **Pro Tip**: Keep the [Quick Reference](reference/QUICK_REFERENCE.md) bookmarked - it's designed to get you productive in under 5 minutes when returning to the project!*