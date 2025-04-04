#!/usr/bin/env python3
import os
import re
from pathlib import Path
import argparse

def remove_links_from_file(file_path, dry_run=False):
    """Remove all Markdown links from a file, keeping only the link text."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace [text](url) with text
        link_pattern = re.compile(r'\[(.*?)\]\([^)]*\)')
        # Count the number of links that will be removed
        links_count = len(link_pattern.findall(content))
        modified_content = link_pattern.sub(r'\1', content)
        
        # Only write back if changes were made
        if content != modified_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            return links_count
        return links_count if links_count > 0 else 0
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0

def find_and_process_md_files(directory, dry_run=False, exclude_dirs=None):
    """Find all .md files in the directory and its subdirectories and remove links."""
    directory_path = Path(directory)
    # Get all .md files
    md_files = []
    for path in directory_path.glob('**/*.md'):
        # Skip excluded directories
        if exclude_dirs and any(excluded in str(path) for excluded in exclude_dirs):
            continue
        md_files.append(path)
    
    total_files = len(md_files)
    modified_files = 0
    total_links_removed = 0
    
    print(f"🔍 Found {total_files} Markdown files to process")
    
    for file_path in md_files:
        links_removed = remove_links_from_file(file_path, dry_run)
        total_links_removed += links_removed
        if links_removed > 0:
            modified_files += 1
            action = "Would remove" if dry_run else "Removed"
            print(f"✅ {action} {links_removed} links from {file_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Total files processed: {total_files}")
    print(f"   Files with links: {modified_files}")
    print(f"   Total links {('found' if dry_run else 'removed')}: {total_links_removed}")
    if dry_run:
        print("   No files were modified (dry run)")

def main():
    parser = argparse.ArgumentParser(description='Remove Markdown links from files, keeping only the link text.')
    parser.add_argument('directory', nargs='?', default='docs', 
                        help='Directory to search for Markdown files (default: docs)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--exclude', nargs='+', default=[],
                        help='Directories to exclude from processing')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN: No files will be modified")
    
    find_and_process_md_files(args.directory, args.dry_run, args.exclude)

if __name__ == "__main__":
    main() 