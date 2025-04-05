#!/usr/bin/env python3
import json
import logging
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_json_data(json_path: Path):
    """Load JSON data from a file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {json_path}: {e}")
        return None

def get_entity_display_name(entity_data):
    """Get the display name for an entity (first auto-link string or name)."""
    if "auto_link_strings" in entity_data and entity_data["auto_link_strings"]:
        # Use the first auto-link string exactly as it appears
        return entity_data["auto_link_strings"][0]
    elif "name" in entity_data:
        return entity_data["name"]
    else:
        return "Unknown Entity"

def generate_entity_table(entities, subtype):
    """Generate a markdown table of entities."""
    # Capitalize the subtype and handle basic pluralization
    header = subtype.title() + "s"
    
    # Special case pluralization rules
    if subtype.lower().endswith('y'):
        header = subtype.title()[:-1] + 'ies'
    
    if not entities:
        return f"| {header} |\n|----------|\n| *No {subtype}s found* |"
    
    # Create the markdown table
    table = f"| {header} |\n|----------|"
    
    # Add each entity as a row - use plain text without links
    for entity_name in sorted(entities):  # Sort alphabetically
        table += f"\n| {entity_name} |"
    
    return table

def write_entity_table_insert(base_path, subtype, entities, dry_run=False):
    """Write the entity table to an insert file."""
    # Create the path for the insert file
    base_dir = Path(base_path)
    insert_file_path = base_dir / f"{subtype}_table.md_insert"
    
    # Generate the table
    table = generate_entity_table(entities, subtype)
    
    # Create parent directories if they don't exist
    if not dry_run:
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(table)
        logging.info(f"✅ Updated {subtype} table at {insert_file_path}")
    else:
        logging.info(f"🔍 Would update {subtype} table at {insert_file_path}")
        logging.info(f"Table content would be:\n{table}")
    
    return True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate sub-entity tables.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting insert_sub_entity_tables.py")
    
    # Get all JSON files in the _json/entities directory
    json_dir = Path("_json/entities")
    if not json_dir.exists():
        logging.error(f"Entities directory not found: {json_dir}")
        return
        
    json_files = list(json_dir.glob("*.json"))
    logging.info(f"Found {len(json_files)} JSON files to process in {json_dir}")
    
    # Track statistics
    total_subtypes = 0
    updated_subtypes = 0
    
    # Process each JSON file
    for json_file in json_files:
        # Load the JSON data
        data = load_json_data(json_file)
        if not data:
            continue
        
        # Check if this is an entity type
        config = data.get("config", {})
        if config.get("type") != "entity":
            logging.info(f"Skipping {json_file.name} - not an entity type")
            continue
        
        # Get the subtype and base path
        subtype = config.get("subtype")
        base_path = config.get("base_path")
        
        if not subtype:
            logging.warning(f"⚠️ No subtype found for {json_file.name}")
            continue
            
        if not base_path:
            logging.warning(f"⚠️ No base path found for {json_file.name}")
            continue
        
        logging.info(f"Processing {json_file.name} - subtype: {subtype}")
        total_subtypes += 1
        
        # Get all entities of this subtype
        entity_names = []
        for entity_key, entity_data in data.get("items", {}).items():
            display_name = get_entity_display_name(entity_data)
            entity_names.append(display_name)
        
        # Write the entity table
        if write_entity_table_insert(base_path, subtype, entity_names, args.dry_run):
            updated_subtypes += 1
    
    logging.info(f"\n✅ Summary: Updated {updated_subtypes} out of {total_subtypes} subtype tables.")
    logging.info("Finished insert_sub_entity_tables.py")

if __name__ == "__main__":
    main()
