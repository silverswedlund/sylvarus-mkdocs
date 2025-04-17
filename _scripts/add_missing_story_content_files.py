#!/usr/bin/env python3
"""
Script to create missing content files for stories.
For each .md file in the stories directory, this script creates a corresponding .md_content file
if it doesn't already exist (ignoring disambiguation files).
"""

import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def create_missing_content_files():
    """Create missing .md_content files for each story .md file."""
    stories_dir = Path('docs/documents/stories')
    
    # Check if the stories directory exists
    if not stories_dir.exists():
        logging.error(f"Stories directory not found: {stories_dir}")
        return
    
    # Count for summary
    created_count = 0
    skipped_count = 0
    
    # Find all .md files in the stories directory
    for md_file in stories_dir.glob('*.md'):
        # Skip disambiguation files
        if 'disambiguation' in md_file.name:
            logging.debug(f"Skipping disambiguation file: {md_file}")
            skipped_count += 1
            continue
        
        # Determine the content file name (replace .md with .md_content)
        content_file_name = md_file.stem + '.md_content'
        content_file_path = md_file.parent / content_file_name
        
        # Create the content file if it doesn't exist
        if not content_file_path.exists():
            try:
                with open(content_file_path, 'w', encoding='utf-8') as f:
                    pass  # Create an empty file
                logging.info(f"Created missing content file: {content_file_path}")
                created_count += 1
            except Exception as e:
                logging.error(f"Error creating content file {content_file_path}: {e}")
        else:
            logging.debug(f"Content file already exists: {content_file_path}")
            skipped_count += 1
    
    # Print summary
    logging.info(f"Summary: Created {created_count} missing content files, skipped {skipped_count} files.")

if __name__ == "__main__":
    create_missing_content_files()
