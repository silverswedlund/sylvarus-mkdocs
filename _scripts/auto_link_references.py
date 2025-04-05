#!/usr/bin/env python3
import os
import re
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_auto_link_data(json_path: str) -> Dict:
    """Load auto-link data from a JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Error loading auto-link data from {json_path}: {e}")
        return {}

def get_all_auto_link_strings(data: Dict) -> Dict[str, Tuple[str, str]]:
    """Extract all auto-link strings and their corresponding URLs from the data."""
    auto_link_map = {}
    
    for category, items in data.items():
        base_path = items.get("config", {}).get("base_path", "")
        if not base_path:
            base_path = f"docs/{category.lower()}"
        
        for item_key, item_data in items.get("items", {}).items():
            auto_link_strings = item_data.get("auto_link_strings", [])
            if not auto_link_strings:
                continue
                
            # Normalize the item key for the URL
            normalized_key = item_key.lower().replace("'", "").replace(" ", "")
            
            # Construct the URL based on the base path
            url = f"{normalized_key}/index.md"
            
            # Add all auto-link strings for this item
            for link_string in auto_link_strings:
                auto_link_map[link_string] = (url, base_path)
    
    return auto_link_map

def find_markdown_files(docs_dir: str, include_md_insert: bool = False) -> List[str]:
    """Find all markdown files in the docs directory."""
    markdown_files = []
    
    # Define patterns to match
    patterns = ["**/*.md"]
    if include_md_insert:
        patterns.append("**/*.md_insert")
    
    # Find all markdown files
    for pattern in patterns:
        markdown_files.extend([str(p) for p in Path(docs_dir).glob(pattern)])
    
    return markdown_files

def is_inside_code_block(content: str, position: int) -> bool:
    """Check if the position is inside a code block."""
    # Find all code block markers
    code_markers = list(re.finditer(r'```', content))
    
    # If no code markers or odd number of markers, something is wrong
    if not code_markers or len(code_markers) % 2 != 0:
        return False
    
    # Check if position is between any pair of code markers
    for i in range(0, len(code_markers), 2):
        start = code_markers[i].end()
        end = code_markers[i+1].start() if i+1 < len(code_markers) else len(content)
        if start <= position <= end:
            return True
    
    return False

def is_inside_link(content: str, position: int) -> bool:
    """Check if the position is already inside a markdown link."""
    # Find all markdown links
    links = list(re.finditer(r'\[([^\]]+)\]\([^)]+\)', content))
    
    # Check if position is inside any link
    for link in links:
        if link.start() <= position <= link.end():
            return True
    
    return False

def auto_link_references(content: str, auto_link_map: Dict[str, Tuple[str, str]], file_path: str) -> Tuple[str, int]:
    """Add auto-links to references in the content."""
    modified_content = content
    replacements = 0
    
    # Get the directory of the current file
    file_dir = os.path.dirname(file_path)
    
    # Sort auto-link strings by length (descending) to handle longer matches first
    sorted_links = sorted(auto_link_map.keys(), key=len, reverse=True)
    
    for link_string in sorted_links:
        # Check if the link string contains a caret (^)
        has_caret = "^" in link_string
        display_text = link_string
        
        if has_caret:
            # Split at the caret - display_text is before the caret
            parts = link_string.split("^", 1)
            display_text = parts[0]
            # For search, we use the full string including the caret
            # This is because we want to match the entire pattern in the document
        
        # Escape special regex characters in the link string
        escaped_link = re.escape(link_string)
        
        # Create a pattern that matches the link string with word boundaries or whitespace/start/end
        # Use (?i) for case-insensitive matching
        pattern = rf'(?i)((?:\s|^){escaped_link}(?:\s|$))'
        
        # Find all matches
        matches = list(re.finditer(pattern, modified_content))
        
        # Process matches in reverse order to avoid position shifts
        for match in reversed(matches):
            full_match = match.group(1)
            start, end = match.span(1)
            
            # Skip if inside a code block or already in a link
            if is_inside_code_block(modified_content, start) or is_inside_link(modified_content, start):
                continue
            
            # Get the URL and base path
            url, base_path = auto_link_map[link_string]
            
            # Calculate relative path from current file to target
            rel_path = os.path.relpath(os.path.join(base_path, url), file_dir)
            rel_path = rel_path.replace("\\", "/")  # Normalize path separators for markdown
            
            # Preserve leading/trailing whitespace
            leading_space = ""
            trailing_space = ""
            
            if full_match.startswith(" "):
                leading_space = " "
            if full_match.endswith(" "):
                trailing_space = " "
            
            # For caret notation, use the display_text
            # Otherwise, preserve the original case of the matched text
            if has_caret:
                link_text = display_text
            else:
                link_text = full_match.strip()
            
            # Replace with auto-link, preserving whitespace
            replacement = f"{leading_space}[{link_text}]({rel_path}){trailing_space}"
            modified_content = modified_content[:start] + replacement + modified_content[end:]
            replacements += 1
    
    return modified_content, replacements

def process_file(file_path: str, auto_link_map: Dict[str, Tuple[str, str]], dry_run: bool = False) -> int:
    """Process a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified_content, replacements = auto_link_references(content, auto_link_map, file_path)
        
        if replacements > 0 and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            logging.info(f"✅ Added {replacements} auto-links to {file_path}")
        elif replacements > 0:
            logging.info(f"🔍 Would add {replacements} auto-links to {file_path}")
        
        return replacements
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description='Add auto-links to references in markdown files.')
    parser.add_argument('--docs-dir', default='docs', help='Directory containing markdown files')
    parser.add_argument('--json-dir', default='_json', help='Directory containing JSON data files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    # Load auto-link data from JSON files
    auto_link_data = {}
    
    # Find all JSON files recursively in the json directory
    json_files = list(Path(args.json_dir).glob('**/*.json'))
    logging.info(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        # Extract category from filename or parent directory
        if json_file.parent.name == args.json_dir:
            # Files in the root json directory
            category = json_file.stem.replace('_data', '')
        elif json_file.parent.name == "entities":
            # Files in the entities subdirectory - use the filename without _data suffix
            category = json_file.stem.replace('_data', '')
        else:
            # Files in other subdirectories - use the subdirectory name as category
            category = json_file.parent.name
        
        # Load the JSON data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if this is an entity data file with the expected structure
            if "items" in data:
                # For entities, set the base path to docs/entities/[category]
                base_path = f"docs/entities/{category.lower()}"
                if json_file.parent.name == "entities":
                    base_path = f"docs/entities/{category.lower()}"
                else:
                    base_path = f"docs/{category.lower()}"
                
                # Create a properly structured entry for this category if it doesn't exist
                if category not in auto_link_data:
                    auto_link_data[category] = {
                        "config": {"base_path": base_path},
                        "items": {}
                    }
                
                # Add all items from this file to the category
                auto_link_data[category]["items"].update(data["items"])
                logging.info(f"Added {len(data['items'])} items from {json_file} with base path {base_path}")
        except Exception as e:
            logging.error(f"Error loading data from {json_file}: {e}")
    
    # Get all auto-link strings
    auto_link_map = get_all_auto_link_strings(auto_link_data)
    logging.info(f"Loaded {len(auto_link_map)} auto-link strings")
    
    # Find all markdown files, including .md_insert files
    markdown_files = find_markdown_files(args.docs_dir, include_md_insert=True)
    logging.info(f"Found {len(markdown_files)} markdown files to process")
    
    # Process each file
    total_replacements = 0
    for file_path in markdown_files:
        replacements = process_file(file_path, auto_link_map, args.dry_run)
        total_replacements += replacements
    
    logging.info(f"Total auto-links added: {total_replacements}")

if __name__ == "__main__":
    main()
