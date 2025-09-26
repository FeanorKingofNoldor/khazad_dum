#!/usr/bin/env python3
"""
Fix script for remaining KHAZAD_DUM reorganization issues
"""

import os
import shutil
from pathlib import Path
import json

class Khazad_DumReorgFixer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.fixes_made = []
        
    def find_missing_files(self):
        """Find files that weren't moved but might exist elsewhere"""
        print("\n1. Looking for missing files...")
        
        missing_files = {
            'wrapper.py': 'src/trading_engines/tradingagents_integration/agent_wrapper.py',
            'test_fetcher.py': 'tests/unit/data_pipeline/test_fetcher.py',
            'test_tradingagents.py': 'tests/integration/test_tradingagents_integration.py',
            'test_mock_broker_complete.py': 'tests/integration/test_mock_broker.py',
            'test_pattern_integration.py': 'tests/integration/test_pattern_system.py',
            'test_khazad_dum_mock_integration.py': 'tests/integration/test_khazad_dum_mock_integration.py',
            'test_portfolio_constructor.py': 'tests/unit/core/test_portfolio_constructor.py',
            'test_memory_matching.py': 'tests/unit/core/test_pattern_memory.py',
        }
        
        # Check various locations
        search_locations = [
            'src/tradingagents',
            'src/tests',
            'src',
            'tests',
            '.',
        ]
        
        for filename, target_path in missing_files.items():
            found = False
            for location in search_locations:
                possible_path = self.project_root / location / filename
                if possible_path.exists():
                    target = self.project_root / target_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        shutil.move(str(possible_path), str(target))
                        print(f"  ✓ Found and moved {filename} to {target_path}")
                        self.fixes_made.append(f"Moved {filename}")
                        found = True
                        break
                    except Exception as e:
                        print(f"  ✗ Error moving {filename}: {e}")
            
            if not found:
                # Check if it's in backup
                backup_dirs = list(self.project_root.glob("backup_*"))
                if backup_dirs:
                    backup_dir = sorted(backup_dirs)[-1]
                    backup_file = backup_dir / 'src/tradingagents' / filename
                    if backup_file.exists():
                        target = self.project_root / target_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(backup_file, target)
                        print(f"  ✓ Restored {filename} from backup")
                        self.fixes_made.append(f"Restored {filename} from backup")
                        found = True
                
            if not found:
                print(f"  ⚠ Could not find {filename}")
    
    def fix_verification_script(self):
        """Fix the verification script's imports"""
        print("\n2. Fixing verification script imports...")
        
        verify_script = self.project_root / 'scripts/verify_khazad_dum_reorganization.py'
        if verify_script.exists():
            with open(verify_script, 'r') as f:
                content = f.read()
            
            # The verification script shouldn't have any project imports
            # It should only use standard library
            if 'from src.' in content or 'import src.' in content:
                # Remove any src imports
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if not ('from src.' in line or 'import src.' in line):
                        new_lines.append(line)
                
                content = '\n'.join(new_lines)
                
                with open(verify_script, 'w') as f:
                    f.write(content)
                
                print("  ✓ Fixed verification script")
                self.fixes_made.append("Fixed verification script")
        
    def cleanup_empty_tests_dirs(self):
        """Clean up the old test directories"""
        print("\n3. Cleaning up old test directories...")
        
        old_test_location = self.project_root / 'src/tests'
        if old_test_location.exists():
            # Move any remaining files to new location
            for file in old_test_location.glob('*.py'):
                # Determine destination based on file name
                if 'integration' in file.name or 'ibkr' in file.name or 'mock' in file.name:
                    dest = self.project_root / 'tests/integration' / file.name
                else:
                    dest = self.project_root / 'tests/unit/core' / file.name
                
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(dest))
                print(f"  ✓ Moved {file.name} to {dest.parent.name}")
                self.fixes_made.append(f"Moved test: {file.name}")
            
            # Remove if empty
            if not any(old_test_location.iterdir()):
                shutil.rmtree(old_test_location)
                print("  ✓ Removed empty src/tests directory")
    
    def update_main_imports(self):
        """Ensure main.py has correct imports"""
        print("\n4. Verifying main.py imports...")
        
        main_py = self.project_root / 'main.py'
        if main_py.exists():
            with open(main_py, 'r') as f:
                content = f.read()
            
            # Key import mappings for main.py
            replacements = [
                ('from src.regime.detector import Khazad_DumRegimeDetector', 
                 'from src.core.market_analysis.regime_detector import RegimeDetector'),
                ('from src.data.database import Khazad_DumDatabase',
                 'from src.data_pipeline.storage.database_manager import DatabaseManager'),
                ('from src.data.fetcher import Khazad_DumDataFetcher',
                 'from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher'),
                ('from src.filtering.filter import Khazad_DumFilter',
                 'from src.core.stock_screening.stock_filter import StockFilter'),
                ('from src.batch.tradingagents_batch_processor import TradingAgentsBatchProcessor',
                 'from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor'),
                ('from src.portfolio.tracker import PositionTracker',
                 'from src.core.portfolio_management.position_tracker import PositionTracker'),
                ('from src.feedback.observer import PerformanceObserver',
                 'from src.core.portfolio_management.performance_observer import PerformanceObserver'),
                ('Khazad_DumRegimeDetector()', 'RegimeDetector()'),
                ('Khazad_DumDatabase()', 'DatabaseManager()'),
                ('Khazad_DumDataFetcher()', 'StockDataFetcher()'),
                ('Khazad_DumFilter(', 'StockFilter('),
                ('TradingAgentsBatchProcessor(', 'BatchProcessor('),
            ]
            
            changed = False
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    changed = True
            
            if changed:
                with open(main_py, 'w') as f:
                    f.write(content)
                print("  ✓ Updated main.py imports")
                self.fixes_made.append("Updated main.py")
            else:
                print("  ✓ main.py imports already correct")
    
    def create_missing_wrapper(self):
        """Create agent_wrapper.py if it doesn't exist"""
        print("\n5. Checking for agent_wrapper.py...")
        
        wrapper_path = self.project_root / 'src/trading_engines/tradingagents_integration/agent_wrapper.py'
        
        if not wrapper_path.exists():
            # Look for coordinator or other files that might have the wrapper functionality
            coordinator_path = self.project_root / 'src/trading_engines/tradingagents_integration/agent_coordinator.py'
            
            if coordinator_path.exists():
                # The coordinator might be the wrapper - create alias
                wrapper_content = '''"""
Agent Wrapper - Interface to TradingAgents
This module provides the main wrapper for TradingAgents integration
"""

# The wrapper functionality is in agent_coordinator for now
from .agent_coordinator import *

# Create alias for backward compatibility
AgentWrapper = Khazad_DumTradingAgentsCoordinator if 'Khazad_DumTradingAgentsCoordinator' in dir() else None
'''
                with open(wrapper_path, 'w') as f:
                    f.write(wrapper_content)
                
                print("  ✓ Created agent_wrapper.py as alias")
                self.fixes_made.append("Created agent_wrapper.py")
            else:
                print("  ⚠ Could not create agent_wrapper.py - coordinator not found")
    
    def run(self):
        """Run all fixes"""
        print("\n" + "="*60)
        print("FIXING KHAZAD_DUM REORGANIZATION ISSUES")
        print("="*60)
        
        self.find_missing_files()
        self.fix_verification_script()
        self.cleanup_empty_tests_dirs()
        self.update_main_imports()
        self.create_missing_wrapper()
        
        print("\n" + "="*60)
        print("FIX SUMMARY")
        print("="*60)
        
        if self.fixes_made:
            print(f"\n✅ Applied {len(self.fixes_made)} fixes:")
            for fix in self.fixes_made:
                print(f"  • {fix}")
        else:
            print("\n⚠ No fixes were needed or possible")
        
        print("\nNext steps:")
        print("1. Run the verification script again")
        print("2. Test main.py to ensure it works")
        print("3. Check if any manual fixes are needed")

if __name__ == "__main__":
    fixer = Khazad_DumReorgFixer()
    fixer.run()