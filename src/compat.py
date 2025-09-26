"""
Compatibility module for easier migration
Provides aliases to commonly used classes with their old names
"""

# Core modules
from src.core.market_analysis.regime_detector import RegimeDetector as Khazad_DumRegimeDetector
from src.core.stock_screening.stock_filter import StockFilter as Khazad_DumFilter

# Pattern recognition - import individual classes
from src.core.pattern_recognition.pattern_classifier import PatternClassifier
from src.core.pattern_recognition.pattern_tracker import PatternTracker
from src.core.pattern_recognition.pattern_database import PatternDatabase
from src.core.pattern_recognition.memory_injector import PatternMemoryInjector

# Data pipeline
from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher as Khazad_DumDataFetcher
from src.data_pipeline.storage.database_manager import DatabaseManager as Khazad_DumDatabase

# Trading engines
try:
    from src.trading_engines.tradingagents_integration.agent_wrapper import AgentWrapper as Khazad_DumTradingAgentsWrapper
except ImportError:
    from src.trading_engines.tradingagents_integration.agent_coordinator import Khazad_DumTradingAgentsCoordinator as Khazad_DumTradingAgentsWrapper

try:
    from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor as TradingAgentsBatchProcessor
except ImportError:
    TradingAgentsBatchProcessor = None

# Portfolio management
from src.core.portfolio_management.portfolio_constructor import PortfolioConstructor
from src.core.portfolio_management.position_tracker import PositionTracker
from src.core.portfolio_management.performance_observer import PerformanceObserver

print("Using compatibility module - consider updating imports to use new names directly")
