#!/usr/bin/env python3
"""
Working IBKR test with proper event loop handling
"""

from ib_async import IB, util
import time

def test_ibkr_portfolio():
    """Test IBKR connection and fetch real portfolio data"""
    
    print("=" * 60)
    print("IBKR PORTFOLIO TEST - KHAZAD_DUM")
    print("=" * 60)
    
    # Start event loop
    util.startLoop()
    
    ib = IB()
    
    try:
        # Connect
        print("\nConnecting to IB Gateway...")
        ib.connect('127.0.0.1', 4002, clientId=1)
        
        if not ib.isConnected():
            print("❌ Failed to connect")
            return False
            
        print("✅ Connected successfully!")
        
        # Wait for data sync
        print("\nWaiting for data sync...")
        time.sleep(3)
        
        # Get account summary
        print("\n" + "=" * 40)
        print("ACCOUNT SUMMARY")
        print("=" * 40)
        
        account_summary = ib.accountSummary()
        
        # Parse summary into dict
        account_data = {}
        for item in account_summary:
            account_data[item.tag] = item.value
        
        # Display key values
        print(f"Account Type: {account_data.get('AccountType', 'N/A')}")
        print(f"Net Liquidation: ${float(account_data.get('NetLiquidation', 0)):,.2f}")
        print(f"Total Cash: ${float(account_data.get('TotalCashValue', 0)):,.2f}")
        print(f"Buying Power: ${float(account_data.get('BuyingPower', 0)):,.2f}")
        print(f"Gross Position Value: ${float(account_data.get('GrossPositionValue', 0)):,.2f}")
        
        # Get positions
        print("\n" + "=" * 40)
        print("CURRENT POSITIONS")
        print("=" * 40)
        
        positions = ib.positions()
        
        if positions:
            total_value = 0
            total_pnl = 0
            
            print(f"Found {len(positions)} positions:\n")
            
            for pos in positions:
                value = pos.marketValue if pos.marketValue else 0
                pnl = pos.unrealizedPNL if pos.unrealizedPNL else 0
                total_value += value
                total_pnl += pnl
                
                print(f"  {pos.contract.symbol}:")
                print(f"    Position: {pos.position:,.0f} shares")
                print(f"    Avg Cost: ${pos.avgCost:.2f}")
                print(f"    Market Value: ${value:,.2f}")
                print(f"    Unrealized P&L: ${pnl:+,.2f}")
                print()
            
            print(f"Total Market Value: ${total_value:,.2f}")
            print(f"Total Unrealized P&L: ${total_pnl:+,.2f}")
        else:
            print("No open positions")
        
        # Get portfolio items
        print("\n" + "=" * 40)
        print("PORTFOLIO ITEMS")
        print("=" * 40)
        
        portfolio = ib.portfolio()
        
        if portfolio:
            print(f"Portfolio has {len(portfolio)} items")
        else:
            print("No portfolio items")
        
        # Get account values
        print("\n" + "=" * 40)
        print("ACCOUNT VALUES")
        print("=" * 40)
        
        account_values = ib.accountValues()
        
        # Show cash by currency
        cash_by_currency = {}
        for val in account_values:
            if val.tag == 'TotalCashValue':
                cash_by_currency[val.currency] = float(val.value)
        
        print("Cash by Currency:")
        for currency, amount in cash_by_currency.items():
            print(f"  {currency}: {amount:,.2f}")
        
        print("\n" + "=" * 60)
        print("✅ PORTFOLIO DATA SUCCESSFULLY RETRIEVED!")
        print("=" * 60)
        
        # Disconnect
        ib.disconnect()
        print("\n✅ Disconnected from IB Gateway")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        if ib.isConnected():
            ib.disconnect()
        
        return False
    
    finally:
        util.stopLoop()

if __name__ == "__main__":
    import sys
    success = test_ibkr_portfolio()
    sys.exit(0 if success else 1)