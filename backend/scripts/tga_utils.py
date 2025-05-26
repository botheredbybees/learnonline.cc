#!/usr/bin/env python3
"""
Utility script for working with TGA XML files

This script provides commands to:
1. Parse XML files
2. Test XML parsing and database storage
3. Process local XML files
"""
import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
TESTS_DIR = os.path.join(BACKEND_DIR, 'tests')
XML_DIR = os.path.join(ROOT_DIR, 'tgaWebServiceKit-2021-12-01', 'xml')

def run_command(cmd, description):
    """Run a command and return its result"""
    logger.info(f"{description}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Command failed with code {result.returncode}")
        logger.error(f"Error: {result.stderr}")
        return None
    
    return result.stdout

def parse_args():
    parser = argparse.ArgumentParser(description='TGA XML Utilities')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Parse XML files
    parse_parser = subparsers.add_parser('parse', help='Parse XML files')
    parse_parser.add_argument('--all', action='store_true', help='Parse all XML files')
    parse_parser.add_argument('--unit', help='Parse a specific unit code')
    parse_parser.add_argument('--xml-dir', default=XML_DIR, help='Directory containing XML files')
    parse_parser.add_argument('--output', help='Output directory for JSON files')
    
    # Store in database
    store_parser = subparsers.add_parser('store', help='Store elements in database')
    store_parser.add_argument('--unit', required=True, help='Unit code to store')
    store_parser.add_argument('--xml-dir', default=XML_DIR, help='Directory containing XML files')
    store_parser.add_argument('--create-unit', action='store_true', help='Create unit if it doesn\'t exist')
    
    # Process local XML files
    process_parser = subparsers.add_parser('process-local', help='Process local XML files')
    process_parser.add_argument('--tp-code', help='Training package code to filter by')
    process_parser.add_argument('--xml-dir', default=XML_DIR, help='Directory containing XML files')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Verify that required directories exist
    if not os.path.exists(BACKEND_DIR):
        logger.error(f"Backend directory not found: {BACKEND_DIR}")
        return 1
    
    if not os.path.exists(args.xml_dir):
        logger.error(f"XML directory not found: {args.xml_dir}")
        return 1
    
    # Execute the appropriate command
    if args.command == 'parse':
        test_script = os.path.join(TESTS_DIR, 'test_tga_xml.py')
        
        if args.all:
            # Parse all XML files
            cmd = [sys.executable, test_script, '--parse-all']
            if args.output:
                cmd.extend(['--output-dir', args.output])
            if args.xml_dir:
                cmd.extend(['--xml-dir', args.xml_dir])
                
            output = run_command(cmd, "Parsing all XML files")
            if output:
                print(output)
                
        elif args.unit:
            # Parse specific unit
            cmd = [sys.executable, test_script, '--unit', args.unit]
            if args.xml_dir:
                cmd.extend(['--xml-dir', args.xml_dir])
                
            output = run_command(cmd, f"Parsing unit {args.unit}")
            if output:
                print(output)
                
        else:
            logger.error("Must specify either --all or --unit")
            return 1
            
    elif args.command == 'store':
        test_script = os.path.join(TESTS_DIR, 'test_tga_xml.py')
        
        # Store in database
        cmd = [sys.executable, test_script, '--unit', args.unit, '--store']
        if args.create_unit:
            cmd.append('--create-unit')
        if args.xml_dir:
            cmd.extend(['--xml-dir', args.xml_dir])
            
        output = run_command(cmd, f"Storing unit {args.unit} in database")
        if output:
            print(output)
            
    elif args.command == 'process-local':
        script_path = os.path.join(BACKEND_DIR, 'scripts', 'tga', 'tp_get.py')
        
        # Process local XML files
        cmd = [sys.executable, script_path, '--process-local']
        if args.tp_code:
            # Note: We need to add support for this in tp_get.py
            cmd.extend(['--tp-code', args.tp_code])
        if args.xml_dir:
            cmd.extend(['--xml-dir', args.xml_dir])
            
        output = run_command(cmd, "Processing local XML files")
        if output:
            print(output)
            
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
