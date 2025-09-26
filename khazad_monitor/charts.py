"""
Chart rendering module using plotext
"""

import plotext as plt
from typing import List, Optional, Tuple
from datetime import datetime

from config import COLORS, CHART_HEIGHT, CHART_WIDTH


class ChartRenderer:
    def __init__(self):
        # Set default plotext settings
        plt.theme('dark')
        
    def render_position_chart(self, 
                             symbol: str,
                             dates: List[datetime],
                             prices: List[float],
                             current_price: float,
                             stop_loss: float,
                             target_price: float,
                             entry_price: Optional[float] = None) -> str:
        """Render a single position chart with stop loss and target lines"""
        
        plt.clear_figure()
        plt.clear_color()
        plt.clear_data()
        
        # Configure size
        plt.plotsize(CHART_WIDTH, CHART_HEIGHT)
        
        # Use numeric x-axis with date labels
        x_values = list(range(len(dates))) if dates else []
        
        # Main price line
        if x_values and prices:
            plt.plot(x_values, prices, 
                    label=f'{symbol} Price', 
                    color=COLORS['price_line'],
                    marker='braille')
        
        # Horizontal lines for stop, target, and current
        if x_values:
            # Stop loss line
            plt.plot(x_values, 
                    [stop_loss] * len(x_values),
                    label=f'Stop: ${stop_loss:.2f}',
                    color=COLORS['stop_loss'],
                    marker='hd')
            
            # Target price line
            plt.plot(x_values,
                    [target_price] * len(x_values),
                    label=f'Target: ${target_price:.2f}',
                    color=COLORS['target'],
                    marker='hd')
            
            # Current price line (dotted)
            plt.plot(x_values,
                    [current_price] * len(x_values),
                    label=f'Current: ${current_price:.2f}',
                    color=COLORS['current'],
                    marker='dot')
            
            # Entry price line if provided
            if entry_price:
                plt.plot(x_values,
                        [entry_price] * len(x_values),
                        label=f'Entry: ${entry_price:.2f}',
                        color='white',
                        marker='dot')
        
        # Calculate P&L for title
        if entry_price and current_price:
            pnl = ((current_price - entry_price) / entry_price) * 100
            pnl_str = f" | P&L: {pnl:+.2f}%"
        else:
            pnl_str = ""
        
        plt.title(f"{symbol} Position Monitor{pnl_str}")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        
        # Build and return the chart as string
        return plt.build()
    
    def render_portfolio_chart(self,
                              dates: List[datetime],
                              values: List[float]) -> str:
        """Render portfolio value chart"""
        
        plt.clear_figure()
        plt.clear_color()
        plt.clear_data()
        
        plt.plotsize(CHART_WIDTH, CHART_HEIGHT)
        
        # Use numeric indices
        x_values = list(range(len(dates))) if dates else []
        
        if x_values and values:
            plt.plot(x_values, values,
                    label='Portfolio Value',
                    color=COLORS['portfolio'],
                    marker='braille')
            
            # Add min/max lines
            if values:
                min_val = min(values)
                max_val = max(values)
                current_val = values[-1] if values else 0
                
                # Show high/low lines
                plt.plot(x_values,
                        [min_val] * len(x_values),
                        label=f'Low: ${min_val:,.0f}',
                        color='red',
                        marker='dot')
                
                plt.plot(x_values,
                        [max_val] * len(x_values),
                        label=f'High: ${max_val:,.0f}',
                        color='green',
                        marker='dot')
        
        # Calculate performance
        if values and len(values) > 1:
            performance = ((values[-1] - values[0]) / values[0]) * 100
            perf_str = f" | Period Return: {performance:+.2f}%"
        else:
            perf_str = ""
        
        plt.title(f"Portfolio Value{perf_str}")
        plt.xlabel("Date")
        plt.ylabel("Value ($)")
        
        return plt.build()
    
    def render_multi_position_chart(self,
                                   positions: List[dict],
                                   days: int = 7) -> str:
        """Render sparkline-style mini charts for multiple positions"""
        
        plt.clear_figure()
        plt.clear_color()
        plt.clear_data()
        
        plt.plotsize(CHART_WIDTH, CHART_HEIGHT)
        plt.subplots(1, min(3, len(positions)))
        
        for i, pos in enumerate(positions[:3]):  # Max 3 charts
            plt.subplot(1, i + 1)
            
            # Simple price line
            symbol = pos['symbol']
            current = pos['current_price']
            entry = pos['entry_price']
            
            # Generate simple trend data (mock)
            prices = [entry + (current - entry) * (j/10) + 
                     (j % 2) * 2 for j in range(10)]
            
            plt.plot(prices, color=COLORS['price_line'])
            
            # P&L in title
            pnl = ((current - entry) / entry) * 100
            color_marker = "🟢" if pnl > 0 else "🔴"
            plt.title(f"{symbol} {pnl:+.1f}%")
        
        plt.show()
        return plt.build()
    
    def clear(self):
        """Clear the current plot"""
        plt.clear_figure()
        plt.clear_color()
        plt.clear_data()
