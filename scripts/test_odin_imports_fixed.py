#!/usr/bin/env python3
"""
Fixed KHAZAD_DUM import test script
Properly adds project root to Python path before importing
"""

import sys
import os
from pathlib import Path

# CRITICAL: Add parent directory (project root) to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

print(f"Added to path: {project_root}")

def test_imports():
    """Test that all imports work"""
    print("\n" + "="*60)
    print("TESTING KHAZAD_DUM IMPORTS (FIXED)")
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
        ("Compat Module", "from src.compat import Khazad_DumRegimeDetector, Khazad_DumDatabase, Khazad_DumDataFetcher"),
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
    
    # Test main.py
    print("\n5. Testing main.py import...")
    try:
        import main
        print("  ✅ main.py imports successfully")
        results.append(("main.py", "✅ SUCCESS"))
    except ImportError as e:
        print(f"  ❌ main.py import failed: {e}")
        results.append(("main.py", f"❌ FAILED: {e}"))
    except Exception as e:
        print(f"  ⚠️  main.py has issues: {e}")
        results.append(("main.py", f"⚠️  ERROR: {e}"))
    
    # Summary
    print("\n" + "="*60)
    print("IMPORT TEST RESULTS")
    print("="*60)
    
    successes = sum(1 for _, r in results if "SUCCESS" in r)
    total = len(results)
    
    if successes == total:
        print(f"✅ ALL {total} IMPORTS SUCCESSFUL!")
        print("\nYour KHAZAD_DUM project has been successfully reorganized!")
        print("\nYou can now run your main script:")
        print("  python main.py")
    else:
        print(f"⚠️  {successes}/{total} imports successful")
        failures = [name for name, r in results if "FAILED" in r or "ERROR" in r]
        if failures:
            print("\nFailed imports:")
            for name in failures:
                print(f"  • {name}")
    
    return successes == total

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)