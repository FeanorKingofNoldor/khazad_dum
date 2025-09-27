#!/usr/bin/env python3
"""
Enhanced CLI Monitor for Khazad-dûm Trading System
Provides real-time monitoring with rich UI and actual database integration
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.align import Align
import plotext as plt

from khazad_monitor.data_fetcher import DataFetcher


class EnhancedMonitor:
    """Enhanced CLI monitoring dashboard for the trading system"""
    
    def __init__(self, use_mock: bool = False):
        self.console = Console()
        self.data_fetcher = DataFetcher(use_mock=use_mock)
        self.running = True
        self.last_update = datetime.now()
        
        # Display settings
        self.refresh_interval = 5  # seconds
        self.chart_days = 30
        
        # Cache for data to avoid excessive database calls
        self.cache = {}
        self.cache_timeout = 30  # seconds
    
    def create_header(self) -> Panel:
        """Create the header panel"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        regime_data = self.get_cached_data('regime', self.data_fetcher.get_market_regime)
        
        regime = regime_data.get('regime', 'unknown')
        fear_greed = regime_data.get('fear_greed_value', 50)
        
        # Color code the regime
        regime_colors = {
            'extreme_fear': 'bold red',
            'fear': 'red',
            'neutral': 'yellow',
            'greed': 'green',
            'extreme_greed': 'bold green'
        }
        
        regime_text = Text(f"Market Regime: {regime.replace('_', ' ').title()}", 
                          style=regime_colors.get(regime, 'white'))
        
        header_text = Text.assemble(
            ("Khazad-dûm Trading Monitor", "bold cyan"),
            f"\\n{current_time}\\n",
            regime_text,
            f"\\nFear & Greed: {fear_greed}/100"
        )
        
        return Panel(
            Align.center(header_text),
            title="🏔️ Trading System Status",
            border_style="cyan"
        )
    
    def create_portfolio_summary(self) -> Panel:
        """Create portfolio summary panel"""
        try:
            metrics = self.get_cached_data('metrics', self.data_fetcher.get_system_metrics)
            positions = self.get_cached_data('positions', self.data_fetcher.get_portfolio_positions)
            
            # Calculate additional metrics
            total_positions = len(positions)
            open_positions = len([p for p in positions if p.get('shares', 0) > 0])
            total_value = metrics.get('total_value', 0)
            total_pnl = metrics.get('total_pnl', 0)
            avg_pnl_pct = metrics.get('avg_pnl_pct', 0)
            
            # Create summary table
            table = Table.grid(padding=1)
            table.add_column(style="bold")
            table.add_column()
            
            # Color code P&L
            pnl_color = "green" if total_pnl >= 0 else "red"
            pnl_pct_color = "green" if avg_pnl_pct >= 0 else "red"
            
            table.add_row("Total Positions:", f"{total_positions}")
            table.add_row("Open Positions:", f"{open_positions}")
            table.add_row("Portfolio Value:", f"${total_value:,.2f}")
            table.add_row("Total P&L:", f"[{pnl_color}]${total_pnl:+,.2f}[/{pnl_color}]")
            table.add_row("Avg P&L %:", f"[{pnl_pct_color}]{avg_pnl_pct:+.2f}%[/{pnl_pct_color}]")
            
        except Exception as e:
            table = Table.grid()
            table.add_row(f"Error loading portfolio data: {e}")
        
        return Panel(
            table,
            title="📊 Portfolio Summary",
            border_style="blue"
        )
    
    def create_positions_table(self) -> Panel:
        """Create active positions table"""
        try:
            positions = self.get_cached_data('positions', self.data_fetcher.get_portfolio_positions)
            
            if not positions:
                return Panel(
                    Align.center("No active positions"),
                    title="📈 Active Positions",
                    border_style="yellow"
                )
            
            table = Table()
            table.add_column("Symbol", style="bold cyan")
            table.add_column("Shares", justify="right")
            table.add_column("Entry", justify="right")
            table.add_column("Current", justify="right")
            table.add_column("P&L $", justify="right")
            table.add_column("P&L %", justify="right")
            table.add_column("Stop Loss", justify="right")
            table.add_column("Target", justify="right")
            
            for pos in positions[:10]:  # Show top 10 positions
                symbol = pos.get('symbol', 'N/A')
                shares = pos.get('shares', 0)
                entry_price = pos.get('entry_price', 0)
                current_price = pos.get('current_price', 0)
                unrealized_pnl = pos.get('unrealized_pnl', 0)
                pnl_pct = pos.get('pnl_percentage', 0)
                stop_loss = pos.get('stop_loss', 0)
                target_price = pos.get('target_price', 0)
                
                # Color code P&L
                pnl_color = "green" if unrealized_pnl >= 0 else "red"
                pnl_pct_color = "green" if pnl_pct >= 0 else "red"
                
                table.add_row(
                    symbol,
                    f"{shares:,.0f}",
                    f"${entry_price:.2f}",
                    f"${current_price:.2f}",
                    f"[{pnl_color}]${unrealized_pnl:+,.2f}[/{pnl_color}]",
                    f"[{pnl_pct_color}]{pnl_pct:+.1f}%[/{pnl_pct_color}]",
                    f"${stop_loss:.2f}" if stop_loss > 0 else "-",
                    f"${target_price:.2f}" if target_price > 0 else "-"
                )
            
        except Exception as e:
            table = Table()
            table.add_row(f"Error loading positions: {e}")
        
        return Panel(
            table,
            title="📈 Active Positions",
            border_style="green"
        )
    
    def create_signals_table(self) -> Panel:
        """Create recent signals table"""
        try:
            signals = self.get_cached_data('signals', 
                                         lambda: self.data_fetcher.get_recent_signals(8))
            
            if not signals:
                return Panel(
                    Align.center("No recent signals"),
                    title="🎯 Recent Signals",
                    border_style="magenta"
                )
            
            table = Table()
            table.add_column("Date", style="dim")
            table.add_column("Symbol", style="bold")
            table.add_column("Decision", justify="center")
            table.add_column("Conviction", justify="right")
            table.add_column("Price", justify="right")
            table.add_column("Regime", justify="center")
            
            for signal in signals:
                date = signal.get('analysis_date', datetime.now())
                if isinstance(date, str):
                    try:
                        date = datetime.fromisoformat(date)
                    except:
                        date = datetime.now()
                
                symbol = signal.get('symbol', 'N/A')
                decision = signal.get('decision', 'UNKNOWN')
                conviction = signal.get('conviction_score', 0)
                entry_price = signal.get('entry_price', 0)
                regime = signal.get('regime', 'unknown')
                
                # Color code decision
                decision_colors = {
                    'BUY_STRONG': 'bold green',
                    'BUY_WEAK': 'green',
                    'HOLD': 'yellow',
                    'SELL_WEAK': 'red',
                    'SELL_STRONG': 'bold red'
                }
                
                decision_color = decision_colors.get(decision, 'white')
                
                table.add_row(
                    date.strftime("%m/%d"),
                    symbol,
                    f"[{decision_color}]{decision}[/{decision_color}]",
                    f"{conviction:.2f}",
                    f"${entry_price:.2f}",
                    regime.replace('_', ' ').title()
                )
                
        except Exception as e:
            table = Table()
            table.add_row(f"Error loading signals: {e}")
        
        return Panel(
            table,
            title="🎯 Recent Signals",
            border_style="magenta"
        )
    
    def create_portfolio_chart(self) -> Panel:
        """Create portfolio performance chart"""
        try:
            dates, values = self.get_cached_data('chart_data', 
                                               lambda: self.data_fetcher.get_portfolio_history(self.chart_days))
            
            if not dates or not values:
                return Panel(
                    Align.center("No chart data available"),
                    title="📈 Portfolio Performance (30 days)",
                    border_style="cyan"
                )
            
            # Create chart using plotext
            plt.clear_data()
            plt.clear_figure()
            
            # Convert dates to strings for plotting
            date_strs = [d.strftime("%m/%d") if isinstance(d, datetime) else str(d) for d in dates]
            
            plt.plot(date_strs, values, marker="dot")
            plt.title("Portfolio Performance")
            plt.xlabel("Date")
            plt.ylabel("Value ($)")
            
            # Configure chart size for terminal
            plt.plotsize(60, 15)
            
            # Get the chart as string
            chart_str = plt.build()
            
        except Exception as e:
            chart_str = f"Error creating chart: {e}"
        
        return Panel(
            chart_str,
            title="📈 Portfolio Performance (30 days)",
            border_style="cyan"
        )
    
    def create_footer(self) -> Panel:
        """Create footer with controls and status"""
        controls = Text.assemble(
            ("Controls: ", "bold white"),
            ("q", "bold red"), (" = quit, ", "white"),
            ("r", "bold green"), (" = refresh, ", "white"),
            ("m", "bold blue"), (" = toggle mock data", "white")
        )
        
        status = Text(f"Last updated: {self.last_update.strftime('%H:%M:%S')} | "
                     f"Refresh: {self.refresh_interval}s | "
                     f"Data source: {'Mock' if self.data_fetcher.use_mock else 'Live'}")
        
        footer_content = Text.assemble(
            controls, "\\n",
            status
        )
        
        return Panel(
            Align.center(footer_content),
            border_style="dim white"
        )
    
    def get_cached_data(self, key: str, fetch_func):
        """Get data from cache or fetch if expired"""
        now = datetime.now()
        
        if (key in self.cache and 
            (now - self.cache[key]['timestamp']).seconds < self.cache_timeout):
            return self.cache[key]['data']
        
        try:
            data = fetch_func()
            self.cache[key] = {
                'data': data,
                'timestamp': now
            }
            return data
        except Exception as e:
            self.console.print(f"[red]Error fetching {key}: {e}[/red]")
            return self.cache.get(key, {}).get('data', {})
    
    def create_layout(self) -> Layout:
        """Create the main layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="main"),
            Layout(name="footer", size=4)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="summary", size=10),
            Layout(name="positions")
        )
        
        layout["right"].split_column(
            Layout(name="signals", size=14),
            Layout(name="chart")
        )
        
        return layout
    
    def update_layout(self, layout: Layout):
        """Update all panels in the layout"""
        try:
            layout["header"].update(self.create_header())
            layout["summary"].update(self.create_portfolio_summary())
            layout["positions"].update(self.create_positions_table())
            layout["signals"].update(self.create_signals_table())
            layout["chart"].update(self.create_portfolio_chart())
            layout["footer"].update(self.create_footer())
            
            self.last_update = datetime.now()
            
        except Exception as e:
            self.console.print(f"[red]Error updating layout: {e}[/red]")
    
    def handle_input(self):
        """Handle keyboard input in a separate thread"""
        import sys, select, termios, tty
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.cbreak(sys.stdin.fileno())
            
            while self.running:
                if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                    key = sys.stdin.read(1).lower()
                    
                    if key == 'q':
                        self.running = False
                        break
                    elif key == 'r':
                        # Clear cache to force refresh
                        self.cache.clear()
                        self.console.print("[green]Cache cleared - refreshing data...[/green]")
                    elif key == 'm':
                        # Toggle mock data mode
                        self.data_fetcher.use_mock = not self.data_fetcher.use_mock
                        self.cache.clear()
                        mode = "Mock" if self.data_fetcher.use_mock else "Live"
                        self.console.print(f"[yellow]Switched to {mode} data mode[/yellow]")
                        
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def run(self):
        """Run the monitor"""
        self.console.clear()
        self.console.print("[bold green]Starting Khazad-dûm Enhanced Monitor...[/bold green]")
        
        # Initialize data connection
        if not self.data_fetcher.use_mock:
            self.console.print("[yellow]Connecting to database...[/yellow]")
            if not self.data_fetcher.init_db_connection():
                self.console.print("[red]Failed to connect to database, using mock data[/red]")
                self.data_fetcher.use_mock = True
        
        layout = self.create_layout()
        
        # Start input handler thread
        input_thread = threading.Thread(target=self.handle_input, daemon=True)
        input_thread.start()
        
        try:
            with Live(layout, refresh_per_second=2, screen=True) as live:
                while self.running:
                    self.update_layout(layout)
                    time.sleep(self.refresh_interval)
                    
        except KeyboardInterrupt:
            self.running = False
        
        self.console.print("\\n[bold red]Monitor stopped[/bold red]")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Khazad-dûm Trading Monitor')
    parser.add_argument('--mock', action='store_true', 
                       help='Use mock data instead of live database')
    parser.add_argument('--refresh', type=int, default=5,
                       help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    monitor = EnhancedMonitor(use_mock=args.mock)
    monitor.refresh_interval = args.refresh
    
    try:
        monitor.run()
    except Exception as e:
        print(f"Error running monitor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()