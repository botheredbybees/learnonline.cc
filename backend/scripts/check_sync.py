#!/usr/bin/env python3
"""
File Synchronization Checker

This script checks that all necessary files exist and are accessible
in the project structure.
"""
import os
import sys
import logging
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_file(file_path):
    """Check if a file exists and is accessible"""
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File not found: {file_path}")
        return False
    
    try:
        # Try to read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) == 0:
                logger.warning(f"File exists but is empty: {file_path}")
                return False
            return True
    except Exception as e:
        logger.error(f"Error accessing file {file_path}: {e}")
        return False

def check_structure():
    """Check the project structure and verify key files"""
    
    # Define key files to check
    key_files = [
        # Backend files
        "backend/main.py",
        "backend/routers/admin.py",
        "backend/routers/auth.py",
        "backend/routers/units.py",
        "backend/routers/users.py",
        "backend/models/user.py",
        "backend/auth/auth_handler.py",
        "backend/auth/auth_bearer.py",
        "backend/db/database.py",
        "backend/scripts/tga/tp_get.py",
        "backend/tests/test_tga_xml.py",
        # Frontend files
        "frontend/src/views/Admin.vue"
    ]
    
    # Results
    results = {
        "found": [],
        "not_found": [],
        "errors": []
    }
    
    # Check each file
    for file_path in key_files:
        full_path = os.path.join(ROOT_DIR, file_path)
        if check_file(full_path):
            results["found"].append(file_path)
        else:
            results["not_found"].append(file_path)
    
    # Print summary
    logger.info(f"Found {len(results['found'])} files")
    if results["not_found"]:
        logger.warning(f"Missing {len(results['not_found'])} files: {results['not_found']}")
    
    # No need to check for symlink as it has been removed
    
    return results

if __name__ == "__main__":
    logger.info("Checking file synchronization...")
    results = check_structure()
    
    # Save results to a file
    output_file = os.path.join(ROOT_DIR, "file_sync_check.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {output_file}")
    
    # Exit with error code if any files are missing
    if results["not_found"] or results["errors"]:
        sys.exit(1)
