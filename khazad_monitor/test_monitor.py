#!/usr/bin/env python3
"""
Quick test to verify KHAZAD_DUM Monitor is working
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import rich
        print("✓ Rich installed")
    except ImportError:
        print("✗ Rich not installed - run: pip install rich")
        return False
    
    try:
        import plotext
        print("✓ Plotext installed")
    except ImportError:
        print("✗ Plotext not installed - run: pip install plotext")
        return False
    
    try:
        import psycopg2
        print("✓ PostgreSQL driver installed")
    except ImportError:
        print("✗ PostgreSQL driver not installed - run: pip install psycopg2-binary")
        # Not critical if using mock data
    
    try:
        import dotenv
        print("✓ Python-dotenv installed")
    except ImportError:
        print("✗ Python-dotenv not installed - run: pip install python-dotenv")
    
    return True


def test_mock_data():
    """Test that mock data works"""
    print("\nTesting mock data mode...")
    
    # Force mock mode
    os.environ['USE_MOCK'] = 'True'
    
    try:
        from data_fetcher import DataFetcher
        from charts import ChartRenderer
        
        # Test data fetcher
        data = DataFetcher()
        positions = data.get_portfolio_positions()
        
        if positions:
            print(f"✓ Mock data working - found {len(positions)} positions")
            for pos in positions:
                print(f"  - {pos['symbol']}: ${pos['current_price']:.2f}")
        else:
            print("✗ No mock positions returned")
            return False
        
        # Test chart renderer
        charts = ChartRenderer()
        dates, prices = data.get_position_history('AAPL')
        
        if dates and prices:
            print(f"✓ Price history working - {len(prices)} data points")
        else:
            print("✗ No price history returned")
            return False
            
        # Test chart generation
        chart_str = charts.render_position_chart(
            symbol='AAPL',
            dates=dates,
            prices=prices,
            current_price=180.0,
            stop_loss=170.0,
            target_price=200.0,
            entry_price=175.0
        )
        
        if chart_str and len(chart_str) > 100:
            print("✓ Chart generation working")
        else:
            print("✗ Chart generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Error testing mock data: {e}")
        return False
    
    return True


def test_display():
    """Test Rich display capabilities"""
    print("\nTesting display capabilities...")
    
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Test table
        table = Table(title="Test Table")
        table.add_column("Symbol")
        table.add_column("Price")
        table.add_row("AAPL", "$180.00")
        
        console.print(Panel("Display test successful!", border_style="green"))
        print("✓ Rich display working")
        
    except Exception as e:
        print(f"✗ Display test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("=" * 50)
    print("KHAZAD_DUM Monitor Test Suite")
    print("=" * 50)
    
    all_pass = True
    
    if not test_imports():
        all_pass = False
        print("\n⚠ Some imports failed. Please install missing packages.")
    
    if not test_mock_data():
        all_pass = False
        print("\n⚠ Mock data test failed.")
    
    if not test_display():
        all_pass = False
        print("\n⚠ Display test failed.")
    
    print("\n" + "=" * 50)
    
    if all_pass:
        print("✅ All tests passed! You can now run:")
        print("   python simple_monitor.py")
        print("\nOr for advanced version:")
        print("   python monitor_cli.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nFor help, check the README.md file")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
