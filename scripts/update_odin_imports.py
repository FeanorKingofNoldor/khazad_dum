#!/usr/bin/env python3
"""
KHAZAD_DUM Import Update Script
Updates all Python imports after project reorganization
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ImportUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.import_mappings = self.create_import_mappings()
        self.files_updated = 0
        self.imports_updated = 0
        
    def create_import_mappings(self) -> Dict[str, str]:
        """Create mappings from old imports to new imports"""
        return {
            # Core - Market Analysis
            'src.core.market_analysis.regime_detector': 'src.core.market_analysis.regime_detector',
            'src.core.market_analysis.cnn_feed_parser': 'src.core.market_analysis.cnn_feed_parser',
            'from src.core.market_analysis import': 'from src.core.market_analysis import',
            
            # Core - Stock Screening
            'src.core.stock_screening.stock_filter': 'src.core.stock_screening.stock_filter',
            'from src.core.stock_screening import': 'from src.core.stock_screening import',
            
            # Core - Pattern Recognition
            'src.core.pattern_recognition.pattern_classifier': 'src.core.pattern_recognition.pattern_classifier',
            'src.core.pattern_recognition.pattern_tracker': 'src.core.pattern_recognition.pattern_tracker',
            'src.core.pattern_recognition.pattern_database': 'src.core.pattern_recognition.pattern_database',
            'src.core.pattern_recognition.memory_injector': 'src.core.pattern_recognition.memory_injector',
            'src.core.pattern_recognition.memory_bridge': 'src.core.pattern_recognition.memory_bridge',
            'from src.core.pattern_recognition import': 'from src.core.pattern_recognition import',
            'src.core.pattern_recognition': 'src.core.pattern_recognition',
            
            # Core - Portfolio Management
            'src.core.portfolio_management.portfolio_constructor': 'src.core.portfolio_management.portfolio_constructor',
            'src.core.portfolio_management.position_tracker': 'src.core.portfolio_management.position_tracker',
            'src.core.portfolio_management.performance_observer': 'src.core.portfolio_management.performance_observer',
            'from src.core.portfolio_management import': 'from src.core.portfolio_management import',
            'from src.core.portfolio_management import': 'from src.core.portfolio_management import',
            
            # Data Pipeline
            'src.data_pipeline.market_data.stock_data_fetcher': 'src.data_pipeline.market_data.stock_data_fetcher',
            'src.data_pipeline.storage.database_manager': 'src.data_pipeline.storage.database_manager',
            'from src.data_pipeline.storage import': 'from src.data_pipeline.storage import',
            
            # Trading Engines - TradingAgents
            'src.trading_engines.tradingagents_integration.agent_wrapper': 'src.trading_engines.tradingagents_integration.agent_wrapper',
            'src.trading_engines.tradingagents_integration.agent_coordinator': 'src.trading_engines.tradingagents_integration.agent_coordinator',
            'src.trading_engines.tradingagents_integration.portfolio_context': 'src.trading_engines.tradingagents_integration.portfolio_context',
            'src.trading_engines.tradingagents_integration.batch_processor': 'src.trading_engines.tradingagents_integration.batch_processor',
            'from src.trading_engines.tradingagents_integration import': 'from src.trading_engines.tradingagents_integration import',
            'from src.trading_engines.tradingagents_integration import': 'from src.trading_engines.tradingagents_integration import',
            
            # Trading Engines - Brokers
            'src.trading_engines.broker_connections.interfaces.broker_interface': 'src.trading_engines.broker_connections.interfaces.broker_interface',
            'src.trading_engines.broker_connections.interfaces.mock_broker': 'src.trading_engines.broker_connections.interfaces.mock_broker',
            'src.trading_engines.broker_connections.implementations.ibkr_connector': 'src.trading_engines.broker_connections.implementations.ibkr_connector',
            'src.trading_engines.broker_connections.implementations.ibkr_order_executor': 'src.trading_engines.broker_connections.implementations.ibkr_order_executor',
            'from src.trading_engines.broker_connections.interfaces import': 'from src.trading_engines.broker_connections.interfaces import',
            'from src.trading_engines.broker_connections.implementations import': 'from src.trading_engines.broker_connections.implementations import',
            
            # Integrations
            'src.integrations.pattern_enhancement': 'src.integrations.pattern_enhancement',
            
            # Config
            'config.settings.base_config': 'config.settings.base_config.base_config',
            'from config.settings.base_config import': 'from config.settings.base_config.base_config import',
            
            # Class name changes
            'StockFilter': 'StockFilter',
            'StockDataFetcher': 'StockDataFetcher',
            'DatabaseManager': 'DatabaseManager',
            'RegimeDetector': 'RegimeDetector',
            'AgentWrapper': 'AgentWrapper',
            'BatchProcessor': 'BatchProcessor',
            'PatternEnhancement': 'PatternEnhancement',
            'PortfolioConstructor': 'PortfolioConstructor',  # Stays same
            'PositionTracker': 'PositionTracker',  # Stays same
            'PerformanceObserver': 'PerformanceObserver',  # Stays same
            'CNNFeedParser': 'CNNFeedParser',
        }
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        
        # Directories to search
        search_dirs = ['src', 'tests', 'scripts']
        
        for dir_name in search_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                python_files.extend(dir_path.rglob('*.py'))
        
        # Add main.py if it exists
        main_py = self.project_root / 'main.py'
        if main_py.exists():
            python_files.append(main_py)
            
        return python_files
    
    def update_imports_in_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """Update imports in a single file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            original_content = content
            changes_made = []
            
            # Apply import mappings
            for old_import, new_import in self.import_mappings.items():
                if old_import in content:
                    # Count occurrences
                    occurrences = content.count(old_import)
                    
                    # Replace
                    content = content.replace(old_import, new_import)
                    
                    if occurrences > 0:
                        changes_made.append(f"{old_import} -> {new_import} ({occurrences}x)")
            
            # Update relative imports if needed
            content = self.update_relative_imports(file_path, content)
            
            # Save if changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                return len(changes_made), changes_made
            
            return 0, []
            
        except Exception as e:
            print(f"  ✗ Error updating {file_path}: {e}")
            return 0, []
    
    def update_relative_imports(self, file_path: Path, content: str) -> str:
        """Update relative imports based on new file location"""
        # This is complex and depends on the specific file location
        # For now, we'll handle the most common cases
        
        # Get the file's new package path
        rel_path = file_path.relative_to(self.project_root)
        
        # Common relative import patterns to update
        if 'src/core' in str(rel_path):
            # Update imports between core modules
            content = re.sub(
                r'from \.\. import (\w+)',
                r'from src.core import \1',
                content
            )
            
        if 'src/data_pipeline' in str(rel_path):
            # Update imports between data pipeline modules
            content = re.sub(
                r'from \.\. import (\w+)',
                r'from src.data_pipeline import \1',
                content
            )
            
        return content
    
    def update_config_references(self):
        """Update references to configuration files"""
        print("\nUpdating configuration references...")
        
        # Update DATABASE_PATH references
        config_file = self.project_root / 'config/settings/base_config.py'
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                
            # Update path references
            content = content.replace(
                'DATABASE_PATH = PROJECT_ROOT / "data" / "khazad_dum.db"',
                'DATABASE_PATH = PROJECT_ROOT / "data" / "databases" / "khazad_dum.db"'
            )
            
            with open(config_file, 'w') as f:
                f.write(content)
                
            print("  ✓ Updated database path in config")
    
    def create_module_aliases(self):
        """Create compatibility aliases for commonly used modules"""
        print("\nCreating compatibility module aliases...")
        
        # Create a compatibility module for easier migration
        compat_file = self.project_root / 'src' / 'compat.py'
        
        compat_content = '''"""
Compatibility module for easier migration
Provides aliases to commonly used classes with their old names
"""

# Core modules
from src.core.market_analysis.regime_detector import RegimeDetector as RegimeDetector
from src.core.stock_screening.stock_filter import StockFilter as StockFilter
from src.core.pattern_recognition import (
    PatternClassifier,
    PatternTracker,
    PatternDatabase,
    PatternMemoryInjector
)

# Data pipeline
from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher as StockDataFetcher
from src.data_pipeline.storage.database_manager import DatabaseManager as DatabaseManager

# Trading engines
from src.trading_engines.tradingagents_integration.agent_wrapper import AgentWrapper as AgentWrapper
from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor as BatchProcessor

# Portfolio management
from src.core.portfolio_management import (
    PortfolioConstructor,
    PositionTracker,
    PerformanceObserver
)

print("Using compatibility module - consider updating imports to use new names directly")
'''
        
        with open(compat_file, 'w') as f:
            f.write(compat_content)
            
        print("  ✓ Created src/compat.py for backward compatibility")
    
    def run(self):
        """Execute the import update process"""
        print("\n" + "="*60)
        print("UPDATING PYTHON IMPORTS")
        print("="*60)
        
        # Find all Python files
        python_files = self.find_python_files()
        print(f"\nFound {len(python_files)} Python files to check")
        
        # Update imports in each file
        total_changes = 0
        files_with_changes = []
        
        for file_path in python_files:
            changes_count, changes = self.update_imports_in_file(file_path)
            
            if changes_count > 0:
                self.files_updated += 1
                total_changes += changes_count
                files_with_changes.append((file_path, changes))
                print(f"  ✓ Updated {file_path.relative_to(self.project_root)}: {changes_count} changes")
        
        # Update config references
        self.update_config_references()
        
        # Create compatibility module
        self.create_module_aliases()
        
        # Print summary
        print("\n" + "="*60)
        print("IMPORT UPDATE SUMMARY")
        print("="*60)
        print(f"✓ Files updated: {self.files_updated}")
        print(f"✓ Total import changes: {total_changes}")
        
        if files_with_changes:
            print("\nDetailed changes:")
            for file_path, changes in files_with_changes[:10]:  # Show first 10
                print(f"\n{file_path.relative_to(self.project_root)}:")
                for change in changes[:3]:  # Show first 3 changes per file
                    print(f"  • {change}")
        
        print("\n" + "="*60)
        print("✅ IMPORT UPDATE COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run tests to verify everything works")
        print("2. Update any missed imports manually")
        print("3. Consider removing src/compat.py after full migration")


if __name__ == "__main__":
    print("\n⚠️  This script will update all Python imports in your project.")
    print("It should be run AFTER the reorganization script.")
    
    response = input("\nHave you run the reorganization script? (yes/no): ")
    
    if response.lower() == 'yes':
        updater = ImportUpdater()
        updater.run()
    else:
        print("Please run reorganize_khazad_dum_structure.py first, then run this script.")