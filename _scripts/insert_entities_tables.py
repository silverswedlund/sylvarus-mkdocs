#!/usr/bin/env python3
import json
import logging
from pathlib import Path
import re
import sys
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Map table placeholders to their corresponding JSON files
ENTITY_CATEGORIES = [
    {"name": "Gods", "json_file": "_json/gods_data.json"},
    {"name": "Demigods", "json_file": "_json/demigods_data.json"},
    {"name": "Titans", "json_file": "_json/titans_data.json"},
    {"name": "Primordial Beings", "json_file": ""},
    {"name": "Mortals", "json_file": ""},
    {"name": "Beasts", "json_file": ""},
    {"name": "Constructs", "json_file": ""},
    {"name": "Chaos Dieties", "json_file": ""},
    {"name": "Other Entities", "json_file": ""}
]

def load_json_data(json_path):
    """Load data from a JSON file if it exists."""
    try:
        if not json_path or not Path(json_path).exists():
            logging.warning(f"JSON file not found: {json_path}")
            return None
        with open(json_path, "r", encoding="utf-8") as f:
            logging.info(f"Loading data from {json_path}")
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load data from {json_path}: {e}")
        return None

def get_entity_names(json_path):
    """Get sorted list of entity names from a JSON file."""
    data = load_json_data(json_path)
    if not data:
        return []
    
    entity_names = []
    for entity_key, entity_info in data.get("items", {}).items():
        auto_link_strings = entity_info.get("auto_link_strings", [])
        if auto_link_strings:
            # Use the first auto_link_string
            entity_name = auto_link_strings[0]
            entity_names.append(entity_name)
    
    # Sort entity names alphabetically
    entity_names.sort()
    return entity_names

def construct_entity_table_rows(dry_run=False):
    """Construct rows for the entity table."""
    # Get entity names for each category
    category_entities = []
    max_entities = 0
    
    for category in ENTITY_CATEGORIES:
        if category["json_file"]:
            entities = get_entity_names(category["json_file"])
            if dry_run:
                logging.info(f"Found {len(entities)} entities for {category['name']}")
        else:
            entities = []
            if dry_run:
                logging.info(f"No JSON file for {category['name']}")
        
        category_entities.append(entities)
        max_entities = max(max_entities, len(entities))
    
    # Construct table rows
    rows = []
    for i in range(max_entities):
        row = []
        for entities in category_entities:
            if i < len(entities):
                row.append(entities[i])
            else:
                row.append("")
        # Only add the row if it has at least one non-empty cell
        if any(cell != "" for cell in row):
            rows.append(row)
    
    # Convert rows to HTML
    html_rows = []
    for row in rows:
        cells = [f"<td>{entity}</td>" for entity in row]
        html_rows.append(f"    <tr>\n      {''.join(cells)}\n    </tr>")
    
    return "\n".join(html_rows)

def update_entity_disambiguation(disambiguation_path, dry_run=False):
    """Update the entity disambiguation file with the entity table."""
    try:
        # Read the current content
        content = disambiguation_path.read_text(encoding="utf-8")
        original_content = content
        
        # Generate the table rows
        table_rows = construct_entity_table_rows(dry_run)
        
        # Check if the placeholder exists
        if "|entity_table_rows|" in content:
            content = content.replace("|entity_table_rows|", table_rows)
            logging.info("Replacing entity table rows placeholder")
        else:
            # Look for existing table
            table_pattern = re.compile(r'<table class="entity-table">.*?<tbody>\s*(.*?)\s*</tbody>\s*</table>', re.DOTALL)
            match = table_pattern.search(content)
            if match:
                # Replace the existing table rows
                table_start = content.find("<tbody>", match.start()) + len("<tbody>")
                table_end = content.find("</tbody>", table_start)
                content = content[:table_start] + "\n" + table_rows + "\n  " + content[table_end:]
                logging.info("Replacing existing entity table rows")
            else:
                logging.warning("Could not find entity table or placeholder in the file")
                return
        
        # Write the updated content if changes were made
        if content != original_content and not dry_run:
            disambiguation_path.write_text(content, encoding="utf-8")
            logging.info(f"✅ Updated entity table in {disambiguation_path}")
        else:
            if dry_run:
                logging.info(f"🔍 Would update entity table in {disambiguation_path}")
            else:
                logging.info(f"ℹ️ No changes needed in {disambiguation_path}")
            
    except Exception as e:
        logging.error(f"Failed to update {disambiguation_path}: {e}")
        sys.exit(1)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Update entity table in the entity disambiguation file.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    # Path to the entity disambiguation file
    entity_disambiguation_path = Path("docs/entities/entity_disambiguation.md")
    
    # Update the entity disambiguation file
    update_entity_disambiguation(entity_disambiguation_path, args.dry_run)

if __name__ == "__main__":
    main()
