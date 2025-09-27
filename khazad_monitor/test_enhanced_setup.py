#!/usr/bin/env python3
"""
Test Enhanced Monitor Setup
Verifies all components of the enhanced monitoring system work properly
"""

import os
import sys
import traceback

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from khazad_monitor.data_fetcher import DataFetcher
        print("✅ DataFetcher import successful")
        
        from khazad_monitor.enhanced_monitor import EnhancedMonitor
        print("✅ EnhancedMonitor import successful")
        
        # Test optional dependencies
        try:
            import rich
            print("✅ Rich library available")
        except ImportError:
            print("❌ Rich library not available - please install: pip install rich")
            return False
        
        try:
            import plotext
            print("✅ Plotext library available")
        except ImportError:
            print("❌ Plotext library not available - please install: pip install plotext")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_data_fetcher():
    """Test the DataFetcher with mock data"""
    print("\\n📊 Testing DataFetcher...")
    
    try:
        from khazad_monitor.data_fetcher import DataFetcher
        # Test with mock data
        fetcher = DataFetcher(use_mock=True)
        
        # Test portfolio positions
        positions = fetcher.get_portfolio_positions()
        print(f"✅ Mock positions loaded: {len(positions)} positions")
        
        # Test portfolio history
        dates, values = fetcher.get_portfolio_history(30)
        print(f"✅ Mock history loaded: {len(dates)} data points")
        
        # Test system metrics
        metrics = fetcher.get_system_metrics()
        print(f"✅ System metrics: {metrics.get('total_positions', 0)} positions")
        
        # Test recent signals
        signals = fetcher.get_recent_signals(5)
        print(f"✅ Recent signals: {len(signals)} signals")
        
        # Test market regime
        regime = fetcher.get_market_regime()
        print(f"✅ Market regime: {regime.get('regime', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ DataFetcher error: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection (if available)"""
    print("\\n🗄️  Testing database connection...")
    
    try:
        from khazad_monitor.data_fetcher import DataFetcher
        
        fetcher = DataFetcher(use_mock=False)
        if fetcher.init_db_connection():
            print("✅ Database connection successful")
            
            # Try to fetch some real data
            try:
                positions = fetcher.get_portfolio_positions()
                print(f"✅ Real data query successful: {len(positions)} positions")
                return True
            except Exception as e:
                print(f"⚠️  Database connected but query failed: {e}")
                print("   This is normal if database is empty")
                return True
        else:
            print("⚠️  Database connection failed - will use mock data")
            return True
            
    except Exception as e:
        print(f"⚠️  Database connection error: {e}")
        print("   This is normal if database doesn't exist yet")
        return True

def test_monitor_creation():
    """Test that the monitor can be created"""
    print("\\n🖥️  Testing monitor creation...")
    
    try:
        from khazad_monitor.enhanced_monitor import EnhancedMonitor
        
        # Create monitor with mock data
        monitor = EnhancedMonitor(use_mock=True)
        print("✅ EnhancedMonitor created successfully")
        
        # Test layout creation
        layout = monitor.create_layout()
        print("✅ Layout created successfully")
        
        # Test panel creation (without running the live interface)
        header = monitor.create_header()
        print("✅ Header panel created")
        
        summary = monitor.create_portfolio_summary()
        print("✅ Portfolio summary created")
        
        positions = monitor.create_positions_table()
        print("✅ Positions table created")
        
        signals = monitor.create_signals_table()
        print("✅ Signals table created")
        
        footer = monitor.create_footer()
        print("✅ Footer created")
        
        # Test chart creation (might fail if plotext has issues)
        try:
            chart = monitor.create_portfolio_chart()
            print("✅ Portfolio chart created")
        except Exception as e:
            print(f"⚠️  Chart creation warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitor creation error: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\\n📁 Testing file structure...")
    
    required_files = [
        'khazad_monitor/data_fetcher.py',
        'khazad_monitor/enhanced_monitor.py', 
        'khazad_monitor/run_enhanced.py',
        'khazad_monitor/ENHANCED_MONITOR_README.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - missing!")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🚀 Enhanced Monitor Setup Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("DataFetcher", test_data_fetcher),
        ("Database Connection", test_database_connection),
        ("Monitor Creation", test_monitor_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\\n🏆 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\\n🎉 All tests passed! Enhanced monitor is ready to use.")
        print("\\nQuick start:")
        print("  python khazad_monitor/run_enhanced.py --demo")
    else:
        print(f"\\n⚠️  {total - passed} test(s) failed. Check the errors above.")
        print("\\nCommon fixes:")
        print("  pip install rich plotext")
        print("  export PYTHONPATH=/path/to/khazad_dum:$PYTHONPATH")

if __name__ == "__main__":
    main()