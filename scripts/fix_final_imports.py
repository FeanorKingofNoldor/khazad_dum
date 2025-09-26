#!/usr/bin/env python3
"""
Fix remaining import issues in KHAZAD_DUM reorganization
"""

from pathlib import Path

def fix_pattern_recognition_init():
    """Fix src/core/pattern_recognition/__init__.py"""
    
    init_file = Path("src/core/pattern_recognition/__init__.py")
    
    content = '''"""Pattern Recognition Module"""

from .pattern_classifier import PatternClassifier
from .pattern_tracker import PatternTracker
from .pattern_database import PatternDatabase
from .memory_injector import PatternMemoryInjector

__all__ = [
    'PatternClassifier',
    'PatternTracker',
    'PatternDatabase',
    'PatternMemoryInjector'
]
'''
    
    with open(init_file, 'w') as f:
        f.write(content)
    
    print("✓ Fixed pattern_recognition __init__.py")


def fix_portfolio_management_init():
    """Fix src/core/portfolio_management/__init__.py"""
    
    init_file = Path("src/core/portfolio_management/__init__.py")
    
    content = '''"""Portfolio Management Module"""

from .portfolio_constructor import PortfolioConstructor
from .position_tracker import PositionTracker
from .performance_observer import PerformanceObserver

__all__ = [
    'PortfolioConstructor',
    'PositionTracker',
    'PerformanceObserver'
]
'''
    
    with open(init_file, 'w') as f:
        f.write(content)
    
    print("✓ Fixed portfolio_management __init__.py")


def fix_batch_processor_imports():
    """Fix imports in batch_processor.py"""
    
    batch_file = Path("src/trading_engines/tradingagents_integration/batch_processor.py")
    
    if batch_file.exists():
        with open(batch_file, 'r') as f:
            content = f.read()
        
        # Fix the tradingagents import
        content = content.replace(
            "from tradingagents.agents import",
            "from tradingagents_lib.tradingagents.agents import"
        )
        
        content = content.replace(
            "from tradingagents import",
            "from tradingagents_lib.tradingagents import"
        )
        
        content = content.replace(
            "import tradingagents",
            "import tradingagents_lib.tradingagents as tradingagents"
        )
        
        with open(batch_file, 'w') as f:
            f.write(content)
        
        print("✓ Fixed batch_processor.py imports")


def fix_agent_coordinator_imports():
    """Fix imports in agent_coordinator.py"""
    
    coord_file = Path("src/trading_engines/tradingagents_integration/agent_coordinator.py")
    
    if coord_file.exists():
        with open(coord_file, 'r') as f:
            content = f.read()
        
        # Fix tradingagents imports
        content = content.replace(
            "from tradingagents.",
            "from tradingagents_lib.tradingagents."
        )
        
        content = content.replace(
            "import tradingagents",
            "import tradingagents_lib.tradingagents as tradingagents"
        )
        
        with open(coord_file, 'w') as f:
            f.write(content)
        
        print("✓ Fixed agent_coordinator.py imports")


def fix_broker_connections_init():
    """Fix src/trading_engines/broker_connections/__init__.py"""
    
    init_file = Path("src/trading_engines/broker_connections/__init__.py")
    
    content = '''"""Broker Connections Module"""

from .interfaces.broker_interface import BrokerInterface
from .interfaces.mock_broker import MockBroker

try:
    from .implementations.ibkr_connector import IBKRPortfolioConnector
    from .implementations.ibkr_order_executor import IBKROrderExecutor
    __all__ = ['BrokerInterface', 'MockBroker', 'IBKRPortfolioConnector', 'IBKROrderExecutor']
except ImportError:
    # IBKR not available
    __all__ = ['BrokerInterface', 'MockBroker']
'''
    
    with open(init_file, 'w') as f:
        f.write(content)
    
    print("✓ Fixed broker_connections __init__.py")


def fix_main_py_imports():
    """Fix imports in main.py"""
    
    main_file = Path("main.py")
    
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Fix tradingagents imports
        if "from tradingagents" in content or "import tradingagents" in content:
            content = content.replace(
                "from tradingagents.",
                "from tradingagents_lib.tradingagents."
            )
            
            content = content.replace(
                "import tradingagents",
                "import tradingagents_lib.tradingagents as tradingagents"
            )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        print("✓ Fixed main.py imports")


def fix_compat_module():
    """Update src/compat.py with correct imports"""
    
    compat_file = Path("src/compat.py")
    
    content = '''"""
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

from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor as TradingAgentsBatchProcessor

# Portfolio management
from src.core.portfolio_management.portfolio_constructor import PortfolioConstructor
from src.core.portfolio_management.position_tracker import PositionTracker
from src.core.portfolio_management.performance_observer import PerformanceObserver

print("Using compatibility module - consider updating imports to use new names directly")
'''
    
    with open(compat_file, 'w') as f:
        f.write(content)
    
    print("✓ Fixed compat.py")


def check_tradingagents_lib():
    """Verify tradingagents_lib exists and create symlink if needed"""
    
    lib_path = Path("tradingagents_lib")
    
    if lib_path.exists():
        # Check if it has the expected structure
        agents_path = lib_path / "tradingagents" / "agents"
        if agents_path.exists():
            print("✓ tradingagents_lib structure looks correct")
        else:
            print("⚠ tradingagents_lib exists but missing agents module")
            print("  Check that tradingagents_lib/tradingagents/agents/ exists")
    else:
        print("⚠ tradingagents_lib not found at project root")
        print("  This is required for TradingAgents functionality")


def main():
    print("\n" + "="*60)
    print("FIXING REMAINING IMPORT ISSUES")
    print("="*60)
    
    print("\n1. Fixing module __init__.py files:")
    fix_pattern_recognition_init()
    fix_portfolio_management_init()
    fix_broker_connections_init()
    
    print("\n2. Fixing TradingAgents imports:")
    fix_batch_processor_imports()
    fix_agent_coordinator_imports()
    fix_main_py_imports()
    
    print("\n3. Fixing compatibility module:")
    fix_compat_module()
    
    print("\n4. Checking tradingagents_lib:")
    check_tradingagents_lib()
    
    print("\n" + "="*60)
    print("✅ FIXES APPLIED")
    print("="*60)
    
    print("\nNow test again with:")
    print("  python scripts/test_khazad_dum_imports_fixed.py")
    print("\nOr test individual imports:")
    print("  python -c \"from src.core.pattern_recognition import PatternClassifier; print('✓ Patterns work')\"")
    print("  python -c \"from src.core.portfolio_management import PortfolioConstructor; print('✓ Portfolio works')\"")


if __name__ == "__main__":
    main()