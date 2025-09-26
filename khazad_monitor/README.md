# KHAZAD_DUM Position Monitor

A simple terminal-based monitoring tool for portfolio positions with stop loss and target price visualization.

## Features

- 📊 **Portfolio Overview**: View total portfolio value chart over time
- 📈 **Position Charts**: Individual position charts with stop loss (red) and target (green) lines
- 📋 **Position Table**: See all positions with P&L calculations
- 🔄 **Auto-refresh**: Optional automatic data refresh
- 🎨 **Clean Terminal UI**: Built with Rich for beautiful terminal display

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connection:
```bash
cp .env.template .env
# Edit .env with your database credentials
```

## Usage

### Simple Version (Recommended for starting)
```bash
python simple_monitor.py
```

This version has a simple menu-driven interface:
- Press 1-5 to select options
- Easy to use over SSH
- No special terminal requirements

### Advanced Version (With live updates)
```bash
python monitor_cli.py
```

This version has hotkeys and live updating:
- [P] Portfolio view
- [S] Single position 
- [T] Table view
- [R] Refresh
- [Q] Quit

## Mock Data Mode

To test without a database connection:

1. Set in `.env`:
```
USE_MOCK=True
```

Or just run without configuring the database - it will automatically fall back to mock data.

## Chart Legend

In position charts:
- **Blue line**: Price history
- **Red line**: Stop loss level
- **Green line**: Target price
- **Yellow line**: Current price
- **White dotted**: Entry price

## Database Schema

Expected tables:
- `positions`: Current positions (symbol, shares, entry_price, stop_loss, target_price)
- `price_history`: Historical prices (symbol, date, close_price)
- `portfolio_history`: Portfolio values (date, total_value)

## Customization

Edit `config.py` to adjust:
- Chart dimensions (height/width)
- Color scheme
- Refresh rate
- Number of historical days to display

## Screenshots

### Position Chart Example
```
AAPL Position Monitor | P&L: +3.87%
     195 ├─────────────────────────── [Green: Target]
     190 │
     185 │           ╭────
     182 │      ╭────╯     [Yellow: Current]
     180 │  ╭───╯
     175 │──╯                [White: Entry]
     170 ├─────────────────────────── [Red: Stop Loss]
         └───────────────────────────
         01/15  01/20  01/25  01/30
```

## Troubleshooting

**Database connection fails:**
- Check your `.env` file has correct credentials
- Ensure PostgreSQL is running
- Monitor will automatically use mock data if connection fails

**Charts look distorted:**
- Ensure terminal width is at least 80 characters
- Try the simple_monitor.py version for better compatibility

**Can't see colors:**
- Make sure your terminal supports ANSI colors
- Most modern terminals (iTerm2, Windows Terminal, etc.) work fine

## Integration with KHAZAD_DUM

This monitor reads from your existing KHAZAD_DUM database. It's read-only and won't modify any data.

To integrate with your main system:
1. Point to the same database
2. Run alongside your trading system
3. Use for real-time position monitoring

## Future Enhancements

Possible additions:
- Alert notifications when price crosses stop/target
- Export charts to images
- Historical P&L tracking
- Risk metrics display
- Multi-portfolio support
