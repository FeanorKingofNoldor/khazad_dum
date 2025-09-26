# KHAZAD_DUM Cyberpunk Monitor v2.0

## 🎮 New Features

### Arrow Navigation System
- **↑↓** Arrow keys to navigate menus
- **Enter** to select
- **C** to enter command mode
- **Q** to quit

### Command Mode
Access with 'C' key from main menu. Available commands:
```
analyze [SYMBOL]  - Full analysis
chart [SYMBOL]    - Generate chart  
export [TYPE]     - Export data (csv/json/pdf)
risk             - Risk metrics display
scan             - Opportunity scanner
history          - Command history
clear            - Clear screen
exit             - Exit command mode
```

### File Manager
Organized file system with:
```
📁 REPORTS/
  ├── 📂 daily/
  ├── 📂 weekly/
  └── 📂 analysis/
📁 EXPORTS/
  ├── 📂 csv/
  ├── 📂 json/
  └── 📂 pdf/
📁 CHARTS/
  ├── 📂 portfolio/
  └── 📂 positions/
📁 LOGS/
  ├── 📂 trades/
  └── 📂 system/
```

## 🚀 Quick Start

### Easy Launch:
```bash
python launch.py
```

### Direct Access:
```bash
# Cyberpunk version (NEW)
python cyberpunk_monitor.py

# Simple version (original)
python simple_monitor.py
```

## 🎨 Cyberpunk Theme

### Color Scheme:
- **Cyan**: Primary UI elements
- **Magenta**: Secondary highlights
- **Green**: Profits/Targets
- **Red**: Losses/Stops
- **Yellow**: Current values/Warnings

### Visual Elements:
- ASCII art headers
- Animated menu cursors
- Matrix-style command mode
- Gradient effects
- Box drawing characters

## 📊 Chart Improvements

### Fixed Issues:
✅ Proper chart formatting
✅ Clean axis labels
✅ Better line rendering
✅ Correct stop/target lines
✅ Improved spacing

### Chart Legend:
- **Cyan line**: Price movement
- **Red line**: Stop loss
- **Green line**: Target price
- **Yellow line**: Current price
- **Magenta line**: Entry price

## ⚡ Keyboard Shortcuts

### Main Navigation:
- **↑/↓**: Move selection
- **Enter**: Select item
- **C**: Command mode
- **Q**: Quit/Back

### In Charts:
- **R**: Refresh data
- **E**: Export chart
- **Esc**: Back to menu

### In Tables:
- **S**: Sort columns
- **F**: Filter data
- **Space**: Select row

## 🛠️ Configuration

### Environment Variables (.env):
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=khazad_dum
DB_USER=postgres
DB_PASSWORD=your_password

# Display
THEME=cyberpunk
CHART_WIDTH=90
CHART_HEIGHT=25

# Features
USE_MOCK=False
AUTO_REFRESH=30
```

## 📝 System Commands

### Risk Analysis:
Shows comprehensive risk metrics including:
- Total portfolio risk
- Risk percentage
- Position concentration
- Stop loss proximity alerts

### Signal Generation:
Automatic signals for:
- **⚠ NEAR STOP**: Price approaching stop loss
- **🎯 NEAR TARGET**: Price approaching target
- **▶ ACTIVE**: Normal trading range

## 🔧 Troubleshooting

### Chart Display Issues:
- Ensure terminal width ≥ 100 chars
- Use a terminal with Unicode support
- Try reducing CHART_WIDTH in config

### Arrow Keys Not Working:
- Install prompt-toolkit: `pip install prompt-toolkit`
- Or use number keys as fallback
- Check terminal compatibility

### Colors Not Showing:
- Enable ANSI colors in terminal
- Use modern terminal (iTerm2, Windows Terminal)
- Check TERM environment variable

## 💾 File Operations

### Export Functions:
- **D**: Download reports (PDF)
- **E**: Export data (CSV/JSON)
- **G**: Generate charts (PNG)
- **L**: View system logs

### Auto-generated Files:
- Daily reports at midnight
- Weekly summaries on Sunday
- Trade logs after each transaction
- Chart snapshots on demand

## 🎯 Tips & Tricks

1. **Quick Analysis**: Use command mode for fastest access
2. **Multi-monitor**: Open multiple terminals for different views
3. **Custom Alerts**: Set stop proximity warnings in settings
4. **Batch Operations**: Use command mode for multiple symbols
5. **Export Automation**: Schedule exports via cron

## 🔒 Security Note

The cyberpunk theme is for visual enhancement only. 
All trading operations maintain the same security standards.
Never share your .env file or credentials.

---

**Version**: 2.0 Cyberpunk Edition
**Author**: KHAZAD_DUM Systems
**Theme**: Cyberpunk 2077 inspired

◢◤ HACK THE MARKETS ◢◤
