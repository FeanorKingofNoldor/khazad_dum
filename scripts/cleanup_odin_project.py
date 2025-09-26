#!/usr/bin/env python3
"""
Clean up old directories after KHAZAD_DUM reorganization
Removes empty directories and old structure remnants
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class Khazad_DumCleanup:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.dirs_removed = []
        self.dirs_kept = []
        self.files_found = []
        
    def identify_old_structure_dirs(self):
        """Identify directories from the old structure that should be removed"""
        
        # Old structure directories that should no longer exist
        old_dirs = [
            "src/regime",           # → moved to src/core/market_analysis
            "src/filtering",        # → moved to src/core/stock_screening  
            "src/patterns",         # → moved to src/core/pattern_recognition
            "src/portfolio",        # → moved to src/core/portfolio_management
            "src/feedback",         # → moved to src/core/portfolio_management
            "src/data",            # → moved to src/data_pipeline/storage
            "src/tradingagents",   # → moved to src/trading_engines/tradingagents_integration
            "src/batch",           # → moved to src/trading_engines/tradingagents_integration
            "src/brokers",         # → moved to src/trading_engines/broker_connections
            "src/migrations",      # → moved to scripts/maintenance
            "src/tests",           # → moved to tests/
            "src/monitoring",      # Old, might not be used
            "src/scheduler",       # Old, might not be used
            "src/trading",         # Old, might not be used
        ]
        
        return [self.project_root / d for d in old_dirs]
    
    def check_directory(self, dir_path):
        """Check if a directory is empty or contains only __pycache__"""
        
        if not dir_path.exists():
            return "not_exists"
        
        if not dir_path.is_dir():
            return "not_dir"
        
        # Get all items in directory
        items = list(dir_path.iterdir())
        
        # Filter out __pycache__ and .pyc files
        real_items = [
            item for item in items 
            if item.name != "__pycache__" and not item.name.endswith(".pyc")
        ]
        
        if not real_items:
            return "empty"
        
        # Check if only has empty subdirectories
        only_empty_dirs = all(
            item.is_dir() and self.check_directory(item) == "empty" 
            for item in real_items
        )
        
        if only_empty_dirs:
            return "empty"
        
        return "has_content"
    
    def remove_pycache(self):
        """Remove all __pycache__ directories"""
        
        print("\n1. Removing __pycache__ directories...")
        
        pycache_dirs = list(self.project_root.rglob("__pycache__"))
        
        for pycache in pycache_dirs:
            try:
                shutil.rmtree(pycache)
                print(f"  ✓ Removed {pycache.relative_to(self.project_root)}")
            except Exception as e:
                print(f"  ✗ Could not remove {pycache}: {e}")
        
        print(f"  Total: Removed {len(pycache_dirs)} __pycache__ directories")
    
    def remove_old_directories(self):
        """Remove old structure directories if empty"""
        
        print("\n2. Checking old structure directories...")
        
        old_dirs = self.identify_old_structure_dirs()
        
        for dir_path in old_dirs:
            status = self.check_directory(dir_path)
            
            if status == "not_exists":
                print(f"  ⊘ Already gone: {dir_path.relative_to(self.project_root)}")
            
            elif status == "empty":
                try:
                    shutil.rmtree(dir_path)
                    self.dirs_removed.append(dir_path)
                    print(f"  ✓ Removed: {dir_path.relative_to(self.project_root)}")
                except Exception as e:
                    print(f"  ✗ Could not remove {dir_path}: {e}")
            
            elif status == "has_content":
                self.dirs_kept.append(dir_path)
                print(f"  ⚠ Has content, keeping: {dir_path.relative_to(self.project_root)}")
                
                # List what's in it
                items = [i for i in dir_path.iterdir() if i.name != "__pycache__"]
                for item in items[:5]:  # Show first 5 items
                    if item.is_file():
                        self.files_found.append(item)
                        print(f"     → Contains: {item.name}")
                    else:
                        print(f"     → Contains dir: {item.name}/")
    
    def find_all_empty_dirs(self):
        """Find and remove ALL empty directories in src/"""
        
        print("\n3. Finding all empty directories in src/...")
        
        src_dir = self.project_root / "src"
        
        if not src_dir.exists():
            print("  ✗ src/ directory not found")
            return
        
        # Repeatedly remove empty dirs until none left
        rounds = 0
        while rounds < 5:  # Max 5 rounds to prevent infinite loop
            empty_dirs = []
            
            for root, dirs, files in os.walk(src_dir, topdown=False):
                root_path = Path(root)
                
                # Skip if it's a __pycache__
                if "__pycache__" in str(root_path):
                    continue
                
                # Check if directory is empty
                real_files = [f for f in files if not f.endswith(".pyc")]
                real_dirs = [d for d in dirs if d != "__pycache__"]
                
                if not real_files and not real_dirs:
                    empty_dirs.append(root_path)
            
            if not empty_dirs:
                break
            
            # Remove empty directories
            for empty_dir in empty_dirs:
                if empty_dir != src_dir:  # Don't remove src itself
                    try:
                        empty_dir.rmdir()
                        print(f"  ✓ Removed empty: {empty_dir.relative_to(self.project_root)}")
                    except Exception:
                        pass  # Directory might have been removed already
            
            rounds += 1
    
    def remove_backup_dirs(self):
        """Optionally remove backup directories"""
        
        print("\n4. Checking for backup directories...")
        
        backup_dirs = list(self.project_root.glob("backup_*"))
        
        if backup_dirs:
            print(f"  Found {len(backup_dirs)} backup directories:")
            for backup in backup_dirs:
                size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file()) / (1024 * 1024)
                print(f"    • {backup.name} ({size:.1f} MB)")
            
            response = input("\n  Remove backup directories? (y/n): ")
            if response.lower() == 'y':
                for backup in backup_dirs:
                    try:
                        shutil.rmtree(backup)
                        print(f"    ✓ Removed {backup.name}")
                    except Exception as e:
                        print(f"    ✗ Could not remove {backup}: {e}")
        else:
            print("  No backup directories found")
    
    def cleanup_misc_files(self):
        """Clean up miscellaneous files"""
        
        print("\n5. Cleaning up miscellaneous files...")
        
        misc_files = [
            "migration_log.json",
            "test_tradingagents_import.py",
            "test_reorganization.py",
            ".DS_Store",
        ]
        
        for filename in misc_files:
            file_path = self.project_root / filename
            if file_path.exists():
                response = input(f"  Remove {filename}? (y/n): ")
                if response.lower() == 'y':
                    file_path.unlink()
                    print(f"    ✓ Removed {filename}")
    
    def run(self, interactive=True):
        """Run the cleanup process"""
        
        print("\n" + "="*60)
        print("KHAZAD_DUM PROJECT CLEANUP")
        print("="*60)
        
        # Remove __pycache__ directories
        self.remove_pycache()
        
        # Remove old structure directories
        self.remove_old_directories()
        
        # Find and remove all empty directories
        self.find_all_empty_dirs()
        
        # Optionally remove backups
        if interactive:
            self.remove_backup_dirs()
            self.cleanup_misc_files()
        
        # Summary
        print("\n" + "="*60)
        print("CLEANUP SUMMARY")
        print("="*60)
        
        if self.dirs_removed:
            print(f"\n✓ Removed {len(self.dirs_removed)} old directories")
        
        if self.dirs_kept:
            print(f"\n⚠ Kept {len(self.dirs_kept)} directories with content:")
            for dir_path in self.dirs_kept:
                print(f"  • {dir_path.relative_to(self.project_root)}")
            
            if self.files_found:
                print("\n  These files might need manual review:")
                for file_path in self.files_found[:10]:
                    print(f"    → {file_path.relative_to(self.project_root)}")
        
        print("\n✅ Cleanup complete!")
        print("\nYour project structure is now clean and organized.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up KHAZAD_DUM project after reorganization")
    parser.add_argument("--yes", action="store_true", help="Non-interactive mode, skip prompts")
    parser.add_argument("--keep-backups", action="store_true", help="Don't remove backup directories")
    args = parser.parse_args()
    
    cleaner = Khazad_DumCleanup()
    cleaner.run(interactive=not args.yes)