#!/usr/bin/env python3
"""
KHAZAD_DUM Cyberpunk Monitor v2.0
Arrow-driven menu with command mode and file management
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.columns import Columns
from rich.tree import Tree
from rich.live import Live
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich import box

from data_fetcher import DataFetcher
from cyberpunk_theme import COLORS, ASCII_ART, ICONS, BOX
from cyberpunk_charts import CyberpunkCharts

# Try to import keyboard navigation
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.application import Application
    from prompt_toolkit.layout.containers import Window
    from prompt_toolkit.layout import Layout as PTLayout
    from prompt_toolkit.formatted_text import HTML
    PROMPT_TOOLKIT = True
except ImportError:
    PROMPT_TOOLKIT = False
    print("Note: Install prompt-toolkit for better navigation: pip install prompt-toolkit")


class CyberpunkMonitor:
    def __init__(self):
        self.console = Console()
        self.data = DataFetcher()
        self.charts = CyberpunkCharts()
        self.current_menu = 'main'
        self.selected_index = 0
        self.menu_items = []
        self.command_mode = False
        self.command_history = []
        self.file_structure = self.init_file_structure()
        self.selected_symbol = None
        self.running = True
        
    def init_file_structure(self):
        """Initialize the file system structure"""
        return {
            'reports': {
                'daily': [],
                'weekly': [],
                'analysis': []
            },
            'exports': {
                'csv': [],
                'json': [],
                'pdf': []
            },
            'charts': {
                'portfolio': [],
                'positions': []
            },
            'logs': {
                'trades': [],
                'system': []
            }
        }
    
    def clear_screen(self):
        """Clear terminal and show header"""
        self.console.clear()
        self.show_cyberpunk_header()
    
    def show_cyberpunk_header(self):
        """Display cyberpunk themed header"""
        # Create gradient effect for logo
        logo_lines = ASCII_ART['logo'].strip().split('\n')
        gradient_colors = COLORS['gradient']
        
        for i, line in enumerate(logo_lines):
            color_index = min(i, len(gradient_colors) - 1)
            color = gradient_colors[color_index]
            self.console.print(line, style=color, justify="center")
        
        # Status bar
        status_text = Text()
        status_text.append("◢◤ ", style="bright_cyan")
        status_text.append(f"SYSTEM ONLINE", style="bright_green bold")
        status_text.append(" ◢◤ ", style="bright_cyan")
        status_text.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), style="bright_magenta")
        status_text.append(" ◢◤ ", style="bright_cyan")
        
        if self.data.use_mock:
            status_text.append("MOCK MODE", style="yellow bold")
        else:
            status_text.append("LIVE DATA", style="green bold")
        
        self.console.print(Panel(
            status_text,
            style="bright_cyan",
            box=box.DOUBLE,
            padding=(0, 2)
        ))
    
    def render_menu(self, title: str, items: List[Tuple[str, str]], selected: int = 0):
        """Render an arrow-navigatable menu"""
        menu_text = Text()
        menu_text.append(f"\n{title}\n\n", style="bright_cyan bold")
        
        for i, (icon, label) in enumerate(items):
            if i == selected:
                # Selected item - animated cursor
                menu_text.append("  ► ", style="bright_magenta bold blink")
                menu_text.append(f"{icon} {label}", style="bright_cyan bold")
                menu_text.append(" ◄", style="bright_magenta bold blink")
            else:
                menu_text.append("    ", style="")
                menu_text.append(f"{icon} {label}", style="grey58")
            menu_text.append("\n")
        
        menu_text.append("\n", style="")
        menu_text.append("─" * 50, style="grey35")
        menu_text.append("\n[↑↓] Navigate  [Enter] Select  [C] Command  [Q] Quit", style="grey50")
        
        return Panel(
            menu_text,
            style="bright_cyan",
            border_style="bright_cyan",
            box=box.HEAVY,
            title=f"◢◤ {title} ◢◤",
            title_align="center"
        )
    
    def main_menu(self):
        """Main menu interface"""
        self.menu_items = [
            (ICONS['portfolio'], "Portfolio Overview"),
            (ICONS['position'], "Single Position Analysis"),
            (ICONS['table'], "Positions Table"),
            (ICONS['files'], "File Manager"),
            (ICONS['command'], "Command Mode"),
            (ICONS['refresh'], "Refresh Data"),
            (ICONS['settings'], "Settings"),
            (ICONS['quit'], "Exit System")
        ]
        
        self.clear_screen()
        menu = self.render_menu("MAIN CONTROL PANEL", self.menu_items, self.selected_index)
        self.console.print(menu)
        return self.selected_index
    
    def navigate_menu(self) -> int:
        """Handle arrow key navigation"""
        import termios
        import tty
        import sys
        
        def get_key():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                if key == '\x1b':  # ESC sequence
                    key += sys.stdin.read(2)
                return key
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        while True:
            self.main_menu()
            key = get_key()
            
            if key == '\x1b[A':  # Up arrow
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif key == '\x1b[B':  # Down arrow
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif key == '\r' or key == '\n':  # Enter
                return self.selected_index
            elif key.lower() == 'c':  # Command mode
                self.command_mode_interface()
            elif key.lower() == 'q':  # Quit
                return len(self.menu_items) - 1  # Last item is quit
    
    def render_improved_chart(self, symbol: str = None):
        """Render a better formatted chart"""
        self.clear_screen()
        
        if symbol:
            # Single position chart
            position = self.data.get_position_details(symbol)
            if not position:
                self.console.print(f"[red]Position {symbol} not found[/red]")
                return
            
            dates, prices = self.data.get_position_history(symbol)
            
            # Render using the new chart module
            self.charts.render_position_chart(
                symbol=symbol,
                dates=dates,
                prices=prices,
                current_price=position['current_price'],
                stop_loss=position['stop_loss'],
                target_price=position['target_price'],
                entry_price=position.get('entry_price')
            )
            
            # Show position details in cyberpunk style
            self.show_position_details_cyberpunk(position)
        else:
            # Portfolio chart
            dates, values = self.data.get_portfolio_value_history()
            
            # Render using the new chart module
            self.charts.render_portfolio_chart(dates, values)
    
    def show_position_details_cyberpunk(self, position: dict):
        """Show position details in cyberpunk style"""
        # Create a cyberpunk data table
        detail_table = Table(
            title="POSITION PARAMETERS",
            style="bright_cyan",
            box=box.DOUBLE_EDGE,
            title_style="bright_magenta bold"
        )
        
        detail_table.add_column("PARAMETER", style="bright_cyan")
        detail_table.add_column("VALUE", style="bright_green")
        detail_table.add_column("STATUS", style="bright_yellow")
        
        # Calculate risk/reward
        risk = (position['entry_price'] - position['stop_loss']) * position['shares']
        reward = (position['target_price'] - position['entry_price']) * position['shares']
        ratio = reward / risk if risk > 0 else 0
        
        # P&L status
        pnl = position.get('unrealized_pnl', 0)
        pnl_status = "▲ PROFIT" if pnl > 0 else "▼ LOSS" if pnl < 0 else "◆ NEUTRAL"
        pnl_color = "bright_green" if pnl > 0 else "bright_red" if pnl < 0 else "grey50"
        
        detail_table.add_row("SHARES", str(position['shares']), "ACTIVE")
        detail_table.add_row("ENTRY", f"${position['entry_price']:.2f}", "EXECUTED")
        detail_table.add_row("CURRENT", f"${position['current_price']:.2f}", "LIVE")
        detail_table.add_row("STOP LOSS", f"${position['stop_loss']:.2f}", "ARMED")
        detail_table.add_row("TARGET", f"${position['target_price']:.2f}", "PENDING")
        detail_table.add_row("RISK", f"${risk:.2f}", "CALCULATED")
        detail_table.add_row("REWARD", f"${reward:.2f}", "PROJECTED")
        detail_table.add_row("R:R RATIO", f"1:{ratio:.2f}", "OPTIMAL" if ratio > 2 else "SUBOPTIMAL")
        
        self.console.print(detail_table)
        
        # P&L display
        pnl_panel = Panel(
            Text(f"{pnl_status}: ${pnl:+,.2f} ({position.get('pnl_percentage', 0):+.2f}%)", 
                 style=pnl_color + " bold"),
            style=pnl_color,
            box=box.DOUBLE
        )
        self.console.print(pnl_panel)
    
    def file_manager(self):
        """File manager interface"""
        self.clear_screen()
        
        tree = Tree("📁 KHAZAD_DUM FILE SYSTEM", style="bright_cyan bold")
        
        for folder, subfolders in self.file_structure.items():
            folder_branch = tree.add(f"📁 {folder.upper()}", style="bright_magenta")
            
            if isinstance(subfolders, dict):
                for subfolder, files in subfolders.items():
                    sub_branch = folder_branch.add(f"📂 {subfolder}", style="cyan")
                    
                    # Add some mock files
                    if not files:
                        if subfolder == 'daily':
                            files = ['report_2024_01_15.pdf', 'report_2024_01_14.pdf']
                        elif subfolder == 'csv':
                            files = ['positions_export.csv', 'trades_export.csv']
                    
                    for file in files:
                        sub_branch.add(f"📄 {file}", style="grey70")
        
        file_panel = Panel(
            tree,
            title="◢◤ FILE SYSTEM NAVIGATOR ◢◤",
            style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        
        self.console.print(file_panel)
        
        # File operations menu
        ops_text = """
[D] Download Reports
[E] Export Data
[G] Generate Chart
[L] View Logs
[B] Back to Main
        """
        
        ops_panel = Panel(
            ops_text,
            title="FILE OPERATIONS",
            style="bright_magenta",
            box=box.HEAVY
        )
        
        self.console.print(ops_panel)
    
    def command_mode_interface(self):
        """Command line interface mode"""
        self.clear_screen()
        
        self.console.print(Panel(
            ASCII_ART['matrix'],
            style="bright_green",
            box=box.DOUBLE
        ))
        
        self.console.print("[bright_cyan]◢◤ COMMAND MODE ACTIVATED ◢◤[/bright_cyan]\n")
        self.console.print("Available commands:", style="bright_magenta")
        
        commands = {
            'analyze [symbol]': 'Run full analysis on symbol',
            'export [type]': 'Export data (csv/json/pdf)',
            'chart [symbol]': 'Generate chart for symbol',
            'risk': 'Show risk metrics',
            'scan': 'Scan for opportunities',
            'history': 'Show command history',
            'clear': 'Clear screen',
            'exit': 'Exit command mode'
        }
        
        for cmd, desc in commands.items():
            self.console.print(f"  [bright_green]{cmd:20}[/bright_green] - {desc}", style="grey70")
        
        self.console.print("\n[bright_cyan]◢◤━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◤◢[/bright_cyan]")
        
        while True:
            try:
                command = Prompt.ask("\n[bright_magenta]khazad_dum>[/bright_magenta]")
                
                if command == 'exit':
                    break
                elif command == 'clear':
                    self.clear_screen()
                elif command.startswith('analyze'):
                    parts = command.split()
                    if len(parts) > 1:
                        self.render_improved_chart(parts[1].upper())
                        input("\nPress Enter to continue...")
                elif command == 'risk':
                    self.show_risk_metrics()
                elif command == 'history':
                    for cmd in self.command_history[-10:]:
                        self.console.print(f"  {cmd}", style="grey50")
                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")
                
                self.command_history.append(command)
                
            except KeyboardInterrupt:
                break
    
    def show_risk_metrics(self):
        """Display risk metrics in cyberpunk style"""
        positions = self.data.get_portfolio_positions()
        
        risk_table = Table(
            title="RISK ANALYSIS MATRIX",
            style="bright_red",
            box=box.DOUBLE_EDGE,
            title_style="bright_red bold"
        )
        
        risk_table.add_column("METRIC", style="bright_cyan")
        risk_table.add_column("VALUE", style="bright_yellow")
        risk_table.add_column("THRESHOLD", style="bright_green")
        risk_table.add_column("STATUS", style="bright_magenta")
        
        # Calculate metrics
        total_risk = sum((p['entry_price'] - p['stop_loss']) * p['shares'] 
                        for p in positions)
        total_value = sum(p['current_price'] * p['shares'] for p in positions)
        risk_percentage = (total_risk / total_value * 100) if total_value > 0 else 0
        
        risk_table.add_row(
            "Total Risk",
            f"${total_risk:,.2f}",
            "$10,000",
            "⚠ WARNING" if total_risk > 10000 else "✓ SAFE"
        )
        
        risk_table.add_row(
            "Risk %",
            f"{risk_percentage:.2f}%",
            "5%",
            "⚠ HIGH" if risk_percentage > 5 else "✓ NORMAL"
        )
        
        risk_table.add_row(
            "Positions",
            str(len(positions)),
            "10",
            "✓ OK" if len(positions) < 10 else "⚠ DIVERSIFY"
        )
        
        self.console.print(risk_table)
    
    def improved_positions_table(self):
        """Enhanced positions table with cyberpunk styling"""
        self.clear_screen()
        
        table = Table(
            title="◢◤ POSITION MATRIX ◢◤",
            style="bright_cyan",
            box=box.DOUBLE_EDGE,
            title_style="bright_magenta bold",
            header_style="bright_cyan bold",
            show_lines=True
        )
        
        # Columns with icons
        table.add_column("📊 SYMBOL", style="bright_cyan", no_wrap=True)
        table.add_column("📦 SHARES", justify="right", style="bright_yellow")
        table.add_column("💵 ENTRY", justify="right", style="grey70")
        table.add_column("💰 CURRENT", justify="right", style="bright_green")
        table.add_column("🛑 STOP", justify="right", style="bright_red")
        table.add_column("🎯 TARGET", justify="right", style="bright_green")
        table.add_column("📈 P&L", justify="right")
        table.add_column("📊 %", justify="right")
        table.add_column("⚡ SIGNAL", justify="center")
        
        positions = self.data.get_portfolio_positions()
        
        for pos in positions:
            pnl = pos.get('unrealized_pnl', 0)
            pnl_pct = pos.get('pnl_percentage', 0)
            
            # Color coding
            pnl_style = "bright_green" if pnl > 0 else "bright_red" if pnl < 0 else "grey50"
            
            # Signal generation
            if pos['current_price'] < pos['stop_loss'] * 1.05:
                signal = "⚠ NEAR STOP"
                signal_style = "bright_red bold blink"
            elif pos['current_price'] > pos['target_price'] * 0.95:
                signal = "🎯 NEAR TARGET"
                signal_style = "bright_green bold blink"
            else:
                signal = "▶ ACTIVE"
                signal_style = "bright_cyan"
            
            table.add_row(
                pos['symbol'],
                str(pos['shares']),
                f"${pos['entry_price']:.2f}",
                f"${pos['current_price']:.2f}",
                f"${pos['stop_loss']:.2f}",
                f"${pos['target_price']:.2f}",
                Text(f"${pnl:+,.2f}", style=pnl_style),
                Text(f"{pnl_pct:+.2f}%", style=pnl_style),
                Text(signal, style=signal_style)
            )
        
        # Total row
        total_pnl = sum(p.get('unrealized_pnl', 0) for p in positions)
        total_style = "bright_green bold" if total_pnl > 0 else "bright_red bold"
        
        table.add_row(
            Text("ΣTOTAL", style="bright_magenta bold"),
            "", "", "", "", "",
            Text(f"${total_pnl:+,.2f}", style=total_style),
            "",
            Text("◢◤", style="bright_cyan")
        )
        
        self.console.print(table)
        
        # System status
        status_panel = Panel(
            f"[bright_green]● SYSTEM OPERATIONAL[/bright_green] | "
            f"[bright_cyan]POSITIONS: {len(positions)}[/bright_cyan] | "
            f"[bright_magenta]REFRESH: AUTO[/bright_magenta] | "
            f"[bright_yellow]MODE: TACTICAL[/bright_yellow]",
            style="bright_cyan",
            box=box.HEAVY
        )
        
        self.console.print(status_panel)
    
    def run(self):
        """Main run loop"""
        try:
            while self.running:
                selection = self.navigate_menu()
                
                if selection == 0:  # Portfolio
                    self.render_improved_chart()
                    input("\nPress Enter to continue...")
                elif selection == 1:  # Single Position
                    self.clear_screen()
                    positions = self.data.get_portfolio_positions()
                    symbols = [p['symbol'] for p in positions]
                    
                    self.console.print("[bright_cyan]Select Symbol:[/bright_cyan]")
                    for i, sym in enumerate(symbols):
                        self.console.print(f"  [{i+1}] {sym}", style="bright_magenta")
                    
                    choice = Prompt.ask("Select", choices=[str(i+1) for i in range(len(symbols))])
                    symbol = symbols[int(choice)-1]
                    self.render_improved_chart(symbol)
                    input("\nPress Enter to continue...")
                elif selection == 2:  # Table
                    self.improved_positions_table()
                    input("\nPress Enter to continue...")
                elif selection == 3:  # Files
                    self.file_manager()
                    input("\nPress Enter to continue...")
                elif selection == 4:  # Command Mode
                    self.command_mode_interface()
                elif selection == 5:  # Refresh
                    self.console.print("[bright_green]◢◤ DATA REFRESHED ◢◤[/bright_green]")
                    time.sleep(1)
                elif selection == 6:  # Settings
                    self.console.print("[bright_yellow]Settings not implemented yet[/bright_yellow]")
                    time.sleep(1)
                elif selection == 7:  # Quit
                    if Confirm.ask("\n[bright_red]TERMINATE SYSTEM?[/bright_red]"):
                        self.running = False
                        
        except KeyboardInterrupt:
            self.console.print("\n[bright_red]◢◤ EMERGENCY SHUTDOWN ◢◤[/bright_red]")
        finally:
            self.data.disconnect()
            self.console.print("\n[bright_cyan]◢◤ SYSTEM OFFLINE ◢◤[/bright_cyan]")


if __name__ == "__main__":
    monitor = CyberpunkMonitor()
    monitor.run()
