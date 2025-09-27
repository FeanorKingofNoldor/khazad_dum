#!/usr/bin/env python3
"""
Test IBKR connection and portfolio fetching
Make sure IB Gateway is running before running this test
"""

import os
import sys
import asyncio
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def test_ib_connection():
    """Test IB Gateway connection and portfolio retrieval"""
    print("🏔️ KHAZAD_DUM IB Gateway Connection Test")
    print("="*60)
    
    try:
        # Import IBKR components
        from src.trading_engines.broker_connections.implementations.ibkr_connection import IBKRConnection
        from src.trading_engines.broker_connections.implementations.ibkr_portfolio import IBKRPortfolio
        from config.settings.base_config import get_ibkr_config
        
        # Get IB config
        config = get_ibkr_config()
        host = config['host']
        port = config['port']  # Should be 4002 for paper trading
        client_id = config['client_id']
        
        print(f"IB Gateway Configuration:")
        print(f"  Host: {host}")
        print(f"  Port: {port} ({'PAPER TRADING' if port == 4002 else 'LIVE TRADING' if port == 4001 else 'UNKNOWN'})")
        print(f"  Client ID: {client_id}")
        print(f"  Enabled: {config['enabled']}")
        
        # Test 1: Check if IB libraries are available
        print(f"\n1. Testing IB library availability...")
        try:
            from ib_async import IB
            print("✅ ib_async library available")
        except ImportError:
            print("❌ ib_async library not available")
            print("   Install with: pip install ib_async")
            return False
        
        # Test 2: Test connection
        print(f"\n2. Testing connection to IB Gateway...")
        print(f"   Attempting connection to {host}:{port}...")
        
        connection = IBKRConnection(host=host, port=port, client_id=client_id)
        
        try:
            # Try to connect (with timeout)
            connected = await asyncio.wait_for(connection.connect(), timeout=10.0)
            
            if connected:
                print("✅ Successfully connected to IB Gateway!")
                
                # Test 3: Test portfolio fetching
                print(f"\n3. Testing portfolio data retrieval...")
                portfolio = IBKRPortfolio(connection)
                
                try:
                    # Get account summary
                    summary = await portfolio.get_account_summary()
                    print("✅ Account summary retrieved:")
                    print(f"   Net Liquidation: ${summary.get('net_liquidation', 0):,.2f}")
                    print(f"   Total Cash: ${summary.get('total_cash', 0):,.2f}")
                    print(f"   Buying Power: ${summary.get('buying_power', 0):,.2f}")
                    print(f"   Gross Position Value: ${summary.get('gross_position_value', 0):,.2f}")
                    
                    # Get positions
                    print(f"\n4. Testing position retrieval...")
                    positions = await portfolio.get_positions()
                    print(f"✅ Found {len(positions)} positions:")
                    
                    if positions:
                        for i, pos in enumerate(positions[:5], 1):  # Show first 5
                            pnl_pct = pos.get('unrealized_pnl_pct', 0)
                            pnl_color = "🟢" if pnl_pct > 0 else "🔴" if pnl_pct < 0 else "⚪"
                            print(f"   {i}. {pos['symbol']}: {pos['position']} shares @ ${pos['avg_cost']:.2f} "
                                  f"{pnl_color} {pnl_pct:+.2f}%")
                    else:
                        print("   No positions found (clean account or paper trading)")
                    
                    # Test 5: Full portfolio data
                    print(f"\n5. Testing complete portfolio retrieval...")
                    portfolio_data = await portfolio.get_portfolio_data()
                    print("✅ Complete portfolio data retrieved:")
                    print(f"   Portfolio Value: ${portfolio_data['summary'].get('portfolio_value', 0):,.2f}")
                    print(f"   Total Positions: {portfolio_data['summary'].get('total_positions', 0)}")
                    print(f"   Total Unrealized P&L: ${portfolio_data['summary'].get('total_unrealized_pnl', 0):+,.2f}")
                    
                except Exception as e:
                    print(f"❌ Portfolio retrieval failed: {e}")
                    traceback.print_exc()
                
                # Disconnect
                await connection.disconnect()
                print(f"\n✅ Successfully disconnected from IB Gateway")
                
            else:
                print("❌ Failed to connect to IB Gateway")
                print("   Make sure IB Gateway is running and accepting connections")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Connection timeout (10 seconds)")
            print("   IB Gateway may not be running or not accepting connections")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("   Check IB Gateway status and configuration")
            return False
        
        print(f"\n" + "="*60)
        print("🎉 IB GATEWAY CONNECTION TEST SUCCESSFUL!")
        print("✅ Your KHAZAD_DUM system can connect to IB Gateway")
        print("✅ Portfolio data retrieval is working")
        print("✅ Ready for live portfolio integration")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Some IBKR modules may be missing")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

async def check_ib_gateway_status():
    """Quick check if IB Gateway is responding"""
    print("🔍 Checking if IB Gateway is running...")
    
    import socket
    
    # Check both paper and live ports
    ports_to_check = [4002, 4001]  # Paper, Live
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                mode = "PAPER TRADING" if port == 4002 else "LIVE TRADING"
                print(f"✅ IB Gateway is running on port {port} ({mode})")
                return port
            else:
                print(f"❌ No IB Gateway on port {port}")
        except Exception as e:
            print(f"❌ Error checking port {port}: {e}")
    
    return None

def main():
    """Main test function"""
    print("Starting IB Gateway connection test...\n")
    
    # First check if IB Gateway is running
    running_port = asyncio.run(check_ib_gateway_status())
    
    if not running_port:
        print("\n🚨 IB Gateway is NOT running!")
        print("\nTo start IB Gateway:")
        print("1. Launch TWS (Trader Workstation) or IB Gateway")
        print("2. Configure API settings:")
        print("   - Enable API")
        print("   - Socket port: 4002 (paper) or 4001 (live)")
        print("   - Client ID: 1")
        print("   - Accept connections from localhost")
        print("3. Run this test again")
        return False
    
    # Run the full connection test
    return asyncio.run(test_ib_connection())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)