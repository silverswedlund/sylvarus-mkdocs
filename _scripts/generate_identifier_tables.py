#!/usr/bin/env python3
import json
import logging
from pathlib import Path
import argparse
import re

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

def get_identifier_mapping():
    """Create a mapping of identifier strings to their keys and categories from all identifier JSON files."""
    identifier_map = {}  # Maps identifier strings to (key, category) tuples
    json_dir = Path("_json")
    identifiers_dir = json_dir / "identifiers"
    
    # Check if identifiers directory exists
    if not identifiers_dir.exists():
        logging.error(f"Identifiers directory not found: {identifiers_dir}")
        return identifier_map
    
    # Process all identifier JSON files
    for json_path in identifiers_dir.glob("*_identifiers_data.json"):
        logging.info(f"Loading identifiers from {json_path.name}")
        
        # Extract category from filename (e.g., "personality" from "personality_identifiers_data.json")
        category_match = re.match(r'(.+)_identifiers_data\.json', json_path.name)
        if not category_match:
            logging.warning(f"Could not extract category from filename: {json_path.name}")
            continue
            
        category = category_match.group(1)
        
        identifiers_data = load_json_data(json_path)
        if not identifiers_data:
            continue
        
        for identifier_key, info in identifiers_data.get("items", {}).items():
            auto_link_strings = info.get("auto_link_strings", [])
            if auto_link_strings:
                for link_string in auto_link_strings:
                    identifier_map[link_string.lower()] = (identifier_key, category)
            else:
                # Use the key itself if no auto-link strings
                identifier_map[identifier_key.lower()] = (identifier_key, category)
    
    return identifier_map

def get_all_identifiers(json_dir: Path):
    """Get all identifiers from all identifier JSON files with their categories."""
    all_identifiers = []  # List of (identifier_key, category) tuples
    identifiers_dir = json_dir / "identifiers"
    
    if not identifiers_dir.exists():
        logging.error(f"Identifiers directory not found: {identifiers_dir}")
        return all_identifiers
    
    for json_path in identifiers_dir.glob("*_identifiers_data.json"):
        # Extract category from filename
        category_match = re.match(r'(.+)_identifiers_data\.json', json_path.name)
        if not category_match:
            continue
            
        category = category_match.group(1)
        
        identifiers_data = load_json_data(json_path)
        if not identifiers_data:
            continue
        
        # Add all identifiers from this file with their category
        for identifier_key in identifiers_data.get("items", {}).keys():
            all_identifiers.append((identifier_key, category))
    
    return all_identifiers

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
    # Structure: {(identifier_key, category): [matches]}
    identifier_matches = {}
    
    # Initialize the dictionary with all identifiers
    for _, (id_key, category) in identifier_map.items():
        if (id_key, category) not in identifier_matches:
            identifier_matches[(id_key, category)] = []
    
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
                for id_string, (id_key, category) in identifier_map.items():
                    if id_string.lower() in lgbtq_id.lower():
                        identifier_matches[(id_key, category)].append(display_name)
                        logging.debug(f"Match found: {entity_key} → {id_key} (via LGBTQ ID: {lgbtq_id})")
                        break
            
            # Check other identifiers
            other_ids = entity_data.get("other_identifiers", [])
            for other_id in other_ids:
                # Check if this ID matches any known identifier
                for id_string, (id_key, category) in identifier_map.items():
                    if id_string.lower() in other_id.lower():
                        identifier_matches[(id_key, category)].append(display_name)
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

def write_id_havers_table_insert(identifier_path, titles, dry_run=False):
    """Write the ID havers table to an insert file."""
    # Get the directory containing the identifier file
    identifier_dir = identifier_path.parent
    
    # Create the insert file path in the same directory as the identifier file
    # Use the identifier filename (without extension) for the insert filename
    identifier_name = identifier_path.stem
    insert_file_path = identifier_dir / f"{identifier_name}_id_havers_table.md_insert"
    
    # Generate the table
    table = generate_id_havers_table(titles)
    
    # Create parent directories if they don't exist
    if not dry_run:
        identifier_dir.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(table)
        logging.info(f"✅ Updated ID havers table for {identifier_name}")
    else:
        logging.info(f"🔍 Would update ID havers table for {identifier_name}")
        logging.info(f"Table content would be:\n{table}")
    
    return True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate ID havers tables for identifiers.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting generate_identifier_tables.py")
    
    # Paths
    json_dir = Path("_json")
    identifiers_base_path = Path("docs/identifiers")
    
    # Create identifier mapping from all identifier JSON files
    identifier_map = get_identifier_mapping()
    logging.info(f"Loaded {len(identifier_map)} identifier strings for {len(set(identifier_map.values()))} unique identifiers")
    
    # Get all identifiers with their categories
    all_identifiers = get_all_identifiers(json_dir)
    logging.info(f"Found {len(all_identifiers)} total identifiers across all categories")
    
    # Get all JSON files to process (excluding identifier JSON files)
    json_files = []
    
    # Add files from specific directories
    directories_to_process = [
        json_dir / "entities",
        json_dir / "locations",
        json_dir / "documents"
    ]
    
    # Add specific files at the root level
    root_files_to_process = [
        "materials_data.json",
        "pantheons_data.json",
        "species_data.json",
        "time_periods_data.json"
    ]
    
    # Collect all JSON files from specified directories
    for directory in directories_to_process:
        if directory.exists():
            for path in directory.glob("*.json"):
                json_files.append(path)
    
    # Add root-level files
    for filename in root_files_to_process:
        file_path = json_dir / filename
        if file_path.exists():
            json_files.append(file_path)
    
    logging.info(f"Found {len(json_files)} JSON files to process")
    
    # Find all matches for each identifier
    identifier_matches = find_identifier_matches(json_files, identifier_map)
    
    # Track statistics
    total_identifiers = len(all_identifiers)
    updated_identifiers = 0
    
    # Generate and write tables for ALL identifiers, even those with no matches
    for identifier_key, category in all_identifiers:
        # Get matches for this identifier (empty list if none)
        matches = identifier_matches.get((identifier_key, category), [])
        
        # Remove duplicates while preserving order
        unique_matches = []
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)
        
        # Get the identifier file path in the appropriate category subdirectory
        identifier_path = identifiers_base_path / category / f"{identifier_key.lower()}.md"
        
        # Create the category directory if it doesn't exist
        if not identifier_path.parent.exists() and not args.dry_run:
            identifier_path.parent.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {identifier_path.parent}")
        
        # Write the ID havers table (even if empty)
        if write_id_havers_table_insert(identifier_path, unique_matches, args.dry_run):
            updated_identifiers += 1
            if matches:
                logging.info(f"  ✅ Updated {identifier_key} (category: {category}) with {len(unique_matches)} ID havers")
            else:
                logging.info(f"  ✅ Created empty table for {identifier_key} (category: {category})")
    
    logging.info(f"\n✅ Summary: Updated {updated_identifiers} out of {total_identifiers} identifiers.")
    logging.info("Finished generate_identifier_tables.py")

if __name__ == "__main__":
    main()
