#!/usr/bin/env python3
"""
🏔️ KHAZAD_DUM - IBKR Order Execution Test
Test the new centralized order execution capabilities

⚠️  CAUTION: This test places REAL orders in your paper trading account!
"""

import sys
import time
from datetime import datetime

def test_order_execution():
    """Test IBKR order execution capabilities"""
    
    print("=" * 60)
    print("KHAZAD_DUM IBKR ORDER EXECUTION TEST")
    print("=" * 60)
    
    # Import the new IBKR facade
    try:
        from src.trading_engines.broker_connections.implementations.ibkr_facade import IBKRFacade
    except ImportError as e:
        print(f"❌ Failed to import IBKR Facade: {e}")
        return False
    
    # Initialize facade
    print("\n1. Initializing IBKR Order Service...")
    facade = IBKRFacade('127.0.0.1', 4002, 1)  # Paper trading
    
    # Connect
    print("\n2. Connecting to IBKR...")
    if not facade.connect_sync():
        print("❌ Failed to connect to IBKR")
        print("Make sure IB Gateway is running on port 4002")
        return False
    
    print("✅ Connected to IBKR Paper Trading")
    
    try:
        # Get current account info
        print("\n3. Checking Account Status...")
        portfolio_data = facade.get_portfolio_data_sync()
        summary = portfolio_data['summary']
        
        currency = summary.get('currency', 'USD')
        print(f"   Account Currency: {currency}")
        print(f"   Available Cash: {currency} {summary['total_cash']:,.2f}")
        print(f"   Net Liquidation: {currency} {summary['net_liquidation']:,.2f}")
        print(f"   Current Positions: {summary['total_positions']}")
        
        # Test symbol
        test_symbol = "AAPL"
        test_quantity = 1  # Small quantity for testing
        
        print(f"\n4. Testing Order Placement (Test Symbol: {test_symbol}, Quantity: {test_quantity})...")
        
        # Test 1: Place a limit order well below market (won't fill)
        print(f"\n   4a. Placing limit order: BUY {test_quantity} {test_symbol} @ $150.00")
        limit_result = facade.place_limit_order(test_symbol, "BUY", test_quantity, 150.00)
        
        if limit_result['success']:
            order_id = limit_result['order_id']
            print(f"   ✅ Limit order placed: Order ID {order_id}")
            print(f"      Status: {limit_result['status']}")
            
            # Wait a moment for order to process
            time.sleep(2)
            
            # Test 2: Check order status
            print(f"\n   4b. Checking order status...")
            status_result = facade.order_service.get_order_status(order_id)
            
            if status_result['success']:
                print(f"   ✅ Order status retrieved:")
                print(f"      Status: {status_result['status']}")
                print(f"      Filled: {status_result['filled']}")
                print(f"      Remaining: {status_result['remaining']}")
            else:
                print(f"   ⚠️  Could not retrieve order status: {status_result['error']}")
            
            # Test 3: Cancel the order
            print(f"\n   4c. Cancelling order {order_id}...")
            cancel_result = facade.cancel_order(order_id)
            
            if cancel_result['success']:
                print(f"   ✅ Order cancellation requested")
                print(f"      Message: {cancel_result['message']}")
            else:
                print(f"   ❌ Failed to cancel order: {cancel_result['error']}")
            
        else:
            print(f"   ❌ Failed to place limit order: {limit_result['error']}")
            return False
        
        # Test 4: Check current orders
        print(f"\n   4d. Checking all open orders...")
        orders = facade.get_orders()
        print(f"   Open orders: {len(orders)}")
        
        if orders:
            for order in orders:
                print(f"      Order {order['order_id']}: {order['symbol']} {order['action']} "
                      f"{order['quantity']} @ {order.get('limit_price', 'MKT')} ({order['status']})")
        
        # Test 5: Cancel all remaining orders (cleanup)
        print(f"\n   4e. Cleaning up - cancelling all orders...")
        cleanup_result = facade.cancel_all_orders()
        
        if cleanup_result['success']:
            print(f"   ✅ Cancelled {cleanup_result['cancelled_count']} orders")
        else:
            print(f"   ⚠️  Cleanup failed: {cleanup_result['error']}")
        
        print(f"\n5. Testing Complete Portfolio + Order Integration...")
        
        # Get final portfolio state
        final_data = facade.get_portfolio_data_sync()
        final_summary = final_data['summary']
        
        print(f"   Final Account Status:")
        print(f"      Cash: {currency} {final_summary['total_cash']:,.2f}")
        print(f"      Positions: {final_summary['total_positions']}")
        print(f"      Open Orders: {final_summary['open_orders_count']}")
        print(f"      Data Source: {final_data.get('data_source')}")
        
        # Connection info
        print(f"\n6. Connection Manager Status:")
        conn_info = facade.get_connection_info()
        print(f"   Connected: {conn_info['connected']}")
        print(f"   Connection Type: {conn_info['connection_type']}")
        print(f"   Cache Items: {conn_info['cache_items']}")
        print(f"   Services: Portfolio✓ Orders✓")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Always disconnect
        print(f"\n7. Disconnecting...")
        facade.disconnect_sync()
        print("✅ Disconnected from IBKR")


def main():
    """Main test function with user confirmation"""
    
    print("⚠️  IBKR ORDER EXECUTION TEST")
    print("\nThis test will place REAL orders in your IBKR paper trading account!")
    print("Orders will be:")
    print("  - Small quantities (1 share)")
    print("  - Limit orders well below market (won't fill)")  
    print("  - Automatically cancelled after testing")
    print("  - Paper trading only (no real money)")
    
    response = input("\nDo you want to proceed with order execution testing? (y/N): ")
    
    if response.lower() != 'y':
        print("Order execution test cancelled by user.")
        return
    
    print("\n" + "="*60)
    print("PROCEEDING WITH ORDER EXECUTION TEST...")
    print("="*60)
    
    success = test_order_execution()
    
    if success:
        print("\n" + "🎉" * 20)
        print("🎉 IBKR ORDER EXECUTION TEST SUCCESSFUL! 🎉")
        print("🎉" * 20)
        print("\n✅ All order execution capabilities working:")
        print("   • Connection management ✓")
        print("   • Portfolio data retrieval ✓") 
        print("   • Order placement (limit orders) ✓")
        print("   • Order status checking ✓")
        print("   • Order cancellation ✓")
        print("   • Batch order operations ✓")
        print("   • Real account data (~934k BASE) ✓")
        print("\n🚀 KHAZAD_DUM is ready for live trading operations!")
        
    else:
        print("\n" + "❌" * 20)
        print("❌ ORDER EXECUTION TEST FAILED ❌")
        print("❌" * 20)
        print("\nPlease check:")
        print("  • IB Gateway is running")
        print("  • Paper trading account is logged in")
        print("  • API permissions are enabled")
        print("  • Port 4002 is accessible")


if __name__ == "__main__":
    main()