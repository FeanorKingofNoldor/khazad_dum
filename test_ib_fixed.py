#!/usr/bin/env python3
"""
Fixed IBKR connection test with proper event loop handling
"""

import sys
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ibkr_connection():
    """Test IBKR connection with proper event loop handling"""
    
    print("=" * 60)
    print("FIXED IBKR CONNECTION TEST")
    print("=" * 60)
    
    # Import ib_async
    try:
        from ib_async import IB, util
        print("✅ ib_async imported")
    except ImportError as e:
        print(f"❌ Cannot import ib_async: {e}")
        return False
    
    # CRITICAL: Initialize the event loop properly for ib_async
    print("\n1. Starting event loop...")
    util.startLoop()  # This starts a background thread with an event loop
    print("✅ Event loop started")
    
    # Create IB instance
    ib = IB()
    
    try:
        # Connect with Client ID 1 as requested
        print("\n2. Connecting with Master Client ID 1...")
        ib.connect('127.0.0.1', 4002, clientId=1, timeout=30)
        
        if ib.isConnected():
            print("✅ CONNECTED SUCCESSFULLY!")
            
            # Wait for initial data
            print("\n3. Waiting for data sync...")
            time.sleep(3)
            
            # Get account summary
            print("\n4. Fetching account data...")
            account_summary = ib.accountSummary()
            
            if account_summary:
                print(f"✅ Account summary: {len(account_summary)} items")
                
                # Parse key values
                account_data = {}
                for item in account_summary:
                    account_data[item.tag] = item.value
                
                # Display important values
                print("\nAccount Details:")
                if 'NetLiquidation' in account_data:
                    print(f"  Net Liquidation: ${float(account_data['NetLiquidation']):,.2f}")
                if 'TotalCashValue' in account_data:
                    print(f"  Total Cash: ${float(account_data['TotalCashValue']):,.2f}")
                if 'BuyingPower' in account_data:
                    print(f"  Buying Power: ${float(account_data['BuyingPower']):,.2f}")
            else:
                print("⚠️  No account summary data (might need to wait longer)")
            
            # Get positions
            print("\n5. Fetching positions...")
            positions = ib.positions()
            print(f"✅ Found {len(positions)} positions")
            
            if positions:
                print("\nPositions:")
                for i, pos in enumerate(positions[:5], 1):
                    print(f"  {i}. {pos.contract.symbol}: {pos.position} @ avg cost ${pos.avgCost:.2f}")
            else:
                print("  No open positions")
            
            # Get portfolio
            print("\n6. Fetching portfolio...")
            portfolio = ib.portfolio()
            print(f"✅ Portfolio items: {len(portfolio)}")
            
            total_value = 0
            if portfolio:
                for item in portfolio:
                    total_value += item.marketValue if item.marketValue else 0
                print(f"  Total portfolio value: ${total_value:,.2f}")
            
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! IB CONNECTION WORKING!")
            print("=" * 60)
            
            # Clean disconnect
            ib.disconnect()
            print("\n✅ Disconnected cleanly")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to disconnect if connected
        try:
            if ib.isConnected():
                ib.disconnect()
        except:
            pass
        
        return False
    
    finally:
        # Stop the event loop
        try:
            util.stopLoop()
        except:
            pass

def check_prerequisites():
    """Check if TWS is running"""
    import socket
    
    print("Checking prerequisites...")
    
    sock = socket.socket()
    result = sock.connect_ex(('127.0.0.1', 4002))
    sock.close()
    
    if result != 0:
        print("❌ Port 4002 is not open")
        print("\nPlease:")
        print("1. Ensure TWS is running")
        print("2. You're logged into Paper Trading")
        print("3. API is enabled in settings")
        return False
    else:
        print("✅ Port 4002 is open\n")
        return True

if __name__ == "__main__":
    if check_prerequisites():
        success = test_ibkr_connection()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Prerequisites not met")
        sys.exit(1)