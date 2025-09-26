#!/usr/bin/env python3
"""
KHAZAD_DUM Monitor CLI
Simple terminal monitoring for portfolio positions with stop loss and target visualization
"""

import sys
import time
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text

from data_fetcher import DataFetcher
from charts import ChartRenderer
from config import REFRESH_RATE, USE_MOCK_DATA


class KhazadMonitor:
    def __init__(self):
        self.console = Console()
        self.data = DataFetcher()
        self.charts = ChartRenderer()
        self.current_view = 'menu'  # menu, portfolio, position, positions_table
        self.selected_symbol = None
        self.running = True
        self.auto_refresh = REFRESH_RATE > 0
        self.last_refresh = time.time()
        
    def create_header(self) -> Panel:
        """Create the header panel"""
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create header text
        header_text = Text()
        header_text.append("KHAZAD_DUM MONITOR", style="bold cyan")
        header_text.append(f"\n{current_time}", style="dim")
        
        if USE_MOCK_DATA:
            header_text.append(" | MOCK DATA", style="yellow")
        
        # Add hotkey help
        hotkeys = "\n[P]ortfolio  [S]ingle  [T]able  [R]efresh  [A]uto-refresh  [Q]uit"
        header_text.append(hotkeys, style="dim cyan")
        
        return Panel(
            Align.center(header_text),
            border_style="cyan",
            height=5
        )
    
    def create_positions_table(self) -> Table:
        """Create a table showing all positions"""
        table = Table(title="Portfolio Positions", title_style="bold cyan")
        
        # Add columns
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Shares", justify="right")
        table.add_column("Entry", justify="right", style="dim")
        table.add_column("Current", justify="right")
        table.add_column("Stop", justify="right", style="red")
        table.add_column("Target", justify="right", style="green")
        table.add_column("P&L ($)", justify="right")
        table.add_column("P&L (%)", justify="right")
        
        # Get positions data
        positions = self.data.get_portfolio_positions()
        
        for pos in positions:
            # Determine P&L color
            pnl_value = pos.get('unrealized_pnl', 0)
            pnl_pct = pos.get('pnl_percentage', 0)
            
            pnl_color = "green" if pnl_value > 0 else "red" if pnl_value < 0 else "white"
            
            table.add_row(
                pos['symbol'],
                str(pos['shares']),
                f"${pos['entry_price']:.2f}",
                f"${pos['current_price']:.2f}",
                f"${pos['stop_loss']:.2f}",
                f"${pos['target_price']:.2f}",
                f"${pnl_value:+,.2f}",
                f"{pnl_pct:+.2f}%",
                style=pnl_color if abs(pnl_value) > 100 else None
            )
        
        # Add summary row
        total_pnl = sum(p.get('unrealized_pnl', 0) for p in positions)
        table.add_row(
            "TOTAL", "", "", "", "", "",
            f"${total_pnl:+,.2f}",
            "",
            style="bold yellow"
        )
        
        return table
    
    def get_portfolio_chart(self) -> str:
        """Get portfolio value chart"""
        dates, values = self.data.get_portfolio_value_history()
        return self.charts.render_portfolio_chart(dates, values)
    
    def get_position_chart(self, symbol: str) -> str:
        """Get single position chart"""
        # Get position details
        position = self.data.get_position_details(symbol)
        if not position:
            return f"Position {symbol} not found"
        
        # Get price history
        dates, prices = self.data.get_position_history(symbol)
        
        # Render chart
        return self.charts.render_position_chart(
            symbol=symbol,
            dates=dates,
            prices=prices,
            current_price=position['current_price'],
            stop_loss=position['stop_loss'],
            target_price=position['target_price'],
            entry_price=position.get('entry_price')
        )
    
    def create_main_content(self) -> Panel:
        """Create the main content panel based on current view"""
        content = ""
        title = "Menu"
        
        if self.current_view == 'menu':
            title = "Main Menu"
            content = """
Welcome to KHAZAD_DUM Monitor!

Select an option using the hotkeys:

[P] - Portfolio Overview
      View total portfolio value chart
      
[S] - Single Position Chart
      View detailed chart for one position
      
[T] - Positions Table
      View all positions in table format
      
[R] - Refresh Data
      Manually refresh all data
      
[A] - Toggle Auto-refresh
      Currently: """ + ("ON" if self.auto_refresh else "OFF") + """
      
[Q] - Quit
      Exit the monitor

Press any key to select...
            """
            
        elif self.current_view == 'portfolio':
            title = "Portfolio Overview"
            content = self.get_portfolio_chart()
            
        elif self.current_view == 'position':
            title = f"Position: {self.selected_symbol}"
            if self.selected_symbol:
                content = self.get_position_chart(self.selected_symbol)
            else:
                content = "No symbol selected"
                
        elif self.current_view == 'positions_table':
            title = "All Positions"
            # Return the table directly instead of as string
            return Panel(
                self.create_positions_table(),
                title=title,
                border_style="blue",
                expand=True
            )
        
        # For text content, wrap in panel
        return Panel(
            content,
            title=title,
            border_style="blue",
            expand=True
        )
    
    def create_footer(self) -> Panel:
        """Create footer with status info"""
        footer_text = []
        
        if self.auto_refresh:
            next_refresh = REFRESH_RATE - (time.time() - self.last_refresh)
            footer_text.append(f"Auto-refresh in: {int(next_refresh)}s")
        else:
            footer_text.append("Auto-refresh: OFF")
        
        footer_text.append(f"View: {self.current_view.upper()}")
        
        if self.selected_symbol:
            footer_text.append(f"Symbol: {self.selected_symbol}")
        
        return Panel(
            " | ".join(footer_text),
            style="dim",
            height=3
        )
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input. Returns True to continue, False to quit"""
        key = key.lower()
        
        if key == 'q':
            return False
            
        elif key == 'p':
            self.current_view = 'portfolio'
            
        elif key == 's':
            # Ask for symbol
            positions = self.data.get_portfolio_positions()
            symbols = [p['symbol'] for p in positions]
            
            self.console.print("\nAvailable symbols: " + ", ".join(symbols))
            symbol = Prompt.ask("Enter symbol", choices=symbols + ['cancel'])
            
            if symbol != 'cancel':
                self.selected_symbol = symbol.upper()
                self.current_view = 'position'
                
        elif key == 't':
            self.current_view = 'positions_table'
            
        elif key == 'r':
            self.last_refresh = time.time()
            self.console.print("Data refreshed!", style="green")
            
        elif key == 'a':
            self.auto_refresh = not self.auto_refresh
            self.last_refresh = time.time()
            
        elif key == 'm':
            self.current_view = 'menu'
        
        return True
    
    def run(self):
        """Main run loop"""
        self.console.clear()
        self.console.print("[bold cyan]Starting KHAZAD_DUM Monitor...[/bold cyan]\n")
        
        # Check if we're in mock mode
        if USE_MOCK_DATA:
            self.console.print("[yellow]Running in MOCK DATA mode[/yellow]")
            self.console.print("To use real data, configure database in .env file\n")
        
        try:
            # Create layout
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=5),
                Layout(name="body"),
                Layout(name="footer", size=3)
            )
            
            # Main loop with Live display
            with Live(layout, refresh_per_second=4, screen=True) as live:
                while self.running:
                    # Update layout
                    layout["header"].update(self.create_header())
                    layout["body"].update(self.create_main_content())
                    layout["footer"].update(self.create_footer())
                    
                    # Check for auto-refresh
                    if self.auto_refresh and (time.time() - self.last_refresh) > REFRESH_RATE:
                        self.last_refresh = time.time()
                    
                    # Non-blocking input check
                    # For now, using simple input - in production you'd use a proper async input handler
                    import select
                    import termios
                    import tty
                    
                    # Set terminal to raw mode for single key input
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        
                        # Check if input is available (non-blocking)
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            key = sys.stdin.read(1)
                            if not self.handle_input(key):
                                self.running = False
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    
                    time.sleep(0.1)  # Small delay to prevent CPU spinning
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
        finally:
            self.data.disconnect()
            self.console.print("\n[cyan]Monitor stopped. Goodbye![/cyan]")


if __name__ == "__main__":
    monitor = KhazadMonitor()
    monitor.run()
