#!/usr/bin/env python3
"""
Final consolidation of KHAZAD_DUM project structure
Moves remaining files from old directories to their proper new locations
"""

import shutil
from pathlib import Path
import os

class FinalConsolidation:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.moves = []
        
    def consolidate_old_directories(self):
        """Move files from old directories to new locations"""
        
        print("\n" + "="*60)
        print("FINAL KHAZAD_DUM STRUCTURE CONSOLIDATION")
        print("="*60)
        
        # Define what needs to be moved/consolidated
        consolidations = [
            # Old batch directory
            ("src/batch/overnight_processor.py", 
             "src/trading_engines/tradingagents_integration/overnight_processor.py",
             "Batch processor"),
            
            # Old brokers/ibkr directory
            ("src/brokers/ibkr/connection.py",
             "src/trading_engines/broker_connections/implementations/ibkr_connection.py",
             "IBKR connection"),
            ("src/brokers/ibkr/orders.py",
             "src/trading_engines/broker_connections/implementations/ibkr_orders.py",
             "IBKR orders"),
            ("src/brokers/ibkr/portfolio.py",
             "src/trading_engines/broker_connections/implementations/ibkr_portfolio.py",
             "IBKR portfolio"),
            ("src/brokers/ibkr/utils.py",
             "src/trading_engines/broker_connections/implementations/ibkr_utils.py",
             "IBKR utils"),
            
            # Old tradingagents directory (these might be duplicates or old versions)
            ("src/tradingagents/analyzer.py",
             "src/trading_engines/tradingagents_integration/analyzer.py",
             "TradingAgents analyzer"),
            ("src/tradingagents/client.py",
             "src/trading_engines/tradingagents_integration/client.py",
             "TradingAgents client"),
            ("src/tradingagents/context_provider.py",
             "src/trading_engines/tradingagents_integration/context_provider.py",
             "TradingAgents context provider"),
            
            # Old patterns directory
            ("src/patterns/analyzer.py",
             "src/core/pattern_recognition/analyzer.py",
             "Pattern analyzer"),
            
            # Old migrations directory
            ("src/migrations/001_add_pattern_tables.sql",
             "scripts/maintenance/migrations/001_add_pattern_tables.sql",
             "Pattern tables migration"),
            
            # Old monitoring directory
            ("src/monitoring/performance.py",
             "src/core/portfolio_management/performance_monitor.py",
             "Performance monitor"),
            
            # Old scheduler directory
            ("src/scheduler/jobs.py",
             "scripts/daily_operations/scheduled_jobs.py",
             "Scheduled jobs"),
            
            # Old trading directory
            ("src/trading/position_manager.py",
             "src/core/portfolio_management/position_manager.py",
             "Position manager"),
        ]
        
        print("\nMoving files to new locations:")
        
        for old_path, new_path, description in consolidations:
            old_file = self.project_root / old_path
            new_file = self.project_root / new_path
            
            if old_file.exists():
                # Create target directory if needed
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if target already exists
                if new_file.exists():
                    print(f"\n  ⚠ {description}:")
                    print(f"    Source: {old_path}")
                    print(f"    Target exists: {new_path}")
                    response = input("    Overwrite? (y/n/s=skip): ")
                    
                    if response.lower() == 's':
                        continue
                    elif response.lower() != 'y':
                        # Keep old file but rename it
                        backup_path = new_file.with_suffix('.backup' + new_file.suffix)
                        shutil.move(str(new_file), str(backup_path))
                        print(f"    Backed up existing to: {backup_path.name}")
                
                # Move the file
                shutil.move(str(old_file), str(new_file))
                self.moves.append((old_path, new_path))
                print(f"  ✓ Moved {description}")
                print(f"    From: {old_path}")
                print(f"    To:   {new_path}")
            else:
                print(f"  ⊘ {description} - file not found")
    
    def remove_empty_old_dirs(self):
        """Remove the now-empty old directories"""
        
        print("\nRemoving empty old directories:")
        
        old_dirs_to_remove = [
            "src/batch",
            "src/brokers/ibkr",
            "src/brokers/base",
            "src/brokers",
            "src/tradingagents",
            "src/patterns", 
            "src/migrations",
            "src/monitoring",
            "src/scheduler",
            "src/trading",
            "src/data",
            "src/feedback",
            "src/portfolio",
            "src/regime",
        ]
        
        removed = []
        
        for dir_path in old_dirs_to_remove:
            full_path = self.project_root / dir_path
            
            if full_path.exists() and full_path.is_dir():
                try:
                    # Check if truly empty (ignoring __pycache__ and __init__.py)
                    contents = list(full_path.iterdir())
                    real_contents = [
                        c for c in contents 
                        if c.name not in ['__pycache__', '__init__.py', '.DS_Store']
                        and not c.name.endswith('.pyc')
                    ]
                    
                    if not real_contents:
                        # Remove __init__.py first if it exists
                        init_file = full_path / "__init__.py"
                        if init_file.exists():
                            init_file.unlink()
                        
                        # Remove directory
                        shutil.rmtree(full_path)
                        removed.append(dir_path)
                        print(f"  ✓ Removed: {dir_path}")
                    else:
                        print(f"  ⚠ Still has content: {dir_path}")
                        for item in real_contents[:3]:
                            print(f"     → {item.name}")
                except Exception as e:
                    print(f"  ✗ Could not remove {dir_path}: {e}")
        
        return removed
    
    def update_imports_in_moved_files(self):
        """Update imports in the files we just moved"""
        
        print("\nUpdating imports in moved files:")
        
        # Files that were moved and need import updates
        for old_path, new_path in self.moves:
            file_path = self.project_root / new_path
            
            if file_path.exists() and file_path.suffix == '.py':
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Update relative imports based on new location
                if 'tradingagents_integration' in str(new_path):
                    # Fix imports for tradingagents_integration
                    content = content.replace('from src.tradingagents', 'from src.trading_engines.tradingagents_integration')
                    content = content.replace('from ..', 'from .')
                    
                if 'pattern_recognition' in str(new_path):
                    # Fix imports for pattern_recognition
                    content = content.replace('from src.patterns', 'from src.core.pattern_recognition')
                    
                if 'portfolio_management' in str(new_path):
                    # Fix imports for portfolio_management
                    content = content.replace('from src.trading', 'from src.core.portfolio_management')
                    content = content.replace('from src.monitoring', 'from src.core.portfolio_management')
                
                # Save if changed
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"  ✓ Updated imports in {new_path}")
    
    def create_summary_report(self):
        """Create a summary of the consolidation"""
        
        print("\n" + "="*60)
        print("CONSOLIDATION SUMMARY")
        print("="*60)
        
        if self.moves:
            print(f"\n✓ Moved {len(self.moves)} files:")
            for old, new in self.moves:
                print(f"  • {Path(old).name} → {Path(new).parent.name}/")
        
        print("\nYour new structure is now fully consolidated!")
        print("\nNext steps:")
        print("1. Update any remaining imports:")
        print("   python fix_all_script_paths.py")
        print("2. Run tests to verify everything works:")
        print("   python scripts/test_khazad_dum_imports_fixed.py")
        print("3. Commit the changes to git")
    
    def run(self):
        """Execute the consolidation"""
        
        # Move files
        self.consolidate_old_directories()
        
        # Update imports in moved files
        if self.moves:
            self.update_imports_in_moved_files()
        
        # Clean up empty directories
        self.remove_empty_old_dirs()
        
        # Show summary
        self.create_summary_report()


if __name__ == "__main__":
    print("This will consolidate remaining old directories into the new structure.")
    print("A backup was already created during the initial reorganization.")
    
    response = input("\nProceed with consolidation? (y/n): ")
    
    if response.lower() == 'y':
        consolidator = FinalConsolidation()
        consolidator.run()
    else:
        print("Consolidation cancelled.")