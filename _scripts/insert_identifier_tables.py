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

def get_identifier_mapping(identifiers_data):
    """Create a mapping of identifier strings to their keys."""
    identifier_map = {}
    
    for identifier_key, info in identifiers_data.get("items", {}).items():
        auto_link_strings = info.get("auto_link_strings", [])
        if auto_link_strings:
            for link_string in auto_link_strings:
                identifier_map[link_string.lower()] = identifier_key
        else:
            # Use the key itself if no auto-link strings
            identifier_map[identifier_key.lower()] = identifier_key
    
    return identifier_map

def get_entity_display_name(entity_data):
    """Get the display name for an entity (first auto-link string or name)."""
    if "auto_link_strings" in entity_data and entity_data["auto_link_strings"]:
        # Use the first auto-link string exactly as it appears
        return entity_data["auto_link_strings"][0]
    elif "name" in entity_data:
        return entity_data["name"]
    else:
        return "Unknown Entity"

def find_identifier_matches(json_files, identifier_map):
    """Find all entities that match each identifier."""
    # Initialize a dictionary to store matches for each identifier
    identifier_matches = {identifier_key: [] for identifier_key in set(identifier_map.values())}
    
    # Process each JSON file
    for json_file in json_files:
        data = load_json_data(json_file)
        if not data:
            continue
        
        logging.info(f"Processing {json_file.name}")
        
        # Process each entity in the JSON file
        for entity_key, entity_data in data.get("items", {}).items():
            # Get the display name for this entity
            display_name = get_entity_display_name(entity_data)
            
            # Check LGBTQ identifications
            lgbtq_ids = entity_data.get("lgbtq_identifications", [])
            for lgbtq_id in lgbtq_ids:
                # Check if this ID matches any known identifier
                for id_string, id_key in identifier_map.items():
                    if id_string.lower() in lgbtq_id.lower():
                        identifier_matches[id_key].append(display_name)
                        logging.debug(f"Match found: {entity_key} → {id_key} (via LGBTQ ID: {lgbtq_id})")
                        break
            
            # Check other identifiers
            other_ids = entity_data.get("other_identifiers", [])
            for other_id in other_ids:
                # Check if this ID matches any known identifier
                for id_string, id_key in identifier_map.items():
                    if id_string.lower() in other_id.lower():
                        identifier_matches[id_key].append(display_name)
                        logging.debug(f"Match found: {entity_key} → {id_key} (via Other ID: {other_id})")
                        break
    
    return identifier_matches

def generate_id_havers_table(titles):
    """Generate a markdown table of ID havers."""
    if not titles:
        return "| ID Havers |\n|----------------|\n| _No references found_ |"
    
    # Create the markdown table
    table = "| ID Havers |\n|----------------|"
    
    # Add each entity as a row - use plain text without links
    for title in sorted(titles):  # Sort alphabetically
        table += f"\n| {title} |"
    
    return table

def write_id_havers_table_insert(identifier_dir, titles, dry_run=False):
    """Write the ID havers table to an insert file."""
    insert_file_path = identifier_dir / "id_havers_table.md_insert"
    
    # Generate the table
    table = generate_id_havers_table(titles)
    
    # Create parent directories if they don't exist
    if not dry_run:
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(table)
        logging.info(f"✅ Updated ID havers table for {identifier_dir.name}")
    else:
        logging.info(f"🔍 Would update ID havers table for {identifier_dir.name}")
        logging.info(f"Table content would be:\n{table}")
    
    return True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate ID havers tables for identifiers.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting insert_identifier_tables.py")
    
    # Paths
    json_dir = Path("_json")
    identifiers_json_path = json_dir / "identifiers_data.json"
    identifiers_base_path = Path("docs/identifiers")
    
    # Load identifiers data
    identifiers_data = load_json_data(identifiers_json_path)
    if not identifiers_data:
        logging.error("❌ Failed to load identifiers data.")
        return
    
    # Create identifier mapping
    identifier_map = get_identifier_mapping(identifiers_data)
    logging.info(f"Loaded {len(identifier_map)} identifier strings for {len(set(identifier_map.values()))} unique identifiers")
    
    # Get all JSON files except identifiers_data.json - including files in subdirectories
    json_files = []
    for path in json_dir.glob("**/*.json"):
        if path.name != "identifiers_data.json":
            json_files.append(path)
    
    logging.info(f"Found {len(json_files)} JSON files to process")
    
    # Find all matches for each identifier
    identifier_matches = find_identifier_matches(json_files, identifier_map)
    
    # Track statistics
    total_identifiers = len(identifier_matches)
    updated_identifiers = 0
    
    # Generate and write tables for each identifier
    for identifier_key, matches in identifier_matches.items():
        # Skip if no matches
        if not matches:
            logging.info(f"No matches found for identifier: {identifier_key}")
            continue
        
        # Remove duplicates while preserving order
        unique_matches = []
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)
        
        # Get the identifier directory
        identifier_dir = identifiers_base_path / identifier_key.lower()
        
        # Skip if directory doesn't exist
        if not identifier_dir.exists():
            logging.warning(f"⚠️ Directory not found for identifier: {identifier_key}")
            continue
        
        # Write the ID havers table
        if write_id_havers_table_insert(identifier_dir, unique_matches, args.dry_run):
            updated_identifiers += 1
            logging.info(f"  ✅ Updated {identifier_key} with {len(unique_matches)} ID havers")
    
    logging.info(f"\n✅ Summary: Updated {updated_identifiers} out of {total_identifiers} identifiers.")
    logging.info("Finished insert_identifier_tables.py")

if __name__ == "__main__":
    main()
