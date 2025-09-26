#!/usr/bin/env python3
"""
Fix Python module import issues for KHAZAD_DUM project
Ensures all __init__.py files exist and paths are correct
"""

import os
import sys
from pathlib import Path

class ImportFixer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        
    def create_all_init_files(self):
        """Create __init__.py files in ALL Python packages"""
        print("\n1. Creating __init__.py files...")
        
        # Define all directories that need __init__.py
        packages = [
            "src",
            "src/core",
            "src/core/market_analysis",
            "src/core/stock_screening",
            "src/core/pattern_recognition",
            "src/core/portfolio_management",
            "src/data_pipeline",
            "src/data_pipeline/market_data",
            "src/data_pipeline/storage",
            "src/data_pipeline/external_apis",
            "src/trading_engines",
            "src/trading_engines/tradingagents_integration",
            "src/trading_engines/broker_connections",
            "src/trading_engines/broker_connections/interfaces",
            "src/trading_engines/broker_connections/implementations",
            "src/integrations",
            "tests",
            "tests/unit",
            "tests/unit/core",
            "tests/unit/data_pipeline",
            "tests/integration",
            "tests/fixtures",
            "config",
            "config/settings",
            "config/environments",
            "scripts",
            "scripts/daily_operations",
            "scripts/maintenance",
            "scripts/setup",
        ]
        
        created_count = 0
        for package_path in packages:
            full_path = self.project_root / package_path
            if full_path.exists():
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_content = f'"""{package_path} package"""\n'
                    
                    # Add special content for certain packages
                    if package_path == "src/core/pattern_recognition":
                        init_content += '''
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
                    elif package_path == "src/core/portfolio_management":
                        init_content += '''
from .portfolio_constructor import PortfolioConstructor
from .position_tracker import PositionTracker
from .performance_observer import PerformanceObserver

__all__ = [
    'PortfolioConstructor',
    'PositionTracker',
    'PerformanceObserver'
]
'''
                    elif package_path == "src/trading_engines/broker_connections":
                        init_content += '''
from .interfaces.broker_interface import BrokerInterface
from .interfaces.mock_broker import MockBroker

__all__ = ['BrokerInterface', 'MockBroker']
'''
                    
                    with open(init_file, 'w') as f:
                        f.write(init_content)
                    created_count += 1
                    print(f"  ✓ Created {init_file.relative_to(self.project_root)}")
            else:
                print(f"  ⚠ Directory doesn't exist: {package_path}")
        
        print(f"\n  Total __init__.py files created: {created_count}")
        
    def fix_class_names_in_files(self):
        """Update class names in the moved files"""
        print("\n2. Updating class names in files...")
        
        updates = {
            "src/core/market_analysis/regime_detector.py": [
                ("class Khazad_DumRegimeDetector", "class RegimeDetector"),
                ("Khazad_DumRegimeDetector", "RegimeDetector")  # in docstrings
            ],
            "src/core/stock_screening/stock_filter.py": [
                ("class Khazad_DumFilter", "class StockFilter"),
            ],
            "src/data_pipeline/storage/database_manager.py": [
                ("class Khazad_DumDatabase", "class DatabaseManager"),
            ],
            "src/data_pipeline/market_data/stock_data_fetcher.py": [
                ("class Khazad_DumDataFetcher", "class StockDataFetcher"),
            ],
            "src/trading_engines/tradingagents_integration/batch_processor.py": [
                ("class TradingAgentsBatchProcessor", "class BatchProcessor"),
            ],
            "src/core/market_analysis/cnn_feed_parser.py": [
                ("class CNNFearGreedIndex", "class CNNFeedParser"),
            ],
        }
        
        for file_path, replacements in updates.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    content = f.read()
                
                changed = False
                for old, new in replacements:
                    if old in content:
                        content = content.replace(old, new)
                        changed = True
                
                if changed:
                    with open(full_path, 'w') as f:
                        f.write(content)
                    print(f"  ✓ Updated class names in {file_path}")
            else:
                print(f"  ⚠ File not found: {file_path}")
    
    def create_project_root_init(self):
        """Create a special __init__.py at project root for easier imports"""
        print("\n3. Creating project root __init__.py...")
        
        root_init = self.project_root / "__init__.py"
        content = '''"""KHAZAD_DUM Trading System"""

# Add src to Python path for easier imports
import sys
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
'''
        
        with open(root_init, 'w') as f:
            f.write(content)
        print("  ✓ Created root __init__.py")
    
    def update_test_imports(self):
        """Fix imports in test files to work from project root"""
        print("\n4. Updating test file imports...")
        
        test_files = list((self.project_root / "tests").rglob("*.py"))
        
        for test_file in test_files:
            if "__pycache__" in str(test_file):
                continue
                
            with open(test_file, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Common import fixes for tests
            replacements = [
                # Add sys.path setup at the beginning if not present
                ("#!/usr/bin/env python3", 
                 "#!/usr/bin/env python3\n\nimport sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))"),
                
                # Fix class names
                ("Khazad_DumDatabase", "DatabaseManager"),
                ("Khazad_DumDataFetcher", "StockDataFetcher"),
                ("Khazad_DumFilter", "StockFilter"),
                ("Khazad_DumRegimeDetector", "RegimeDetector"),
                ("Khazad_DumTradingAgentsWrapper", "AgentWrapper"),
                ("TradingAgentsBatchProcessor", "BatchProcessor"),
            ]
            
            # Apply replacements
            for old, new in replacements:
                if old in content and new not in content:
                    content = content.replace(old, new)
            
            # Only write if changed
            if content != original_content:
                with open(test_file, 'w') as f:
                    f.write(content)
                print(f"  ✓ Updated {test_file.relative_to(self.project_root)}")
    
    def create_working_test_script(self):
        """Create a test script that will definitely work"""
        print("\n5. Creating working test script...")
        
        test_script = self.project_root / "test_reorganization.py"
        content = '''#!/usr/bin/env python3
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
    print("\\n" + "="*60)
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
    print("\\n" + "="*60)
    successes = sum(1 for _, r in results if "SUCCESS" in r)
    total = len(results)
    
    if successes == total:
        print(f"✅ ALL {total} IMPORTS SUCCESSFUL!")
        print("\\nYour KHAZAD_DUM project has been successfully reorganized!")
    else:
        print(f"⚠️  {successes}/{total} imports successful")
        print("\\nSome imports still failing - check the errors above")
    
    return successes == total

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
'''
        
        with open(test_script, 'w') as f:
            f.write(content)
        
        # Make it executable
        test_script.chmod(0o755)
        
        print(f"  ✓ Created {test_script.name}")
    
    def run(self):
        """Run all fixes"""
        print("\n" + "="*60)
        print("FIXING PYTHON IMPORT ISSUES")
        print("="*60)
        
        self.create_all_init_files()
        self.fix_class_names_in_files()
        self.create_project_root_init()
        self.update_test_imports()
        self.create_working_test_script()
        
        print("\n" + "="*60)
        print("✅ FIXES COMPLETE")
        print("="*60)
        
        print("\nNow test your imports:")
        print("  python test_reorganization.py")
        
        print("\nIf imports still fail, you can also try:")
        print("  cd [project_root]")
        print("  python -m pytest tests/  # Run tests as modules")
        print("  python -c \"from src.core.market_analysis.regime_detector import RegimeDetector; print('Success!')\"")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix KHAZAD_DUM import issues")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()
    
    fixer = ImportFixer(args.root)
    fixer.run()