#!/usr/bin/env python3
import os
import re
from pathlib import Path
import argparse

def remove_links_from_file(file_path):
    """Remove all Markdown links from a file, keeping only the link text."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace [text](url) with text
        link_pattern = re.compile(r'\[(.*?)\]\([^)]*\)')
        modified_content = link_pattern.sub(r'\1', content)
        
        # Only write back if changes were made
        if content != modified_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def find_and_process_md_files(directory):
    """Find all .md files in the directory and its subdirectories and remove links."""
    directory_path = Path(directory)
    md_files = list(directory_path.glob('**/*.md'))
    
    total_files = len(md_files)
    modified_files = 0
    
    print(f"🔍 Found {total_files} Markdown files to process")
    
    for file_path in md_files:
        if remove_links_from_file(file_path):
            modified_files += 1
            print(f"✅ Removed links from {file_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files modified: {modified_files}")

def main():
    parser = argparse.ArgumentParser(description='Remove Markdown links from files, keeping only the link text.')
    parser.add_argument('directory', nargs='?', default='docs', 
                        help='Directory to search for Markdown files (default: docs)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN: No files will be modified")
    
    find_and_process_md_files(args.directory)

if __name__ == "__main__":
    main()