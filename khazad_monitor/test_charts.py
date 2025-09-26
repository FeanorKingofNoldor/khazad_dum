#!/usr/bin/env python3
"""
Test Chart Rendering with Black Background
"""

import os
import sys

# Set USE_MOCK to True for testing
os.environ['USE_MOCK'] = 'True'

from cyberpunk_charts import CyberpunkCharts
from data_fetcher import DataFetcher


def test_charts():
    """Test chart rendering"""
    print("\033[2J\033[H")  # Clear screen
    print("\033[1;36m◢◤ TESTING CHART RENDERING ◢◤\033[0m\n")
    
    # Initialize
    charts = CyberpunkCharts()
    data = DataFetcher()
    
    # Test 1: Portfolio Chart
    print("\033[1;35m1. Portfolio Chart Test:\033[0m")
    dates, values = data.get_portfolio_value_history()
    charts.render_portfolio_chart(dates, values)
    
    input("\nPress Enter to test Position Chart...")
    print("\033[2J\033[H")  # Clear screen
    
    # Test 2: Position Chart
    print("\033[1;35m2. Position Chart Test (AAPL):\033[0m")
    position = data.get_position_details('AAPL')
    dates, prices = data.get_position_history('AAPL')
    
    if position:
        charts.render_position_chart(
            symbol='AAPL',
            dates=dates,
            prices=prices,
            current_price=position['current_price'],
            stop_loss=position['stop_loss'],
            target_price=position['target_price'],
            entry_price=position.get('entry_price')
        )
    
    print("\n\033[1;32m✓ Chart tests complete!\033[0m")
    print("\033[1;33mNote: Charts should have BLACK background\033[0m")
    print("\033[1;33mIf background is not black, your terminal may override colors\033[0m")


if __name__ == "__main__":
    test_charts()
