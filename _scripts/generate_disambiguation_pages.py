#!/usr/bin/env python3
"""
Script to generate disambiguation pages for directories under docs.
For each directory, this script:
1. Creates a <directory_name>_disambiguation.md file using the template
2. Creates an empty <directory_name>_disambiguation.md_content file if it doesn't exist
3. Generates a <directory_name>_table.md_insert file with a table of items based on JSON data

The script reads all JSON files under _json, extracts item information and base paths,
and uses this to build tables for each directory in the docs structure.
"""

import os
import re
import json
import argparse
from pathlib import Path
import logging
from collections import defaultdict
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Base directory for docs
DOCS_DIR = Path("docs")
JSON_DIR = Path("_json")
TEMPLATE_PATH = Path("_templates/disambiguation.md_template")

def get_directory_title(directory):
    """Get a formatted title for a directory."""
    dir_name = directory.name
    return dir_name.replace('_', ' ').title()

def to_pascal_case(text):
    """Convert a string to PascalCase."""
    # First replace underscores with spaces and capitalize each word
    words = text.replace('_', ' ').title().split()
    # Then join the words without spaces
    return ''.join(words)

def load_json_data(json_path):
    """Load data from a JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {json_path}: {e}")
        return None

def find_all_json_files():
    """Find all JSON files under _json directory."""
    json_files = []
    for path in JSON_DIR.glob('**/*.json'):
        if path.is_file():
            json_files.append(path)
    return json_files

def get_display_name(item_data, item_key):
    """Extract the display name from item data (first auto_link_string or name)."""
    if "auto_link_strings" in item_data and item_data["auto_link_strings"]:
        return item_data["auto_link_strings"][0]
    elif "name" in item_data:
        return item_data["name"]
    return item_key

def build_directory_structure():
    """
    Build a mapping of directories to their items based on JSON data.
    
    Returns:
        dict: A dictionary where keys are Path objects representing directories,
              and values are dictionaries mapping item keys to display names.
    """
    # Structure: {directory_path: {item_key: display_name}}
    directory_items = defaultdict(dict)
    
    # Find all JSON files
    json_files = find_all_json_files()
    logging.info(f"Found {len(json_files)} JSON files to process")
    
    # Process each JSON file
    for json_path in json_files:
        data = load_json_data(json_path)
        if not data or "items" not in data:
            continue
        
        # Get the base path from the config
        base_path = data.get("config", {}).get("base_path", "")
        if not base_path:
            # Skip if no base path is defined
            logging.warning(f"No base path defined in {json_path}, skipping")
            continue
        
        # Convert the base path to a Path object
        base_path = Path(base_path)
        
        # Process each item
        for item_key, item_data in data["items"].items():
            # Get the display name for this item
            display_name = get_display_name(item_data, item_key)
            
            # Add this item to the directory
            directory_items[base_path][item_key] = display_name
    
    return directory_items

def write_file(file_path, content, dry_run=False):
    """Write content to a file, creating parent directories if needed."""
    if dry_run:
        logging.info(f"Would write to {file_path}:\n{content}")
        return
    
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the content to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logging.info(f"Wrote {file_path}")

def create_disambiguation_page(directory, dry_run=False):
    """Create a disambiguation page for a directory using the template."""
    # Skip the root docs directory
    if directory == DOCS_DIR:
        return
    
    # Get the directory name and relative path
    dir_name = directory.name
    rel_path = directory.relative_to(DOCS_DIR)
    
    # Create the disambiguation page path
    disambig_page_path = directory / f"{dir_name}_disambiguation.md"
    
    # Check if the template exists
    if not TEMPLATE_PATH.exists():
        logging.error(f"Template not found: {TEMPLATE_PATH}")
        return
    
    # Read the template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Replace template variables
    content = template_content.replace("{{ name }}", dir_name)
    content = content.replace("{{ path }}", str(rel_path))
    content = content.replace("{{ pascal_case_name }}", to_pascal_case(dir_name))
    
    # Write the disambiguation page
    write_file(disambig_page_path, content, dry_run)

def create_empty_content_file(directory, filename, dry_run=False):
    """Create an empty content file if it doesn't exist."""
    file_path = directory / filename
    
    # Check if the file already exists
    if file_path.exists():
        logging.info(f"Content file already exists: {file_path}")
        return
    
    # Create an empty file
    write_file(file_path, "", dry_run)

def generate_leaf_table(directory, items, dry_run=False):
    """Generate a table for a leaf directory (no subdirectories)."""
    # Skip if no items
    if not items:
        logging.info(f"No items for {directory}, creating empty table")
        content = "No items found in this directory."
    else:
        # Create a single-column table
        content = "| Name |\n|------|\n"
        
        # Sort items by display name
        sorted_items = sorted(items.items(), key=lambda x: x[1].lower())
        
        # Add each item to the table
        for item_key, display_name in sorted_items:
            # Create a simple table row with just the display name (no link)
            content += f"| {display_name} |\n"
    
    # Write the table to the insert file
    table_insert_path = directory / f"{directory.name}_table.md_insert"
    write_file(table_insert_path, content, dry_run)

def get_subdirectories(all_directories, parent_directory):
    """Get all immediate subdirectories of a directory."""
    subdirectories = []
    for directory in all_directories:
        if directory.parent == parent_directory:
            subdirectories.append(directory)
    return subdirectories

def generate_directory_table(directory, subdirectory_items, dry_run=False):
    """Generate a table for a directory with subdirectories."""
    # Get all subdirectories
    subdirectories = sorted(subdirectory_items.keys(), key=lambda x: x.name.lower())
    
    if not subdirectories:
        logging.warning(f"No subdirectories found for {directory}, creating empty table")
        content = "No subdirectories found."
        table_insert_path = directory / f"{directory.name}_table.md_insert"
        write_file(table_insert_path, content, dry_run)
        return
    
    # Create the table header
    header = []
    for subdir in subdirectories:
        # Get a formatted title for the subdirectory
        title = get_directory_title(subdir)
        header.append(title)
    
    # Create the table header row
    content = "| " + " | ".join(header) + " |\n"
    
    # Create the separator row
    content += "| " + " | ".join(["---" for _ in subdirectories]) + " |\n"
    
    # Find the maximum number of items in any subdirectory
    max_items = max([len(subdirectory_items.get(subdir, {})) for subdir in subdirectories], default=0)
    
    # Create the table rows
    for i in range(max_items):
        row = []
        for subdir in subdirectories:
            items = subdirectory_items.get(subdir, {})
            sorted_items = sorted(items.items(), key=lambda x: x[1].lower())
            
            if i < len(sorted_items):
                item_key, display_name = sorted_items[i]
                row.append(display_name)
            else:
                row.append("")
        
        # Only add the row if it has at least one non-empty cell
        if any(cell != "" for cell in row):
            content += "| " + " | ".join(row) + " |\n"
    
    # Write the table to the insert file
    table_insert_path = directory / f"{directory.name}_table.md_insert"
    write_file(table_insert_path, content, dry_run)

def process_directories(directory_items, dry_run=False):
    """Process all directories and generate disambiguation pages and tables."""
    # Get all unique directories
    all_directories = set()
    for base_path in directory_items.keys():
        # Add the base path and all its parent directories
        current = base_path
        while current != DOCS_DIR and current.is_relative_to(DOCS_DIR):
            all_directories.add(current)
            current = current.parent
    
    # Process each directory (excluding the root docs directory)
    for directory in sorted(all_directories):
        if directory == DOCS_DIR:
            continue
            
        logging.info(f"Processing directory: {directory}")
        
        # Create the disambiguation page
        create_disambiguation_page(directory, dry_run)
        
        # Create the empty disambiguation content file if it doesn't exist
        create_empty_content_file(directory, f"{directory.name}_disambiguation.md_content", dry_run)
        
        # Check if this is a leaf directory or has subdirectories
        subdirectories = get_subdirectories(all_directories, directory)
        
        if subdirectories:
            # This directory has subdirectories - create a multi-column table
            subdirectory_items = {}
            for subdir in subdirectories:
                # Get items for this subdirectory
                if subdir in directory_items:
                    subdirectory_items[subdir] = directory_items[subdir]
                else:
                    subdirectory_items[subdir] = {}
            
            generate_directory_table(directory, subdirectory_items, dry_run)
        else:
            # This is a leaf directory - create a single-column table
            items = directory_items.get(directory, {})
            generate_leaf_table(directory, items, dry_run)

def main():
    """Main function to process directories and generate disambiguation pages."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate disambiguation pages for directories.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.dry_run:
        logging.info("DRY RUN: No files will be modified")
    
    # Check if template exists
    if not TEMPLATE_PATH.exists():
        logging.error(f"Template not found: {TEMPLATE_PATH}")
        return
    
    logging.info("Building directory structure from JSON files...")
    directory_items = build_directory_structure()
    logging.info(f"Found {len(directory_items)} directories with items")
    
    logging.info("Processing directories and generating disambiguation pages...")
    process_directories(directory_items, args.dry_run)
    
    logging.info("Disambiguation page generation complete.")

if __name__ == "__main__":
    main()
