#!/usr/bin/env python3
"""
Simple synchronous test for IBKR - avoids async issues
"""

from ib_async import IB, util
import time

def test_ibkr_sync():
    """Test IBKR connection with proper sync handling"""
    print("="*50)
    print("IBKR Synchronous Connection Test")
    print("="*50)
    
    # Create IB instance
    ib = IB()
    
    try:
        # Connect to paper trading
        print("\nConnecting to IB Gateway (port 4002)...")
        ib.connect('127.0.0.1', 4002, clientId=1)
        
        if ib.isConnected():
            print("✓ Connected successfully!")
            
            # Wait a moment for data to sync
            print("\nWaiting for data sync...")
            time.sleep(2)
            
            # Get account values
            print("\nFetching account values...")
            account_values = ib.accountValues()
            
            # Get account summary
            account_summary = ib.accountSummary()
            
            # Parse key values
            cash = 0
            portfolio_value = 0
            net_liquidation = 0
            currency = "USD"
            
            for value in account_values:
                if value.tag == 'TotalCashValue' and value.currency == 'BASE':
                    cash = float(value.value)
                    currency = value.currency
                elif value.tag == 'NetLiquidation' and value.currency == 'BASE':
                    net_liquidation = float(value.value)
                elif value.tag == 'GrossPositionValue' and value.currency == 'BASE':
                    portfolio_value = float(value.value)
            
            # Also check USD values if base currency is different
            for value in account_values:
                if value.tag == 'TotalCashValue' and value.currency == 'USD':
                    cash_usd = float(value.value)
                elif value.tag == 'TotalCashValue' and value.currency == 'CHF':
                    cash_chf = float(value.value)
            
            print(f"\n" + "="*50)
            print("ACCOUNT SUMMARY")
            print("="*50)
            
            # Show all currencies found
            currencies_found = set()
            for value in account_values:
                if value.currency:
                    currencies_found.add(value.currency)
            
            print(f"Currencies found: {', '.join(currencies_found)}")
            
            # Display values in all currencies
            print("\nCash Balances:")
            for value in account_values:
                if value.tag == 'TotalCashValue':
                    print(f"  {value.currency}: {float(value.value):,.2f}")
            
            print("\nNet Liquidation:")
            for value in account_values:
                if value.tag == 'NetLiquidation':
                    print(f"  {value.currency}: {float(value.value):,.2f}")
            
            # Get positions
            print("\nPositions:")
            positions = ib.positions()
            
            if positions:
                for position in positions[:5]:  # Show first 5
                    contract = position.contract
                    print(f"  {contract.symbol}: {position.position:,.0f} shares @ avg cost {position.avgCost:.2f}")
            else:
                print("  No open positions")
            
            # Get portfolio items
            print("\nPortfolio Items:")
            portfolio = ib.portfolio()
            
            if portfolio:
                total_value = 0
                for item in portfolio[:5]:  # Show first 5
                    contract = item.contract
                    position = item.position
                    market_value = item.marketValue
                    total_value += market_value
                    print(f"  {contract.symbol}: {position:,.0f} units, Value: ${market_value:,.2f}")
                if len(portfolio) > 5:
                    print(f"  ... and {len(portfolio)-5} more positions")
                print(f"\nTotal Portfolio Value: ${total_value:,.2f}")
            else:
                print("  No portfolio items")
            
            print("\n" + "="*50)
            print("✓ Data retrieved successfully!")
            print("="*50)
            
        else:
            print("✗ Failed to connect")
            print("\nTroubleshooting:")
            print("1. Check IB Gateway is running")
            print("2. Check it's logged into Paper Trading account")
            print("3. Verify port 4002 in API settings")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCommon causes:")
        print("1. IB Gateway not running")
        print("2. Wrong port (should be 4002 for paper)")
        print("3. API not enabled in IB Gateway settings")
        
    finally:
        # Always disconnect
        if ib.isConnected():
            print("\nDisconnecting...")
            ib.disconnect()
            print("✓ Disconnected")

if __name__ == "__main__":
    # Run with util.startLoop to handle async properly
    util.startLoop()
    test_ibkr_sync()
    
    print("\nTest complete!")