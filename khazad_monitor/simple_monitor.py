#!/usr/bin/env python3
"""
KHAZAD_DUM Monitor CLI - Simple Version
Simplified version with basic input handling
"""

import time
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import print

from data_fetcher import DataFetcher
from charts import ChartRenderer
from config import REFRESH_RATE, USE_MOCK_DATA


class SimpleMonitor:
    def __init__(self):
        self.console = Console()
        self.data = DataFetcher()
        self.charts = ChartRenderer()
        self.running = True
        
    def show_header(self):
        """Display header"""
        self.console.clear()
        self.console.rule("[bold cyan]KHAZAD_DUM POSITION MONITOR[/bold cyan]")
        
        if USE_MOCK_DATA:
            self.console.print("[yellow]⚠ Running with MOCK DATA[/yellow]\n")
    
    def show_menu(self):
        """Display main menu"""
        menu_text = """
[bold cyan]Main Menu[/bold cyan]

[1] 📊 Portfolio Overview - View total portfolio chart
[2] 📈 Single Position - View position with stop/target lines  
[3] 📋 Positions Table - View all positions
[4] 🔄 Refresh Data
[5] ❌ Quit

"""
        print(Panel(menu_text, border_style="cyan"))
        
        choice = Prompt.ask(
            "Select option",
            choices=["1", "2", "3", "4", "5"],
            default="1"
        )
        
        return choice
    
    def show_portfolio(self):
        """Show portfolio chart"""
        self.show_header()
        print("[bold]Portfolio Value History[/bold]\n")
        
        dates, values = self.data.get_portfolio_value_history()
        
        if dates and values:
            chart = self.charts.render_portfolio_chart(dates, values)
            print(chart)
            
            # Show summary
            current_value = values[-1] if values else 0
            start_value = values[0] if values else 0
            change = current_value - start_value
            change_pct = (change / start_value * 100) if start_value else 0
            
            summary = f"""
Current Value: ${current_value:,.2f}
Period Change: ${change:+,.2f} ({change_pct:+.2f}%)
"""
            print(Panel(summary, title="Summary", border_style="green"))
        else:
            print("[red]No portfolio data available[/red]")
        
        input("\nPress Enter to continue...")
    
    def show_position(self):
        """Show single position chart"""
        self.show_header()
        
        # Get available positions
        positions = self.data.get_portfolio_positions()
        
        if not positions:
            print("[red]No positions found[/red]")
            input("Press Enter to continue...")
            return
        
        # Show position list
        print("[bold]Select Position:[/bold]\n")
        for i, pos in enumerate(positions, 1):
            pnl = pos.get('pnl_percentage', 0)
            color = "green" if pnl > 0 else "red" if pnl < 0 else "white"
            print(f"  [{i}] {pos['symbol']:6} - Current: ${pos['current_price']:>7.2f} - P&L: [{color}]{pnl:+.2f}%[/{color}]")
        
        # Get selection
        print()
        choice = Prompt.ask(
            "Select position",
            choices=[str(i) for i in range(1, len(positions) + 1)]
        )
        
        selected_pos = positions[int(choice) - 1]
        symbol = selected_pos['symbol']
        
        # Get and display chart
        self.show_header()
        print(f"[bold]{symbol} Position Chart[/bold]\n")
        
        dates, prices = self.data.get_position_history(symbol)
        
        if dates and prices:
            chart = self.charts.render_position_chart(
                symbol=symbol,
                dates=dates,
                prices=prices,
                current_price=selected_pos['current_price'],
                stop_loss=selected_pos['stop_loss'],
                target_price=selected_pos['target_price'],
                entry_price=selected_pos.get('entry_price')
            )
            print(chart)
            
            # Show position details
            details = f"""
Symbol:        {symbol}
Shares:        {selected_pos['shares']}
Entry Price:   ${selected_pos['entry_price']:.2f}
Current Price: ${selected_pos['current_price']:.2f}
Stop Loss:     ${selected_pos['stop_loss']:.2f} [red](Risk: ${(selected_pos['entry_price'] - selected_pos['stop_loss']) * selected_pos['shares']:,.2f})[/red]
Target Price:  ${selected_pos['target_price']:.2f} [green](Reward: ${(selected_pos['target_price'] - selected_pos['entry_price']) * selected_pos['shares']:,.2f})[/green]
Unrealized P&L: ${selected_pos.get('unrealized_pnl', 0):+,.2f} ({selected_pos.get('pnl_percentage', 0):+.2f}%)
"""
            print(Panel(details, title="Position Details", border_style="cyan"))
        else:
            print("[red]No price history available[/red]")
        
        input("\nPress Enter to continue...")
    
    def show_positions_table(self):
        """Show all positions in a table"""
        self.show_header()
        print("[bold]All Positions[/bold]\n")
        
        table = Table(title=None, show_header=True, header_style="bold cyan")
        
        # Add columns
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Shares", justify="right")
        table.add_column("Entry", justify="right", style="dim")
        table.add_column("Current", justify="right")
        table.add_column("Stop", justify="right", style="red")
        table.add_column("Target", justify="right", style="green") 
        table.add_column("P&L ($)", justify="right")
        table.add_column("P&L (%)", justify="right")
        table.add_column("Risk:Reward", justify="center")
        
        # Get positions
        positions = self.data.get_portfolio_positions()
        
        total_pnl = 0
        
        for pos in positions:
            pnl_value = pos.get('unrealized_pnl', 0)
            pnl_pct = pos.get('pnl_percentage', 0)
            total_pnl += pnl_value
            
            # Calculate risk:reward ratio
            risk = pos['entry_price'] - pos['stop_loss']
            reward = pos['target_price'] - pos['entry_price']
            rr_ratio = f"1:{reward/risk:.1f}" if risk > 0 else "N/A"
            
            # Color code P&L
            pnl_color = "green" if pnl_value > 0 else "red" if pnl_value < 0 else "white"
            
            table.add_row(
                pos['symbol'],
                str(pos['shares']),
                f"${pos['entry_price']:.2f}",
                f"${pos['current_price']:.2f}",
                f"${pos['stop_loss']:.2f}",
                f"${pos['target_price']:.2f}",
                f"[{pnl_color}]${pnl_value:+,.2f}[/{pnl_color}]",
                f"[{pnl_color}]{pnl_pct:+.2f}%[/{pnl_color}]",
                rr_ratio
            )
        
        self.console.print(table)
        
        # Show summary
        summary_text = f"""
[bold]Portfolio Summary:[/bold]
Total Positions: {len(positions)}
Total Unrealized P&L: [{'green' if total_pnl > 0 else 'red'}]${total_pnl:+,.2f}[/{'green' if total_pnl > 0 else 'red'}]
"""
        print(Panel(summary_text, border_style="yellow"))
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main loop"""
        try:
            while self.running:
                self.show_header()
                choice = self.show_menu()
                
                if choice == "1":
                    self.show_portfolio()
                elif choice == "2":
                    self.show_position()
                elif choice == "3":
                    self.show_positions_table()
                elif choice == "4":
                    self.console.print("\n[green]✓ Data refreshed![/green]")
                    time.sleep(1)
                elif choice == "5":
                    if Confirm.ask("\nAre you sure you want to quit?"):
                        self.running = False
                        
        except KeyboardInterrupt:
            print("\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            print(f"\n[red]Error: {e}[/red]")
        finally:
            self.data.disconnect()
            print("\n[cyan]Monitor stopped. Goodbye![/cyan]")


if __name__ == "__main__":
    monitor = SimpleMonitor()
    monitor.run()
