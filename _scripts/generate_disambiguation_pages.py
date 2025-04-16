#!/usr/bin/env python3
"""
Script to generate disambiguation pages for non-leaf directories under docs.
For each directory that has subdirectories but no disambiguation page,
this script creates a <directory_name>_disambiguation.md file.
"""

import os
import re
from pathlib import Path

# Base directory for docs
DOCS_DIR = Path("docs")

def is_leaf_directory(directory):
    """Check if a directory is a leaf directory (has no subdirectories)."""
    for item in os.listdir(directory):
        item_path = directory / item
        if item_path.is_dir():
            return False
    return True

def has_disambiguation_page(directory):
    """Check if a directory already has a disambiguation page."""
    dir_name = directory.name
    disambiguation_filename = f"{dir_name}_disambiguation.md"
    return (directory / disambiguation_filename).exists()

def create_disambiguation_page(directory):
    """Create a disambiguation page for the given directory."""
    dir_name = directory.name
    disambiguation_filename = f"{dir_name}_disambiguation.md"
    file_path = directory / disambiguation_filename
    
    # Get a list of subdirectories
    subdirectories = [d for d in directory.iterdir() if d.is_dir()]
    
    # Format the directory name for display (replace underscores with spaces and capitalize)
    display_name = dir_name.replace('_', ' ').title()
    
    # Create content for the disambiguation page
    content = f"# {display_name} Disambiguation\n\n"
    content += f"This page lists all subcategories in the {display_name} section.\n\n"
    
    # Add links to subdirectories and their markdown files
    for subdir in sorted(subdirectories):
        subdir_name = subdir.name
        display_subdir_name = subdir_name.replace('_', ' ').title()
        
        # Check for markdown files in the subdirectory (excluding disambiguation pages)
        md_files = [f for f in subdir.glob("*.md") if not f.name.endswith("_disambiguation.md")]
        
        if md_files:
            content += f"## {display_subdir_name}\n\n"
            
            # Add links to each markdown file
            for md_file in sorted(md_files):
                # Get the file name without extension for display
                file_display_name = md_file.stem.replace('_', ' ').title()
                
                # Create relative path to the file
                rel_path = f"{subdir_name}/{md_file.name}"
                
                content += f"- [{file_display_name}]({rel_path})\n"
            
            content += "\n"
        else:
            # If no markdown files, just list the directory
            content += f"- {display_subdir_name}\n"
    
    # Write the content to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Created disambiguation page: {file_path}")

def process_directory(directory):
    """Process a directory to check if it needs a disambiguation page."""
    # Skip hidden directories
    if directory.name.startswith('.'):
        return
    
    # If it's not a leaf directory and doesn't have a disambiguation page, create one
    if not is_leaf_directory(directory) and not has_disambiguation_page(directory):
        create_disambiguation_page(directory)
    
    # Recursively process subdirectories
    for item in directory.iterdir():
        if item.is_dir():
            process_directory(item)

def main():
    """Main function to process the docs directory."""
    if not DOCS_DIR.exists():
        print(f"Error: {DOCS_DIR} directory not found.")
        return
    
    print(f"Processing {DOCS_DIR} for missing disambiguation pages...")
    process_directory(DOCS_DIR)
    print("Disambiguation page generation complete.")

if __name__ == "__main__":
    main()
