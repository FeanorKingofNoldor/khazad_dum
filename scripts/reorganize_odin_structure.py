#!/usr/bin/env python3
"""
KHAZAD_DUM Project Structure Reorganization Script
This script safely reorganizes the project structure to improve clarity and maintainability.
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class Khazad_DumReorganizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.moves_log = []
        
    def create_backup(self):
        """Create a backup of the current structure"""
        print(f"Creating backup at {self.backup_dir}...")
        
        # Files to backup (excluding tradingagents_lib and large files)
        to_backup = [
            "src", "config", "tests", "scripts", "main.py",
            "requirements.txt", "requirements_ibkr.txt"
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for item in to_backup:
            if (self.project_root / item).exists():
                if (self.project_root / item).is_dir():
                    shutil.copytree(
                        self.project_root / item, 
                        self.backup_dir / item,
                        dirs_exist_ok=True
                    )
                else:
                    shutil.copy2(self.project_root / item, self.backup_dir / item)
        
        print(f"✓ Backup created at {self.backup_dir}")
        
    def create_new_structure(self):
        """Create the new directory structure"""
        print("\nCreating new directory structure...")
        
        new_dirs = [
            # Core directories
            "src/core/market_analysis",
            "src/core/stock_screening", 
            "src/core/pattern_recognition",
            "src/core/portfolio_management",
            
            # Data pipeline
            "src/data_pipeline/market_data",
            "src/data_pipeline/storage",
            "src/data_pipeline/external_apis",
            
            # Trading engines
            "src/trading_engines/tradingagents_integration",
            "src/trading_engines/broker_connections/interfaces",
            "src/trading_engines/broker_connections/implementations",
            
            # Integrations
            "src/integrations",
            
            # Config
            "config/settings",
            "config/environments",
            
            # Scripts
            "scripts/daily_operations",
            "scripts/maintenance", 
            "scripts/setup",
            
            # Tests
            "tests/unit/core",
            "tests/unit/data_pipeline",
            "tests/integration",
            "tests/fixtures",
            
            # Docs
            "docs/setup",
            "docs/architecture",
            "docs/api",
            
            # Data directories
            "data/databases",
            "data/cache",
            "data/results",
            
            # Logs
            "logs",
        ]
        
        for dir_path in new_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
            
        print(f"✓ Created {len(new_dirs)} directories")
    
    def move_files(self):
        """Move and rename files to new locations"""
        print("\nReorganizing files...")
        
        # Define file moves (old_path -> new_path)
        file_moves = {
            # Core - Market Analysis
            "src/regime/detector.py": "src/core/market_analysis/regime_detector.py",
            "src/regime/cnn_scraper.py": "src/core/market_analysis/cnn_feed_parser.py",
            
            # Core - Stock Screening
            "src/filtering/filter.py": "src/core/stock_screening/stock_filter.py",
            
            # Core - Pattern Recognition
            "src/patterns/classifier.py": "src/core/pattern_recognition/pattern_classifier.py",
            "src/patterns/tracker.py": "src/core/pattern_recognition/pattern_tracker.py",
            "src/patterns/database.py": "src/core/pattern_recognition/pattern_database.py",
            "src/patterns/memory_injector.py": "src/core/pattern_recognition/memory_injector.py",
            "src/patterns/memory_bridge.py": "src/core/pattern_recognition/memory_bridge.py",
            "src/patterns/__init__.py": "src/core/pattern_recognition/__init__.py",
            
            # Core - Portfolio Management
            "src/portfolio/constructor.py": "src/core/portfolio_management/portfolio_constructor.py",
            "src/portfolio/tracker.py": "src/core/portfolio_management/position_tracker.py",
            "src/feedback/observer.py": "src/core/portfolio_management/performance_observer.py",
            
            # Data Pipeline - Market Data
            "src/data/fetcher.py": "src/data_pipeline/market_data/stock_data_fetcher.py",
            
            # Data Pipeline - Storage
            "src/data/database.py": "src/data_pipeline/storage/database_manager.py",
            "src/data/schema_updates.sql": "src/data_pipeline/storage/schema_migrations.sql",
            
            # Trading Engines - TradingAgents Integration
            "src/tradingagents/wrapper.py": "src/trading_engines/tradingagents_integration/agent_wrapper.py",
            "src/tradingagents/coordinator.py": "src/trading_engines/tradingagents_integration/agent_coordinator.py",
            "src/tradingagents/portfolio_context.py": "src/trading_engines/tradingagents_integration/portfolio_context.py",
            "src/batch/tradingagents_batch_processor.py": "src/trading_engines/tradingagents_integration/batch_processor.py",
            
            # Trading Engines - Broker Connections
            "src/brokers/base/broker_interface.py": "src/trading_engines/broker_connections/interfaces/broker_interface.py",
            "src/brokers/base/mock_broker.py": "src/trading_engines/broker_connections/interfaces/mock_broker.py",
            "src/brokers/ibkr_connector.py": "src/trading_engines/broker_connections/implementations/ibkr_connector.py",
            "src/brokers/ibkr_order_executor.py": "src/trading_engines/broker_connections/implementations/ibkr_order_executor.py",
            "src/brokers/__init__.py": "src/trading_engines/broker_connections/__init__.py",
            
            # Integrations
            "src/integrations/pattern_wrapper.py": "src/integrations/pattern_enhancement.py",
            
            # Config
            "config/settings.py": "config/settings/base_config.py",
            
            # Scripts - Maintenance
            "src/migrations/apply_migration.py": "scripts/maintenance/apply_db_migration.py",
            "scripts/run_weekly_learning.py": "scripts/maintenance/run_weekly_learning.py",
            "scripts/pattern_dashboard.py": "scripts/maintenance/pattern_dashboard.py",
            
            # Tests - Unit tests
            "tests/test_fetcher.py": "tests/unit/data_pipeline/test_fetcher.py",
            
            # Tests - Integration tests  
            "tests/test_tradingagents.py": "tests/integration/test_tradingagents_integration.py",
            "tests/test_mock_broker_complete.py": "tests/integration/test_mock_broker.py",
            "tests/test_pattern_integration.py": "tests/integration/test_pattern_system.py",
            "tests/test_khazad_dum_mock_integration.py": "tests/integration/test_khazad_dum_mock_integration.py",
            "tests/test_portfolio_constructor.py": "tests/unit/core/test_portfolio_constructor.py",
            "tests/test_memory_matching.py": "tests/unit/core/test_pattern_memory.py",
            
            # Documentation
            "IBKR_INTEGRATION_GUIDE.md": "docs/setup/ibkr_setup_guide.md",
            "tradingagents_enhanced_implementation_plan_v2.md": "docs/architecture/implementation_plan.md",
            "key_changes_and_decisions_summary.md": "docs/architecture/key_decisions.md",
        }
        
        successful_moves = 0
        failed_moves = []
        
        for old_path, new_path in file_moves.items():
            old_file = self.project_root / old_path
            new_file = self.project_root / new_path
            
            if old_file.exists():
                try:
                    # Create parent directory if needed
                    new_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    shutil.move(str(old_file), str(new_file))
                    
                    self.moves_log.append({
                        "old": str(old_path),
                        "new": str(new_path),
                        "status": "success"
                    })
                    successful_moves += 1
                    print(f"  ✓ {old_path} -> {new_path}")
                    
                except Exception as e:
                    failed_moves.append((old_path, str(e)))
                    self.moves_log.append({
                        "old": str(old_path),
                        "new": str(new_path),
                        "status": "failed",
                        "error": str(e)
                    })
                    print(f"  ✗ Failed to move {old_path}: {e}")
            else:
                print(f"  ⚠ Source not found: {old_path}")
                self.moves_log.append({
                    "old": str(old_path),
                    "new": str(new_path),
                    "status": "not_found"
                })
        
        print(f"\n✓ Successfully moved {successful_moves} files")
        if failed_moves:
            print(f"✗ Failed to move {len(failed_moves)} files")
            
    def create_init_files(self):
        """Create __init__.py files for new packages"""
        print("\nCreating __init__.py files...")
        
        init_locations = [
            "src/core",
            "src/core/market_analysis",
            "src/core/stock_screening",
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
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
        ]
        
        for location in init_locations:
            init_file = self.project_root / location / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Package initialization"""\n')
                
        print(f"✓ Created {len(init_locations)} __init__.py files")
    
    def cleanup_empty_dirs(self):
        """Remove empty directories from old structure"""
        print("\nCleaning up empty directories...")
        
        dirs_to_check = [
            "src/regime",
            "src/filtering", 
            "src/patterns",
            "src/portfolio",
            "src/feedback",
            "src/data",
            "src/tradingagents",
            "src/batch",
            "src/brokers/base",
            "src/brokers",
            "src/migrations",
        ]
        
        removed_count = 0
        for dir_path in dirs_to_check:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                # Check if directory is empty
                if not any(full_path.iterdir()):
                    shutil.rmtree(full_path)
                    removed_count += 1
                    print(f"  ✓ Removed empty directory: {dir_path}")
                    
        print(f"✓ Removed {removed_count} empty directories")
    
    def save_migration_log(self):
        """Save a log of all moves for reference"""
        log_file = self.project_root / "migration_log.json"
        
        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "backup_location": str(self.backup_dir),
                "moves": self.moves_log
            }, f, indent=2)
            
        print(f"\n✓ Migration log saved to {log_file}")
    
    def print_tree(self):
        """Print the new structure tree"""
        print("\n" + "="*60)
        print("NEW PROJECT STRUCTURE:")
        print("="*60)
        
        def print_dir_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
                
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(prefix + current_prefix + item.name)
                
                if item.is_dir() and item.name not in ['.git', '__pycache__', 'backup_*', 'tradingagents_lib']:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    print_dir_tree(item, next_prefix, max_depth, current_depth + 1)
        
        print("\nkhazad_dum-trading-system/")
        print_dir_tree(self.project_root)
    
    def run(self):
        """Execute the complete reorganization"""
        print("\n" + "="*60)
        print("KHAZAD_DUM PROJECT STRUCTURE REORGANIZATION")
        print("="*60)
        
        # Step 1: Create backup
        self.create_backup()
        
        # Step 2: Create new directory structure
        self.create_new_structure()
        
        # Step 3: Move files to new locations
        self.move_files()
        
        # Step 4: Create __init__.py files
        self.create_init_files()
        
        # Step 5: Clean up empty directories
        self.cleanup_empty_dirs()
        
        # Step 6: Save migration log
        self.save_migration_log()
        
        # Step 7: Display new structure
        self.print_tree()
        
        print("\n" + "="*60)
        print("✅ REORGANIZATION COMPLETE!")
        print("="*60)
        print(f"\n📁 Backup saved at: {self.backup_dir}")
        print("📝 Migration log saved at: migration_log.json")
        print("\nNext steps:")
        print("1. Review the new structure")
        print("2. Run the import update script (coming next)")
        print("3. Test the reorganized project")
        print("\nTo restore from backup if needed:")
        print(f"  cp -r {self.backup_dir}/* .")
        

if __name__ == "__main__":
    import sys
    
    # Safety check
    print("\n⚠️  WARNING: This script will reorganize your entire project structure!")
    print("A backup will be created, but please ensure you have committed any changes to git.")
    
    response = input("\nDo you want to proceed? (yes/no): ")
    
    if response.lower() == 'yes':
        reorganizer = Khazad_DumReorganizer()
        reorganizer.run()
    else:
        print("Reorganization cancelled.")
        sys.exit(0)