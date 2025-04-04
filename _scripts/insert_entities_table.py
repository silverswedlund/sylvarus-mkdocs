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
    {"name": "Immortals", "json_file": "_json/immortals_data.json"},
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
    
    entity_info = []
    for entity_key, entity_data in data.get("items", {}).items():
        # Use the first auto_link_string if available, otherwise use the entity key
        display_name = entity_key
        if "auto_link_strings" in entity_data and entity_data["auto_link_strings"]:
            display_name = entity_data["auto_link_strings"][0]
        
        # Store both the display name and the entity key for path generation
        entity_info.append({
            "display_name": display_name,
            "entity_key": entity_key
        })
    
    # Sort entity info alphabetically by display name
    entity_info.sort(key=lambda x: x["display_name"])
    return entity_info

def construct_entity_markdown_table(dry_run=False):
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
    
    # Create the table header
    header_row = " | ".join([category["name"] for category in ENTITY_CATEGORIES])
    separator_row = "|".join(["---" for _ in ENTITY_CATEGORIES])
    
    # Create the table rows
    rows = []
    rows.append(header_row)
    rows.append(separator_row)
    
    for i in range(max_entities):
        row_cells = []
        for j, entities in enumerate(category_entities):
            if i < len(entities):
                entity_info = entities[i]
                display_name = entity_info["display_name"]
                row_cells.append(f" {display_name} ")
            else:
                row_cells.append("")
        # Only add the row if it has at least one non-empty cell
        if any(cell != "" for cell in row_cells):
            rows.append(" | ".join(row_cells))
    
    return "\n".join(rows)

def write_entities_table_insert(insert_file_path, markdown_table, dry_run=False):
    """Write the entity table to the insert file."""
    try:
        # Create parent directories if they don't exist
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not dry_run:
            # Write the table to the insert file
            insert_file_path.write_text(markdown_table, encoding="utf-8")
            logging.info(f"✅ Entity table written to {insert_file_path}")
        else:
            logging.info(f"🔍 Would write entity table to {insert_file_path}")
            
    except Exception as e:
        logging.error(f"Failed to write to {insert_file_path}: {e}")
        sys.exit(1)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate entity table and write to insert file.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    # Path to the entity table insert file
    insert_file_path = Path("docs/entities/entities_table.md_insert")
    
    # Generate the entity table
    markdown_table = construct_entity_markdown_table(args.dry_run)
    
    # Write the table to the insert file
    write_entities_table_insert(insert_file_path, markdown_table, args.dry_run)

if __name__ == "__main__":
    main()
