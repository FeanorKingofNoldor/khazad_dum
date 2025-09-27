#!/usr/bin/env python3
"""
🏔️ KHAZAD_DUM - IBKR Order Service
Order execution operations using the centralized connection manager

All order-related IBKR operations (buy, sell, cancel, modify) go through here.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from decimal import Decimal

try:
    from ib_async import Stock, Contract, Order, MarketOrder, LimitOrder, StopOrder
    IB_AVAILABLE = True
except ImportError:
    print("Warning: ib_async not installed. Install with: pip install ib_async")
    IB_AVAILABLE = False

try:
    from .ibkr_connection_manager import get_connection_manager
except ImportError:
    from ibkr_connection_manager import get_connection_manager

logger = logging.getLogger(__name__)


class IBKROrderService:
    """
    Order execution service using centralized IBKR connection manager
    Handles buy/sell orders, cancellations, and order management
    """
    
    def __init__(self, connection_manager=None):
        """
        Initialize order service
        
        Args:
            connection_manager: Optional connection manager (uses global if None)
        """
        if not IB_AVAILABLE:
            raise ImportError("ib_async library not available. Install with: pip install ib_async")
            
        self.manager = connection_manager or get_connection_manager()
    
    def create_stock_contract(self, symbol: str, exchange: str = "SMART", currency: str = "USD") -> Contract:
        """
        Create a stock contract for order execution
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            exchange: Exchange (default: SMART routing)
            currency: Currency (default: USD)
            
        Returns:
            Stock contract object
        """
        return Stock(symbol, exchange, currency)
    
    def place_market_order(
        self, 
        symbol: str, 
        action: str, 
        quantity: int,
        exchange: str = "SMART",
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Place a market order
        
        Args:
            symbol: Stock symbol
            action: 'BUY' or 'SELL'
            quantity: Number of shares
            exchange: Exchange (default: SMART)
            currency: Currency (default: USD)
            
        Returns:
            Order result dictionary
        """
        try:
            with self.manager.ensure_connection() as ib:
                logger.info(f"Placing market order: {action} {quantity} {symbol}")
                
                # Create contract and order
                contract = self.create_stock_contract(symbol, exchange, currency)
                order = MarketOrder(action, quantity)
                
                # Place the order
                trade = ib.placeOrder(contract, order)
                
                # Wait for order to be submitted
                ib.sleep(1)
                
                order_result = {
                    'success': True,
                    'order_id': trade.order.orderId,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'order_type': 'MKT',
                    'status': trade.orderStatus.status,
                    'filled': trade.orderStatus.filled,
                    'remaining': trade.orderStatus.remaining,
                    'avg_fill_price': trade.orderStatus.avgFillPrice,
                    'commission': trade.orderStatus.commission,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Market order placed successfully"
                }
                
                logger.info(f"✅ Market order placed: {order_result['order_id']} ({order_result['status']})")
                return order_result
                
        except Exception as e:
            logger.error(f"❌ Failed to place market order: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'order_type': 'MKT',
                'timestamp': datetime.now().isoformat(),
                'message': f"Market order failed: {e}"
            }
    
    def place_limit_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        limit_price: float,
        exchange: str = "SMART",
        currency: str = "USD",
        time_in_force: str = "DAY"
    ) -> Dict[str, Any]:
        """
        Place a limit order
        
        Args:
            symbol: Stock symbol
            action: 'BUY' or 'SELL'
            quantity: Number of shares
            limit_price: Limit price
            exchange: Exchange (default: SMART)
            currency: Currency (default: USD)
            time_in_force: Order duration (DAY, GTC, etc.)
            
        Returns:
            Order result dictionary
        """
        try:
            with self.manager.ensure_connection() as ib:
                logger.info(f"Placing limit order: {action} {quantity} {symbol} @ ${limit_price:.2f}")
                
                # Create contract and order
                contract = self.create_stock_contract(symbol, exchange, currency)
                order = LimitOrder(action, quantity, limit_price)
                order.tif = time_in_force
                
                # Place the order
                trade = ib.placeOrder(contract, order)
                
                # Wait for order to be submitted
                ib.sleep(1)
                
                order_result = {
                    'success': True,
                    'order_id': trade.order.orderId,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'limit_price': limit_price,
                    'order_type': 'LMT',
                    'time_in_force': time_in_force,
                    'status': trade.orderStatus.status,
                    'filled': trade.orderStatus.filled,
                    'remaining': trade.orderStatus.remaining,
                    'avg_fill_price': trade.orderStatus.avgFillPrice,
                    'commission': trade.orderStatus.commission,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Limit order placed successfully"
                }
                
                logger.info(f"✅ Limit order placed: {order_result['order_id']} ({order_result['status']})")
                return order_result
                
        except Exception as e:
            logger.error(f"❌ Failed to place limit order: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'limit_price': limit_price,
                'order_type': 'LMT',
                'timestamp': datetime.now().isoformat(),
                'message': f"Limit order failed: {e}"
            }
    
    def place_stop_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        stop_price: float,
        exchange: str = "SMART",
        currency: str = "USD",
        time_in_force: str = "DAY"
    ) -> Dict[str, Any]:
        """
        Place a stop order
        
        Args:
            symbol: Stock symbol
            action: 'BUY' or 'SELL'
            quantity: Number of shares
            stop_price: Stop trigger price
            exchange: Exchange (default: SMART)
            currency: Currency (default: USD)
            time_in_force: Order duration (DAY, GTC, etc.)
            
        Returns:
            Order result dictionary
        """
        try:
            with self.manager.ensure_connection() as ib:
                logger.info(f"Placing stop order: {action} {quantity} {symbol} @ stop ${stop_price:.2f}")
                
                # Create contract and order
                contract = self.create_stock_contract(symbol, exchange, currency)
                order = StopOrder(action, quantity, stop_price)
                order.tif = time_in_force
                
                # Place the order
                trade = ib.placeOrder(contract, order)
                
                # Wait for order to be submitted
                ib.sleep(1)
                
                order_result = {
                    'success': True,
                    'order_id': trade.order.orderId,
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'stop_price': stop_price,
                    'order_type': 'STP',
                    'time_in_force': time_in_force,
                    'status': trade.orderStatus.status,
                    'filled': trade.orderStatus.filled,
                    'remaining': trade.orderStatus.remaining,
                    'avg_fill_price': trade.orderStatus.avgFillPrice,
                    'commission': trade.orderStatus.commission,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Stop order placed successfully"
                }
                
                logger.info(f"✅ Stop order placed: {order_result['order_id']} ({order_result['status']})")
                return order_result
                
        except Exception as e:
            logger.error(f"❌ Failed to place stop order: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'stop_price': stop_price,
                'order_type': 'STP',
                'timestamp': datetime.now().isoformat(),
                'message': f"Stop order failed: {e}"
            }
    
    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order by order ID
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result dictionary
        """
        try:
            with self.manager.ensure_connection() as ib:
                logger.info(f"Cancelling order: {order_id}")
                
                # Find the order
                orders = ib.orders()
                target_order = None
                
                for order in orders:
                    if order.order.orderId == order_id:
                        target_order = order
                        break
                
                if not target_order:
                    return {
                        'success': False,
                        'order_id': order_id,
                        'error': 'Order not found',
                        'timestamp': datetime.now().isoformat(),
                        'message': f"Order {order_id} not found"
                    }
                
                # Cancel the order
                ib.cancelOrder(target_order.order)
                
                # Wait for cancellation
                ib.sleep(1)
                
                result = {
                    'success': True,
                    'order_id': order_id,
                    'symbol': target_order.contract.symbol,
                    'action': target_order.order.action,
                    'quantity': target_order.order.totalQuantity,
                    'status': 'PendingCancel',
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Order cancellation requested"
                }
                
                logger.info(f"✅ Order cancellation requested: {order_id}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to cancel order {order_id}: {e}")
            return {
                'success': False,
                'order_id': order_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'message': f"Order cancellation failed: {e}"
            }
    
    def cancel_all_orders(self, symbol: str = None) -> Dict[str, Any]:
        """
        Cancel all open orders, optionally filtered by symbol
        
        Args:
            symbol: Optional symbol filter (cancel only orders for this symbol)
            
        Returns:
            Batch cancellation result dictionary
        """
        try:
            with self.manager.ensure_connection() as ib:
                logger.info(f"Cancelling all orders{f' for {symbol}' if symbol else ''}")
                
                # Get all open orders
                orders = ib.orders()
                orders_to_cancel = []
                
                for order in orders:
                    if order.orderStatus.status in ['PreSubmitted', 'Submitted', 'PendingSubmit']:
                        # Filter by symbol if specified
                        if symbol is None or order.contract.symbol == symbol:
                            orders_to_cancel.append(order)
                
                if not orders_to_cancel:
                    return {
                        'success': True,
                        'cancelled_count': 0,
                        'message': f"No open orders to cancel{f' for {symbol}' if symbol else ''}",
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Cancel all matching orders
                cancelled_orders = []
                for order in orders_to_cancel:
                    try:
                        ib.cancelOrder(order.order)
                        cancelled_orders.append({
                            'order_id': order.order.orderId,
                            'symbol': order.contract.symbol,
                            'action': order.order.action,
                            'quantity': order.order.totalQuantity
                        })
                    except Exception as e:
                        logger.error(f"Failed to cancel order {order.order.orderId}: {e}")
                
                # Wait for cancellations to process
                ib.sleep(2)
                
                result = {
                    'success': True,
                    'cancelled_count': len(cancelled_orders),
                    'cancelled_orders': cancelled_orders,
                    'symbol_filter': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Cancelled {len(cancelled_orders)} orders"
                }
                
                logger.info(f"✅ Cancelled {len(cancelled_orders)} orders")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to cancel orders: {e}")
            return {
                'success': False,
                'cancelled_count': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'message': f"Batch order cancellation failed: {e}"
            }
    
    def get_order_status(self, order_id: int) -> Dict[str, Any]:
        """
        Get status of a specific order
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order status dictionary
        """
        try:
            with self.manager.ensure_connection() as ib:
                # Find the order
                orders = ib.orders()
                
                for order in orders:
                    if order.order.orderId == order_id:
                        return {
                            'success': True,
                            'order_id': order_id,
                            'symbol': order.contract.symbol,
                            'action': order.order.action,
                            'quantity': order.order.totalQuantity,
                            'order_type': order.order.orderType,
                            'limit_price': order.order.lmtPrice if order.order.lmtPrice else None,
                            'aux_price': order.order.auxPrice if order.order.auxPrice else None,
                            'status': order.orderStatus.status,
                            'filled': order.orderStatus.filled,
                            'remaining': order.orderStatus.remaining,
                            'avg_fill_price': order.orderStatus.avgFillPrice,
                            'commission': order.orderStatus.commission,
                            'timestamp': datetime.now().isoformat()
                        }
                
                # Order not found
                return {
                    'success': False,
                    'order_id': order_id,
                    'error': 'Order not found',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get order status for {order_id}: {e}")
            return {
                'success': False,
                'order_id': order_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_trading_signal(
        self,
        symbol: str,
        action: str,
        quantity: int,
        order_type: str = "MKT",
        limit_price: float = None,
        stop_price: float = None,
        time_in_force: str = "DAY"
    ) -> Dict[str, Any]:
        """
        Execute a trading signal (high-level order placement)
        
        Args:
            symbol: Stock symbol
            action: 'BUY' or 'SELL'
            quantity: Number of shares
            order_type: 'MKT', 'LMT', 'STP'
            limit_price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            time_in_force: Order duration
            
        Returns:
            Order execution result
        """
        logger.info(f"Executing trading signal: {action} {quantity} {symbol} ({order_type})")
        
        if order_type.upper() == "MKT":
            return self.place_market_order(symbol, action, quantity)
        elif order_type.upper() == "LMT":
            if limit_price is None:
                raise ValueError("Limit price required for limit orders")
            return self.place_limit_order(symbol, action, quantity, limit_price, time_in_force=time_in_force)
        elif order_type.upper() == "STP":
            if stop_price is None:
                raise ValueError("Stop price required for stop orders")
            return self.place_stop_order(symbol, action, quantity, stop_price, time_in_force=time_in_force)
        else:
            raise ValueError(f"Unsupported order type: {order_type}")


# Convenience functions for backward compatibility
def place_market_order_sync(symbol: str, action: str, quantity: int) -> Dict[str, Any]:
    """Place market order (backward compatibility)"""
    service = IBKROrderService()
    return service.place_market_order(symbol, action, quantity)


def place_limit_order_sync(symbol: str, action: str, quantity: int, limit_price: float) -> Dict[str, Any]:
    """Place limit order (backward compatibility)"""
    service = IBKROrderService()
    return service.place_limit_order(symbol, action, quantity, limit_price)


def cancel_order_sync(order_id: int) -> Dict[str, Any]:
    """Cancel order (backward compatibility)"""
    service = IBKROrderService()
    return service.cancel_order(order_id)


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    def test_order_service():
        """Test the order service (CAREFUL: This places real orders in paper trading!)"""
        print("Testing IBKR Order Service...")
        print("⚠️  WARNING: This test places actual orders in your paper trading account!")
        
        # Initialize service
        service = IBKROrderService()
        
        # Test symbol for demo
        test_symbol = "AAPL"
        test_quantity = 1  # Small quantity for testing
        
        print(f"\n=== Testing with {test_symbol} (quantity: {test_quantity}) ===")
        
        # Test 1: Place a small limit order
        print(f"\n1. Testing limit order: BUY {test_quantity} {test_symbol}")
        limit_result = service.place_limit_order(test_symbol, "BUY", test_quantity, 150.00)  # Well below market
        
        if limit_result['success']:
            print(f"✅ Limit order placed: {limit_result['order_id']} ({limit_result['status']})")
            order_id = limit_result['order_id']
            
            # Test 2: Check order status
            print(f"\n2. Testing order status check for order {order_id}")
            status = service.get_order_status(order_id)
            if status['success']:
                print(f"✅ Order status: {status['status']} (filled: {status['filled']})")
            else:
                print(f"❌ Failed to get order status: {status['error']}")
            
            # Test 3: Cancel the order
            print(f"\n3. Testing order cancellation for order {order_id}")
            cancel_result = service.cancel_order(order_id)
            if cancel_result['success']:
                print(f"✅ Order cancellation requested: {cancel_result['message']}")
            else:
                print(f"❌ Failed to cancel order: {cancel_result['error']}")
        else:
            print(f"❌ Failed to place limit order: {limit_result['error']}")
            return False
        
        # Test 4: Cancel all orders (cleanup)
        print(f"\n4. Testing cancel all orders")
        cancel_all_result = service.cancel_all_orders()
        if cancel_all_result['success']:
            print(f"✅ Cancelled {cancel_all_result['cancelled_count']} orders")
        else:
            print(f"❌ Failed to cancel all orders: {cancel_all_result['error']}")
        
        print("\n⚠️  Note: Orders were placed in paper trading account only!")
        return True
    
    # Ask for confirmation before testing
    response = input("This test will place actual orders in your IBKR paper account. Continue? (y/N): ")
    if response.lower() == 'y':
        if test_order_service():
            print("\n🎉 Order service tests completed!")
            sys.exit(0)
        else:
            print("\n❌ Order service tests failed!")
            sys.exit(1)
    else:
        print("Order service test cancelled by user.")
        sys.exit(0)