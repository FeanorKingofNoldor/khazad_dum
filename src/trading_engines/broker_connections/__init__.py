"""Broker Connections Module"""

from .interfaces.broker_interface import BrokerInterface
from .interfaces.mock_broker import MockBroker

try:
    # Import new centralized IBKR architecture
    from .implementations.ibkr_facade import IBKRPortfolioConnector, IBKRFacade
    from .implementations.ibkr_connection_manager import get_connection_manager
    from .implementations.ibkr_portfolio_service import IBKRPortfolioService
    from .implementations.ibkr_order_service import IBKROrderService
    
    # Keep old imports for backward compatibility
    from .implementations.ibkr_order_executor import IBKROrderExecutor
    
    __all__ = [
        'BrokerInterface', 'MockBroker', 
        # New centralized architecture (recommended)
        'IBKRFacade', 'get_connection_manager', 'IBKRPortfolioService', 'IBKROrderService',
        # Backward compatibility
        'IBKRPortfolioConnector', 'IBKROrderExecutor'
    ]
except ImportError:
    # IBKR not available
    __all__ = ['BrokerInterface', 'MockBroker']
