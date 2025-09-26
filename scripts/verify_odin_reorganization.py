#!/usr/bin/env python3
"""
KHAZAD_DUM Reorganization Verification Script
Verifies the project structure after reorganization and checks for issues
"""

import os
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ReorganizationVerifier:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def check_directory_structure(self) -> bool:
        """Verify the new directory structure exists"""
        print("\n1. Checking directory structure...")
        
        required_dirs = [
            "src/core/market_analysis",
            "src/core/stock_screening",
            "src/core/pattern_recognition",
            "src/core/portfolio_management",
            "src/data_pipeline/market_data",
            "src/data_pipeline/storage",
            "src/trading_engines/tradingagents_integration",
            "src/trading_engines/broker_connections/interfaces",
            "config/settings",
            "scripts/maintenance",
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.successes.append(f"✓ Directory exists: {dir_path}")
            else:
                self.issues.append(f"✗ Missing directory: {dir_path}")
                all_exist = False
                
        return all_exist
    
    def check_critical_files(self) -> bool:
        """Verify critical files are in their new locations"""
        print("\n2. Checking critical files...")
        
        critical_files = [
            ("src/core/market_analysis/regime_detector.py", "RegimeDetector"),
            ("src/core/stock_screening/stock_filter.py", "StockFilter"),
            ("src/core/pattern_recognition/pattern_classifier.py", "PatternClassifier"),
            ("src/data_pipeline/storage/database_manager.py", "DatabaseManager"),
            ("src/trading_engines/tradingagents_integration/agent_wrapper.py", "AgentWrapper"),
            ("config/settings/base_config.py", None),
            ("main.py", None),
        ]
        
        all_exist = True
        for file_path, expected_class in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.successes.append(f"✓ File exists: {file_path}")
                
                # Check if expected class is defined
                if expected_class:
                    try:
                        with open(full_path, 'r') as f:
                            content = f.read()
                        if f"class {expected_class}" in content:
                            self.successes.append(f"  ✓ Class {expected_class} found")
                        else:
                            self.warnings.append(f"  ⚠ Class {expected_class} not found in {file_path}")
                    except Exception as e:
                        self.warnings.append(f"  ⚠ Could not parse {file_path}: {e}")
            else:
                self.issues.append(f"✗ Missing file: {file_path}")
                all_exist = False
                
        return all_exist
    
    def check_imports(self) -> bool:
        """Check Python files for import errors"""
        print("\n3. Checking Python imports...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        # Skip vendor and backup directories
        python_files = [
            f for f in python_files 
            if 'tradingagents_lib' not in str(f) 
            and 'backup_' not in str(f)
            and '__pycache__' not in str(f)
        ]
        
        import_issues = []
        files_checked = 0
        
        for file_path in python_files[:20]:  # Check first 20 files
            files_checked += 1
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Parse the Python file
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    import_issues.append((file_path, f"Syntax error: {e}"))
                    
                # Check for old import patterns
                old_patterns = [
                    'src.brokers.base',
                ]
                
                for pattern in old_patterns:
                    if pattern in content:
                        import_issues.append((file_path, f"Found old import: {pattern}"))
                        
            except Exception as e:
                self.warnings.append(f"Could not check {file_path}: {e}")
        
        print(f"  Checked {files_checked} files")
        
        if import_issues:
            for file_path, issue in import_issues[:5]:  # Show first 5 issues
                self.issues.append(f"  ✗ {file_path.relative_to(self.project_root)}: {issue}")
            return False
        else:
            self.successes.append(f"  ✓ No import issues found in checked files")
            return True
    
    def check_tradingagents_lib(self) -> bool:
        """Verify tradingagents_lib is still at root level"""
        print("\n4. Checking tradingagents_lib...")
        
        lib_path = self.project_root / 'tradingagents_lib'
        if lib_path.exists() and lib_path.is_dir():
            self.successes.append("✓ tradingagents_lib exists at root level")
            
            # Check for key files
            key_files = [
                'tradingagents_lib/tradingagents/graph/trading_graph.py',
                'tradingagents_lib/tradingagents/agents/__init__.py',
            ]
            
            for file_path in key_files:
                if (self.project_root / file_path).exists():
                    self.successes.append(f"  ✓ Found: {file_path}")
                else:
                    self.warnings.append(f"  ⚠ Missing: {file_path}")
                    
            return True
        else:
            self.issues.append("✗ tradingagents_lib not found at root level")
            return False
    
    def check_backup(self) -> bool:
        """Check if backup exists"""
        print("\n5. Checking for backup...")
        
        backup_dirs = list(self.project_root.glob("backup_*"))
        
        if backup_dirs:
            latest_backup = sorted(backup_dirs)[-1]
            self.successes.append(f"✓ Backup found: {latest_backup}")
            return True
        else:
            self.warnings.append("⚠ No backup directory found")
            return False
    
    def check_migration_log(self) -> bool:
        """Check if migration log exists"""
        print("\n6. Checking migration log...")
        
        log_file = self.project_root / 'migration_log.json'
        if log_file.exists():
            self.successes.append("✓ Migration log exists")
            
            # Try to parse it
            try:
                import json
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                    
                moves = log_data.get('moves', [])
                successful = len([m for m in moves if m['status'] == 'success'])
                failed = len([m for m in moves if m['status'] == 'failed'])
                
                self.successes.append(f"  ✓ {successful} successful moves")
                if failed > 0:
                    self.warnings.append(f"  ⚠ {failed} failed moves")
                    
                return True
            except Exception as e:
                self.warnings.append(f"  ⚠ Could not parse migration log: {e}")
                return False
        else:
            self.warnings.append("⚠ Migration log not found")
            return False
    
    def run(self) -> bool:
        """Run all verification checks"""
        print("\n" + "="*60)
        print("KHAZAD_DUM REORGANIZATION VERIFICATION")
        print("="*60)
        
        # Run checks
        checks = [
            self.check_directory_structure(),
            self.check_critical_files(),
            self.check_imports(),
            self.check_tradingagents_lib(),
            self.check_backup(),
            self.check_migration_log(),
        ]
        
        # Print results
        print("\n" + "="*60)
        print("VERIFICATION RESULTS")
        print("="*60)
        
        if self.successes:
            print("\n✅ SUCCESSES:")
            for success in self.successes[:15]:  # Show first 15
                print(f"  {success}")
            if len(self.successes) > 15:
                print(f"  ... and {len(self.successes) - 15} more")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print("\n❌ ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
        
        # Overall result
        print("\n" + "="*60)
        if all(checks) and not self.issues:
            print("✅ VERIFICATION PASSED - Reorganization successful!")
            return True
        elif self.issues:
            print("❌ VERIFICATION FAILED - Issues found that need fixing")
            print("\nTo fix:")
            print("1. Review the issues listed above")
            print("2. Check the migration_log.json for details")
            print("3. If needed, restore from backup and try again")
            return False
        else:
            print("⚠️ VERIFICATION PASSED WITH WARNINGS")
            print("The reorganization succeeded but there are some warnings to review")
            return True


if __name__ == "__main__":
    verifier = ReorganizationVerifier()
    success = verifier.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)