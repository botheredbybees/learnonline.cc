#!/bin/bash
# Example usage of tga_utils.py for XML processing

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
UTILS_SCRIPT="$ROOT_DIR/backend/scripts/tga_utils.py"

# Make sure the script is executable
chmod +x "$UTILS_SCRIPT"

# Function to print section header
print_header() {
    echo
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo
}

# Function to pause for user input
pause() {
    echo
    read -p "Press Enter to continue..."
    echo
}

# Function to run a command and display it
run_command() {
    echo "$ $1"
    echo
    eval "$1"
}

# Print intro
clear
echo "TGA XML Processing Examples"
echo "=========================="
echo "This script demonstrates how to use the tga_utils.py tool"
echo "for processing XML files from Training.gov.au."
echo

# Check if the script exists
if [ ! -f "$UTILS_SCRIPT" ]; then
    echo "Error: Could not find tga_utils.py at $UTILS_SCRIPT"
    exit 1
fi

# Show usage information
print_header "1. Show usage information"
run_command "python $UTILS_SCRIPT --help"
pause

# Parse a specific unit
print_header "2. Parse a specific unit XML file"
run_command "python $UTILS_SCRIPT parse --unit PUAAMS101"
pause

# Parse all XML files
print_header "3. Parse all XML files"
run_command "python $UTILS_SCRIPT parse --all --output $ROOT_DIR/output"
pause

# Store unit in database
print_header "4. Store unit elements in database"
echo "This requires database connection. Uncomment the next line to run it:"
echo "# python $UTILS_SCRIPT store --unit PUAAMS101 --create-unit"
pause

# Process all local XML files
print_header "5. Process all local XML files"
echo "This imports all XML files into the database. Uncomment the next line to run it:"
echo "# python $UTILS_SCRIPT process-local"
pause

# Finished
print_header "Tutorial Complete"
echo "You have completed the TGA XML processing tutorial."
echo "You can use these commands in your own scripts or run them directly."
echo
echo "For more information, see the documentation at:"
echo "$ROOT_DIR/docs/technical/tga_integration.md"
echo
