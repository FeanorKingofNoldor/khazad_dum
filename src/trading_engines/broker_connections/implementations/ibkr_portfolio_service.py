#!/usr/bin/env python3
"""
🏔️ KHAZAD_DUM - IBKR Portfolio Service
Portfolio data operations using the centralized connection manager

All portfolio-related IBKR operations (positions, account summary, P&L) go through here.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

try:
    from .ibkr_connection_manager import get_connection_manager
except ImportError:
    from ibkr_connection_manager import get_connection_manager

logger = logging.getLogger(__name__)


class IBKRPortfolioService:
    """
    Portfolio service using centralized IBKR connection manager
    Handles positions, account data, and portfolio analytics
    """
    
    def __init__(self, connection_manager=None):
        """
        Initialize portfolio service
        
        Args:
            connection_manager: Optional connection manager (uses global if None)
        """
        self.manager = connection_manager or get_connection_manager()
    
    def get_account_summary(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get account summary with cash, equity, buying power, etc.
        
        Args:
            force_refresh: Force refresh cached data
            
        Returns:
            Dict with account summary data
        """
        cache_key = "account_summary"
        
        # Check cache first unless forcing refresh
        if not force_refresh:
            cached = self.manager.get_cache(cache_key)
            if cached:
                logger.debug("Using cached account summary")
                return cached
        
        try:
            with self.manager.ensure_connection() as ib:
                logger.info("Fetching fresh account summary from IBKR...")
                
                # Request comprehensive account summary
                account_tags = [
                    'TotalCashValue',
                    'NetLiquidation', 
                    'GrossPositionValue',
                    'BuyingPower',
                    'AvailableFunds',
                    'Cushion',
                    'FullAvailableFunds',
                    'FullExcessLiquidity',
                    'FullInitMarginReq',
                    'FullMaintMarginReq',
                    'Currency',
                    'AccountType'
                ]
                
                # Get account summary from IBKR
                summary_items = ib.accountSummary()
                
                account_data = {}
                for item in summary_items:
                    if item.tag in account_tags:
                        try:
                            # Try to convert to float for numeric values
                            if item.tag not in ['Currency', 'AccountType']:
                                account_data[item.tag] = float(item.value)
                            else:
                                account_data[item.tag] = item.value
                        except (ValueError, TypeError):
                            account_data[item.tag] = item.value
                
                # Calculate derived metrics
                total_cash = account_data.get('TotalCashValue', 0)
                net_liquidation = account_data.get('NetLiquidation', 0)
                gross_position_value = account_data.get('GrossPositionValue', 0)
                
                processed_summary = {
                    'total_cash': total_cash,
                    'net_liquidation': net_liquidation,
                    'gross_position_value': gross_position_value,
                    'buying_power': account_data.get('BuyingPower', 0),
                    'available_funds': account_data.get('AvailableFunds', 0),
                    'portfolio_value': net_liquidation - total_cash,
                    'cash_percentage': (total_cash / net_liquidation * 100) if net_liquidation > 0 else 0,
                    'equity_percentage': ((net_liquidation - total_cash) / net_liquidation * 100) if net_liquidation > 0 else 0,
                    'currency': account_data.get('Currency', 'USD'),
                    'account_type': account_data.get('AccountType', 'Unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': account_data,
                    'data_source': 'IBKR_LIVE'
                }
                
                # Cache the results
                self.manager.set_cache(cache_key, processed_summary)
                
                logger.info(f"Account summary: {processed_summary['currency']} {processed_summary['net_liquidation']:,.2f} net liquidation")
                return processed_summary
                
        except Exception as e:
            logger.error(f"Error fetching account summary: {e}")
            # Return empty summary on error
            return {
                'total_cash': 0,
                'net_liquidation': 0,
                'gross_position_value': 0,
                'buying_power': 0,
                'available_funds': 0,
                'portfolio_value': 0,
                'cash_percentage': 0,
                'equity_percentage': 0,
                'currency': 'USD',
                'account_type': 'Unknown',
                'timestamp': datetime.now().isoformat(),
                'raw_data': {},
                'data_source': 'IBKR_ERROR'
            }
    
    def get_portfolio_positions(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get current portfolio positions with P&L
        
        Args:
            force_refresh: Force refresh cached data
            
        Returns:
            List of position dictionaries
        """
        cache_key = "portfolio_positions"
        
        # Check cache first unless forcing refresh
        if not force_refresh:
            cached = self.manager.get_cache(cache_key)
            if cached:
                logger.debug("Using cached portfolio positions")
                return cached
        
        try:
            with self.manager.ensure_connection() as ib:
                logger.info("Fetching fresh portfolio positions from IBKR...")
                
                # Get portfolio positions
                positions = ib.portfolio()
                
                position_list = []
                for pos in positions:
                    # Skip positions with zero quantity
                    if pos.position == 0:
                        continue
                    
                    position_dict = {
                        'symbol': pos.contract.symbol,
                        'exchange': pos.contract.exchange,
                        'currency': pos.contract.currency,
                        'sec_type': pos.contract.secType,
                        'position': float(pos.position),
                        'market_price': float(pos.marketPrice) if pos.marketPrice else 0.0,
                        'market_value': float(pos.marketValue) if pos.marketValue else 0.0,
                        'average_cost': float(pos.averageCost) if pos.averageCost else 0.0,
                        'unrealized_pnl': float(pos.unrealizedPNL) if pos.unrealizedPNL else 0.0,
                        'realized_pnl': float(pos.realizedPNL) if pos.realizedPNL else 0.0,
                        'contract_id': pos.contract.conId,
                        'account': pos.account
                    }
                    
                    # Calculate additional metrics
                    if position_dict['position'] != 0 and position_dict['average_cost'] > 0:
                        cost_basis = abs(position_dict['position']) * position_dict['average_cost']
                        if cost_basis > 0:
                            position_dict['unrealized_pnl_pct'] = position_dict['unrealized_pnl'] / cost_basis * 100
                        else:
                            position_dict['unrealized_pnl_pct'] = 0.0
                    else:
                        position_dict['unrealized_pnl_pct'] = 0.0
                    
                    # Position weight in portfolio
                    if position_dict['market_value'] != 0:
                        # We'll calculate this after we have total portfolio value
                        position_dict['position_weight_pct'] = 0.0
                    
                    position_list.append(position_dict)
                
                # Calculate position weights if we have positions
                if position_list:
                    total_portfolio_value = sum(abs(pos['market_value']) for pos in position_list)
                    if total_portfolio_value > 0:
                        for pos in position_list:
                            pos['position_weight_pct'] = abs(pos['market_value']) / total_portfolio_value * 100
                
                # Sort by market value (largest first)
                position_list.sort(key=lambda x: abs(x['market_value']), reverse=True)
                
                # Cache the results
                self.manager.set_cache(cache_key, position_list)
                
                logger.info(f"Retrieved {len(position_list)} portfolio positions")
                return position_list
                
        except Exception as e:
            logger.error(f"Error fetching portfolio positions: {e}")
            return []
    
    def get_open_orders(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get open orders
        
        Args:
            force_refresh: Force refresh cached data
            
        Returns:
            List of open order dictionaries
        """
        cache_key = "open_orders"
        
        # Check cache first unless forcing refresh  
        if not force_refresh:
            cached = self.manager.get_cache(cache_key)
            if cached:
                logger.debug("Using cached open orders")
                return cached
        
        try:
            with self.manager.ensure_connection() as ib:
                logger.info("Fetching open orders from IBKR...")
                
                # Get all orders
                orders = ib.orders()
                
                open_orders = []
                for order in orders:
                    # Only include orders that are still active
                    if order.orderStatus.status in ['PreSubmitted', 'Submitted', 'PendingSubmit']:
                        order_dict = {
                            'order_id': order.orderId,
                            'symbol': order.contract.symbol,
                            'action': order.order.action,  # BUY/SELL
                            'quantity': order.order.totalQuantity,
                            'order_type': order.order.orderType,  # MKT, LMT, STP, etc.
                            'limit_price': order.order.lmtPrice if order.order.lmtPrice else None,
                            'aux_price': order.order.auxPrice if order.order.auxPrice else None,
                            'status': order.orderStatus.status,
                            'filled': order.orderStatus.filled,
                            'remaining': order.orderStatus.remaining,
                            'avg_fill_price': order.orderStatus.avgFillPrice,
                            'commission': order.orderStatus.commission,
                            'parent_id': order.order.parentId,
                            'time_in_force': order.order.tif,
                            'account': order.order.account,
                            'perm_id': order.orderStatus.permId
                        }
                        open_orders.append(order_dict)
                
                # Cache the results
                self.manager.set_cache(cache_key, open_orders)
                
                logger.info(f"Retrieved {len(open_orders)} open orders")
                return open_orders
                
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []
    
    def get_complete_portfolio_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get complete portfolio data (summary + positions + orders)
        
        Args:
            force_refresh: Force refresh all cached data
            
        Returns:
            Complete portfolio data dictionary
        """
        try:
            logger.info("Fetching complete portfolio data...")
            
            # Get all data components
            account = self.get_account_summary(force_refresh)
            positions = self.get_portfolio_positions(force_refresh)
            orders = self.get_open_orders(force_refresh)
            
            # Calculate summary statistics
            summary = {
                'total_positions': len([p for p in positions if p['position'] != 0]),
                'total_cash': account['total_cash'],
                'portfolio_value': account['portfolio_value'], 
                'net_liquidation': account['net_liquidation'],
                'open_orders_count': len(orders),
                'largest_position': max(positions, key=lambda x: abs(x['market_value']))['symbol'] if positions else None,
                'total_unrealized_pnl': sum(p['unrealized_pnl'] for p in positions),
                'total_realized_pnl': sum(p['realized_pnl'] for p in positions),
                'risk_utilization': min(len(positions) / 20, 1.0),  # Assume max 20 positions for full risk
                'currency': account['currency'],
                'account_type': account['account_type'],
                'last_updated': datetime.now().isoformat()
            }
            
            complete_data = {
                'account': account,
                'positions': positions,
                'orders': orders,
                'summary': summary,
                'data_source': 'IBKR_COMPLETE',
                'timestamp': summary['last_updated']
            }
            
            logger.info(f"Complete portfolio: {summary['currency']} {summary['net_liquidation']:,.2f}, {summary['total_positions']} positions")
            return complete_data
            
        except Exception as e:
            logger.error(f"Error getting complete portfolio data: {e}")
            # Return empty structure on error
            return {
                'account': {},
                'positions': [],
                'orders': [],
                'summary': {
                    'total_positions': 0,
                    'total_cash': 0,
                    'portfolio_value': 0,
                    'net_liquidation': 0,
                    'open_orders_count': 0,
                    'largest_position': None,
                    'total_unrealized_pnl': 0,
                    'total_realized_pnl': 0,
                    'risk_utilization': 0.0,
                    'currency': 'USD',
                    'account_type': 'Unknown',
                    'last_updated': datetime.now().isoformat()
                },
                'data_source': 'IBKR_ERROR',
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_cache(self):
        """Clear all cached portfolio data"""
        self.manager.clear_cache("account_summary")
        self.manager.clear_cache("portfolio_positions") 
        self.manager.clear_cache("open_orders")
        logger.info("Portfolio cache cleared")


# Convenience functions for backward compatibility
def get_portfolio_data_sync() -> Dict[str, Any]:
    """Get complete portfolio data (backward compatibility)"""
    service = IBKRPortfolioService()
    return service.get_complete_portfolio_data()


def get_account_summary_sync() -> Dict[str, Any]:
    """Get account summary (backward compatibility)"""
    service = IBKRPortfolioService()
    return service.get_account_summary()


def get_positions_sync() -> List[Dict[str, Any]]:
    """Get portfolio positions (backward compatibility)"""
    service = IBKRPortfolioService()
    return service.get_portfolio_positions()


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    def test_portfolio_service():
        """Test the portfolio service"""
        print("Testing IBKR Portfolio Service...")
        
        # Initialize service
        service = IBKRPortfolioService()
        
        # Test account summary
        print("\n=== Testing Account Summary ===")
        account = service.get_account_summary()
        if account and account.get('data_source') == 'IBKR_LIVE':
            print(f"✅ Account: {account['currency']} {account['net_liquidation']:,.2f}")
            print(f"   Cash: {account['currency']} {account['total_cash']:,.2f}")
            print(f"   Portfolio: {account['currency']} {account['portfolio_value']:,.2f}")
        else:
            print("❌ Failed to get account summary")
            return False
        
        # Test positions
        print("\n=== Testing Portfolio Positions ===")
        positions = service.get_portfolio_positions()
        print(f"✅ Retrieved {len(positions)} positions")
        
        if positions:
            print("Top 3 positions:")
            for i, pos in enumerate(positions[:3]):
                print(f"  {i+1}. {pos['symbol']}: {pos['position']:,.0f} shares, "
                      f"{pos['currency']} {pos['market_value']:,.2f}, "
                      f"{pos['unrealized_pnl_pct']:+.1f}% P&L")
        
        # Test orders
        print("\n=== Testing Open Orders ===")
        orders = service.get_open_orders()
        print(f"✅ Retrieved {len(orders)} open orders")
        
        if orders:
            print("Open orders:")
            for order in orders:
                print(f"  {order['symbol']} {order['action']} {order['quantity']} @ "
                      f"{order['limit_price'] or 'MKT'} ({order['status']})")
        
        # Test complete data
        print("\n=== Testing Complete Portfolio ===")
        complete = service.get_complete_portfolio_data()
        if complete and complete.get('data_source') == 'IBKR_COMPLETE':
            summary = complete['summary']
            print(f"✅ Complete portfolio: {summary['currency']} {summary['net_liquidation']:,.2f}")
            print(f"   Positions: {summary['total_positions']}")
            print(f"   Orders: {summary['open_orders_count']}")
            print(f"   Unrealized P&L: {summary['currency']} {summary['total_unrealized_pnl']:+,.2f}")
        else:
            print("❌ Failed to get complete portfolio data")
            return False
        
        return True
    
    if test_portfolio_service():
        print("\n🎉 Portfolio service tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Portfolio service tests failed!")
        sys.exit(1)