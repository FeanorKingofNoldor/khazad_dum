#!/usr/bin/env python3
"""
Quick test to verify reorganized KHAZAD_DUM imports work correctly
"""

import sys
from pathlib import Path

def test_imports():
    """Test that key imports work after reorganization"""
    
    print("\n" + "="*60)
    print("TESTING KHAZAD_DUM IMPORTS")
    print("="*60)
    
    successes = []
    failures = []
    
    # Test core imports
    print("\n1. Testing Core Modules...")
    
    try:
        from src.core.market_analysis.regime_detector import RegimeDetector
        successes.append("✓ RegimeDetector imports correctly")
    except ImportError as e:
        failures.append(f"✗ RegimeDetector import failed: {e}")
    
    try:
        from src.core.stock_screening.stock_filter import StockFilter
        successes.append("✓ StockFilter imports correctly")
    except ImportError as e:
        failures.append(f"✗ StockFilter import failed: {e}")
    
    try:
        from src.core.pattern_recognition import PatternClassifier
        successes.append("✓ PatternClassifier imports correctly")
    except ImportError as e:
        failures.append(f"✗ PatternClassifier import failed: {e}")
    
    try:
        from src.core.portfolio_management import PortfolioConstructor
        successes.append("✓ PortfolioConstructor imports correctly")
    except ImportError as e:
        failures.append(f"✗ PortfolioConstructor import failed: {e}")
    
    # Test data pipeline imports
    print("\n2. Testing Data Pipeline...")
    
    try:
        from src.data_pipeline.storage.database_manager import DatabaseManager
        successes.append("✓ DatabaseManager imports correctly")
    except ImportError as e:
        failures.append(f"✗ DatabaseManager import failed: {e}")
    
    try:
        from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher
        successes.append("✓ StockDataFetcher imports correctly")
    except ImportError as e:
        failures.append(f"✗ StockDataFetcher import failed: {e}")
    
    # Test trading engines imports
    print("\n3. Testing Trading Engines...")
    
    try:
        from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor
        successes.append("✓ BatchProcessor imports correctly")
    except ImportError as e:
        failures.append(f"✗ BatchProcessor import failed: {e}")
    
    try:
        from src.trading_engines.broker_connections.interfaces.mock_broker import MockBroker
        successes.append("✓ MockBroker imports correctly")
    except ImportError as e:
        failures.append(f"✗ MockBroker import failed: {e}")
    
    # Test compatibility module
    print("\n4. Testing Compatibility Module...")
    
    try:
        from src.compat import (
            Khazad_DumRegimeDetector, 
            Khazad_DumDatabase, 
            Khazad_DumDataFetcher,
            Khazad_DumFilter,
            Khazad_DumTradingAgentsWrapper
        )
        successes.append("✓ Compatibility module works")
    except ImportError as e:
        failures.append(f"✗ Compatibility module failed: {e}")
    
    # Print results
    print("\n" + "="*60)
    print("IMPORT TEST RESULTS")
    print("="*60)
    
    if successes:
        print("\n✅ SUCCESSES:")
        for success in successes:
            print(f"  {success}")
    
    if failures:
        print("\n❌ FAILURES:")
        for failure in failures:
            print(f"  {failure}")
    
    print("\n" + "="*60)
    
    if not failures:
        print("✅ ALL IMPORTS SUCCESSFUL!")
        print("\nYour KHAZAD_DUM reorganization is complete and working!")
        return True
    else:
        print(f"❌ {len(failures)} IMPORT FAILURES DETECTED")
        print("\nTo fix:")
        print("1. Run the fix script: python fix_khazad_dum_reorg_issues.py")
        print("2. Check if files exist in the expected locations")
        print("3. Ensure __init__.py files exist in all packages")
        return False


def test_main_execution():
    """Test if main.py can be imported"""
    print("\n5. Testing main.py...")
    
    try:
        # Try importing main
        import main
        print("  ✓ main.py imports successfully")
        return True
    except ImportError as e:
        print(f"  ✗ main.py import failed: {e}")
        return False
    except Exception as e:
        print(f"  ⚠ main.py imported but has issues: {e}")
        return False


if __name__ == "__main__":
    # Run import tests
    imports_ok = test_imports()
    
    # Test main.py
    main_ok = test_main_execution()
    
    # Overall result
    if imports_ok and main_ok:
        print("\n🎉 SUCCESS: Your KHAZAD_DUM project has been successfully reorganized!")
        sys.exit(0)
    else:
        print("\n⚠️  Some issues remain - please run the fix script")
        sys.exit(1)