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

def get_species_mapping(species_data):
    """Create a mapping of species names to their keys."""
    species_map = {}
    
    for species_key, info in species_data.get("items", {}).items():
        auto_link_strings = info.get("auto_link_strings", [])
        if auto_link_strings:
            for link_string in auto_link_strings:
                species_map[link_string.lower()] = species_key
        else:
            # Use the key itself if no auto-link strings
            species_map[species_key.lower()] = species_key
    
    return species_map

def get_entity_display_name(entity_data):
    """Get the display name for an entity (first auto-link string or name)."""
    if "auto_link_strings" in entity_data and entity_data["auto_link_strings"]:
        # Use the first auto-link string exactly as it appears
        return entity_data["auto_link_strings"][0]
    elif "name" in entity_data:
        return entity_data["name"]
    else:
        return "Unknown Entity"

def find_species_matches(json_files, species_map):
    """Find all entities that match each species."""
    # Initialize a dictionary to store matches for each species
    species_matches = {species_key: [] for species_key in set(species_map.values())}
    
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
            
            # Check for species field
            for field, value in entity_data.items():
                if "species" in field.lower() and isinstance(value, str):
                    # Check if this species matches any known species
                    for species_string, species_key in species_map.items():
                        if species_string.lower() in value.lower():
                            species_matches[species_key].append(display_name)
                            logging.debug(f"Match found: {entity_key} → {species_key} (via species: {value})")
                            break
    
    return species_matches

def generate_species_members_table(titles):
    """Generate a markdown table of species members."""
    if not titles:
        return "| Species Members |\n|----------------|\n| _No members found_ |"
    
    # Create the markdown table
    table = "| Species Members |\n|----------------|"
    
    # Add each entity as a row - use plain text without links
    for title in sorted(titles):  # Sort alphabetically
        table += f"\n| {title} |"
    
    return table

def write_species_members_table_insert(species_dir, titles, dry_run=False):
    """Write the species members table to an insert file."""
    insert_file_path = species_dir / "species_members_table.md_insert"
    
    # Generate the table
    table = generate_species_members_table(titles)
    
    # Create parent directories if they don't exist
    if not dry_run:
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(table)
        logging.info(f"✅ Updated species members table for {species_dir.name}")
    else:
        logging.info(f"🔍 Would update species members table for {species_dir.name}")
        logging.info(f"Table content would be:\n{table}")
    
    return True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate species members tables for species.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting insert_species_members_tables.py")
    
    # Paths
    json_dir = Path("_json/entities")
    species_json_path = Path("_json/species_data.json")
    species_base_path = Path("docs/species")
    
    # Load species data
    species_data = load_json_data(species_json_path)
    if not species_data:
        logging.error("❌ Failed to load species data.")
        return
    
    # Create species mapping
    species_map = get_species_mapping(species_data)
    logging.info(f"Loaded {len(species_map)} species strings for {len(set(species_map.values()))} unique species")
    
    # Get all JSON files in the _json/entities directory
    json_files = list(json_dir.glob("*.json"))
    
    logging.info(f"Found {len(json_files)} JSON files to process")
    
    # Find all matches for each species
    species_matches = find_species_matches(json_files, species_map)
    
    # Track statistics
    total_species = len(species_matches)
    updated_species = 0
    
    # Generate and write tables for each species
    for species_key, matches in species_matches.items():
        # Remove duplicates while preserving order
        unique_matches = []
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)
        
        # Get the species directory
        species_dir = species_base_path / species_key.lower()
        
        # Ensure the directory exists
        if not species_dir.exists():
            species_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the species members table
        if write_species_members_table_insert(species_dir, unique_matches, args.dry_run):
            updated_species += 1
            logging.info(f"  ✅ Updated {species_key} with {len(unique_matches)} species members")
    
    logging.info(f"\n✅ Summary: Updated {updated_species} out of {total_species} species.")
    logging.info("Finished insert_species_members_tables.py")

if __name__ == "__main__":
    main()
