#!/usr/bin/env python3
"""
Test script to verify KHAZAD_DUM reorganization
This script properly sets up the Python path
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports work"""
    print("\n" + "="*60)
    print("TESTING KHAZAD_DUM IMPORTS")
    print("="*60)
    
    results = []
    
    # Test imports
    tests = [
        ("Core - RegimeDetector", "from src.core.market_analysis.regime_detector import RegimeDetector"),
        ("Core - StockFilter", "from src.core.stock_screening.stock_filter import StockFilter"),
        ("Core - Patterns", "from src.core.pattern_recognition import PatternClassifier"),
        ("Core - Portfolio", "from src.core.portfolio_management import PortfolioConstructor"),
        ("Data - Database", "from src.data_pipeline.storage.database_manager import DatabaseManager"),
        ("Data - Fetcher", "from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher"),
        ("Trading - Batch", "from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor"),
        ("Trading - Broker", "from src.trading_engines.broker_connections.interfaces.mock_broker import MockBroker"),
    ]
    
    for name, import_str in tests:
        try:
            exec(import_str)
            results.append((name, "✅ SUCCESS"))
            print(f"  ✅ {name}: Import successful")
        except ImportError as e:
            results.append((name, f"❌ FAILED: {e}"))
            print(f"  ❌ {name}: {e}")
        except Exception as e:
            results.append((name, f"⚠️  ERROR: {e}"))
            print(f"  ⚠️  {name}: {e}")
    
    # Summary
    print("\n" + "="*60)
    successes = sum(1 for _, r in results if "SUCCESS" in r)
    total = len(results)
    
    if successes == total:
        print(f"✅ ALL {total} IMPORTS SUCCESSFUL!")
        print("\nYour KHAZAD_DUM project has been successfully reorganized!")
    else:
        print(f"⚠️  {successes}/{total} imports successful")
        print("\nSome imports still failing - check the errors above")
    
    return successes == total

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
