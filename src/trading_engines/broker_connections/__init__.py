"""Broker Connections Module"""

from .interfaces.broker_interface import BrokerInterface
from .interfaces.mock_broker import MockBroker

try:
    from .implementations.ibkr_connector import IBKRPortfolioConnector
    from .implementations.ibkr_order_executor import IBKROrderExecutor
    __all__ = ['BrokerInterface', 'MockBroker', 'IBKRPortfolioConnector', 'IBKROrderExecutor']
except ImportError:
    # IBKR not available
    __all__ = ['BrokerInterface', 'MockBroker']
