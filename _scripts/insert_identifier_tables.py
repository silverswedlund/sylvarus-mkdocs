#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# === CONFIGURABLE EXCEPTIONS ===
EXCLUDED_PATHS = [
    "docs/identifiers",  # Don't search identifier pages themselves
    # Add more full paths to exclude as needed
]

# === PATHS ===
base_docs = Path("docs")
identifier_json_path = Path("_json/identifiers_data.json")
identifiers_base_path = base_docs / "identifiers"

# === HELPER: Extract title from index.md (fallback to folder name) ===
def extract_title(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    return match.group(1).strip() if match else path.parent.name

# === HELPER: Check if path should be excluded ===
def should_exclude(path: Path) -> bool:
    path_str = str(path)
    return any(excl in path_str for excl in EXCLUDED_PATHS)

# === HELPER: Load JSON data ===
def load_json_data(json_path: Path):
    """Load JSON data from a file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {json_path}: {e}")
        return None

# === HELPER: Generate related pages table ===
def generate_related_pages_table(matches):
    """Generate a markdown table of related pages."""
    if not matches:
        return "| Related Pages |\n|----------------|\n| _No references found_ |"
    
    # Create the markdown table
    table = "| Related Pages |\n|----------------|"
    
    # Add each page as a row - use plain text without links
    for title, _ in sorted(matches):  # Sort alphabetically
        table += f"\n| {title} |"
    
    return table

# === HELPER: Write table to insert file ===
def write_related_pages_insert(identifier_dir, matches, dry_run=False):
    """Write the related pages table to an insert file."""
    insert_file_path = identifier_dir / "related_pages.md_insert"
    
    # Generate the table
    table = generate_related_pages_table(matches)
    
    # Create parent directories if they don't exist
    if not dry_run:
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(table)
        logging.info(f"✅ Updated related pages for {identifier_dir.name}")
    else:
        logging.info(f"🔍 Would update related pages for {identifier_dir.name}")
        logging.info(f"Table content would be:\n{table}")
    
    return True

# === MAIN FUNCTION ===
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate related pages tables for identifiers.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting insert_identifier_tables.py")
    
    # Paths
    base_docs = Path("docs")
    identifier_json_path = Path("_json/identifiers_data.json")
    identifiers_base_path = base_docs / "identifiers"
    
    # Load identifiers from JSON
    identifiers_data = load_json_data(identifier_json_path)
    if not identifiers_data:
        logging.error("❌ Failed to load identifiers data.")
        return
    
    identifiers = identifiers_data.get("items", {})
    
    # Track statistics
    total_identifiers = 0
    updated_identifiers = 0
    
    # Process each identifier
    for identifier_key, info in identifiers.items():
        total_identifiers += 1
        
        # Use auto_link_strings if available, otherwise use name or key
        display_name = identifier_key
        if "name" in info:
            display_name = info["name"]
        if "auto_link_strings" in info and info["auto_link_strings"]:
            display_name = info["auto_link_strings"][0]
        
        identifier_dir = identifiers_base_path / identifier_key.lower()
        identifier_index = identifier_dir / "index.md"
        
        if not identifier_index.exists():
            logging.warning(f"⚠️ Index file not found for {display_name}")
            continue
        
        matches = []
        
        # Search ALL index.md files in docs directory
        for index_file in base_docs.rglob("index.md"):
            if should_exclude(index_file):
                continue
                
            try:
                content = index_file.read_text(encoding="utf-8").lower()
                if display_name.lower() in content:
                    logging.info(f"Found match in: {index_file}")
                    title = extract_title(index_file)
                    rel_path = os.path.relpath(index_file, identifier_dir)
                    matches.append((title, rel_path))
            except Exception as e:
                logging.error(f"Error processing {index_file}: {e}")
        
        # Write the related pages table to an insert file
        if write_related_pages_insert(identifier_dir, matches, args.dry_run):
            updated_identifiers += 1
            logging.info(f"  ✅ Updated {display_name} with {len(matches)} related pages")
    
    logging.info(f"\n✅ Summary: Updated {updated_identifiers} out of {total_identifiers} identifiers.")
    logging.info("Finished insert_identifier_tables.py")

if __name__ == "__main__":
    main()
