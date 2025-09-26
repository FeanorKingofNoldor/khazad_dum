"""
Improved Chart Module for Cyberpunk Monitor
Handles all chart rendering with proper black background
"""

import plotext as plt
from typing import List, Optional
from datetime import datetime
from cyberpunk_theme import COLORS


class CyberpunkCharts:
    def __init__(self):
        # Set global plotext defaults
        self.configure_plotext()
    
    def configure_plotext(self):
        """Configure plotext for cyberpunk aesthetic"""
        plt.theme('dark')
        # Additional config to ensure black background
        plt.clc()  # Clear color
        
    def render_position_chart(self, 
                             symbol: str,
                             dates: List[datetime],
                             prices: List[float],
                             current_price: float,
                             stop_loss: float,
                             target_price: float,
                             entry_price: Optional[float] = None,
                             width: int = 80,
                             height: int = 20):
        """Render a position chart with black background"""
        
        # Clear everything first
        plt.clf()
        plt.clt()
        plt.clc()
        
        # Set theme and size
        plt.theme('dark')
        plt.plotsize(width, height)
        
        # Force black background
        plt.canvas_color('black')
        plt.axes_color('black')
        
        # Create x-axis as indices
        if dates and prices:
            x_vals = list(range(len(dates)))
            
            # Plot main price line
            plt.plot(x_vals, prices, 
                    label=f'{symbol}', 
                    color='cyan',
                    marker='braille')
            
            # Horizontal lines for levels
            if x_vals:
                # Stop loss (red)
                plt.plot(x_vals, [stop_loss] * len(x_vals),
                        color='red',
                        label=f'STOP: ${stop_loss:.2f}',
                        marker='hd')
                
                # Target (green)
                plt.plot(x_vals, [target_price] * len(x_vals),
                        color='green',
                        label=f'TARGET: ${target_price:.2f}',
                        marker='hd')
                
                # Current (yellow)
                plt.plot(x_vals, [current_price] * len(x_vals),
                        color='yellow',
                        label=f'CURRENT: ${current_price:.2f}',
                        marker='dot')
                
                # Entry (magenta) if provided
                if entry_price:
                    plt.plot(x_vals, [entry_price] * len(x_vals),
                            color='magenta',
                            label=f'ENTRY: ${entry_price:.2f}',
                            marker='dot')
        
        # Labels and title
        plt.title(f"◢◤ {symbol} TACTICAL OVERVIEW ◢◤")
        plt.xlabel("Time Sequence")
        plt.ylabel("Price [$]")
        
        # Show the plot
        plt.show()
    
    def render_portfolio_chart(self,
                              dates: List[datetime],
                              values: List[float],
                              width: int = 80,
                              height: int = 20):
        """Render portfolio chart with black background"""
        
        # Clear everything
        plt.clf()
        plt.clt()
        plt.clc()
        
        # Configure
        plt.theme('dark')
        plt.plotsize(width, height)
        
        # Force black background
        plt.canvas_color('black')
        plt.axes_color('black')
        
        if dates and values:
            x_vals = list(range(len(dates)))
            
            # Main portfolio line
            plt.plot(x_vals, values,
                    label='PORTFOLIO VALUE',
                    color='magenta',
                    marker='braille')
            
            # Min/Max lines
            if values:
                min_val = min(values)
                max_val = max(values)
                
                plt.plot(x_vals, [min_val] * len(x_vals),
                        color='red',
                        label=f'MIN: ${min_val:,.0f}',
                        marker='dot')
                
                plt.plot(x_vals, [max_val] * len(x_vals),
                        color='green',
                        label=f'MAX: ${max_val:,.0f}',
                        marker='dot')
        
        # Calculate performance
        if values and len(values) > 1:
            perf = ((values[-1] - values[0]) / values[0]) * 100
            title = f"◢◤ PORTFOLIO MATRIX | Return: {perf:+.2f}% ◢◤"
        else:
            title = "◢◤ PORTFOLIO MATRIX ◢◤"
        
        plt.title(title)
        plt.xlabel("Time Units")
        plt.ylabel("Value [$]")
        
        # Show the plot
        plt.show()
    
    def render_mini_chart(self, 
                         symbol: str,
                         prices: List[float],
                         width: int = 25,
                         height: int = 8):
        """Render a small sparkline chart"""
        
        plt.clf()
        plt.clc()
        
        plt.theme('dark')
        plt.plotsize(width, height)
        plt.canvas_color('black')
        plt.axes_color('black')
        
        if prices:
            plt.plot(prices, color='cyan', marker='braille')
            plt.title(symbol)
            plt.show()
    
    def clear(self):
        """Clear all plot data"""
        plt.clf()
        plt.clt()
        plt.clc()
