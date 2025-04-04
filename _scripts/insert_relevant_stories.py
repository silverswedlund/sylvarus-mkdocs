#!/usr/bin/env python3

import json
import os
import re
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# === CONFIGURABLE SETTINGS ===
JSON_DIR = Path("_json")
STORIES_JSON_PATH = JSON_DIR / "stories_data.json"

# === CONFIGURABLE EXCEPTIONS ===
EXCLUDED_PATHS = [
    "docs/stories",  # Don't search story pages themselves
    # Add more full paths to exclude as needed
]

# === HELPER: Load JSON data ===
def load_json_data(json_path: Path):
    """Load JSON data from a file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {json_path}: {e}")
        return None

# === HELPER: Find stories for entity ===
def find_stories_for_entity(auto_links, stories_data):
    """Find all stories that mention the entity based on its auto-linking strings."""
    matching_stories = []
    base_path = Path(stories_data.get("config", {}).get("base_path", "docs/stories"))
    
    for story_id, story_info in stories_data.get("items", {}).items():
        story_dir = base_path / story_id
        
        # Skip if story directory doesn't exist
        if not story_dir.exists():
            continue
        
        # Look for the index.md file in the story directory
        index_file = story_dir / "index.md"
        if not index_file.exists():
            continue
        
        # Read the story index content and check for auto-links
        try:
            content = index_file.read_text(encoding='utf-8').lower()
            
            # Check if any of the entity's auto-linking strings are in the content
            for auto_link in auto_links:
                if auto_link and auto_link.lower() in content:
                    # Use auto_link_strings if available, otherwise use name or key
                    display_name = story_id.replace("_", " ").title()
                    if "name" in story_info:
                        display_name = story_info["name"]
                    if "auto_link_strings" in story_info and story_info["auto_link_strings"]:
                        display_name = story_info["auto_link_strings"][0]
                        
                    story_path = f"../../../../stories/{story_id}"
                    matching_stories.append((display_name, story_path))
                    break  # Found a match, no need to check other auto-links
        except Exception as e:
            logging.error(f"Error reading story index for {story_id}: {e}")
    
    return matching_stories

# === HELPER: Generate story table ===
def generate_story_table(stories):
    """Generate a markdown table of stories."""
    if not stories:
        return "| Stories |\n|--------|\n| *No stories found featuring this character* |"
    
    # Create the markdown table
    table = "| Stories |\n|--------|"
    
    # Add each story as a row - use plain text without links
    for story_name, _ in sorted(stories):  # Sort stories alphabetically
        table += f"\n| {story_name} |"
    
    return table

# === HELPER: Write table to insert file ===
def write_stories_table_insert(entity_dir, stories, dry_run=False):
    """Write the stories table to an insert file."""
    insert_file_path = entity_dir / "stories_table.md_insert"
    
    # Generate the story table
    story_table = generate_story_table(stories)
    
    # Create parent directories if they don't exist
    if not dry_run:
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(story_table)
        logging.info(f"✅ Updated stories table for {entity_dir.name}")
    else:
        logging.info(f"🔍 Would update stories table for {entity_dir.name}")
        logging.info(f"Table content would be:\n{story_table}")
    
    return True

# === MAIN FUNCTION ===
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate relevant stories tables for entities.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting insert_relevant_stories.py")
    
    # Load stories data
    stories_data = load_json_data(Path("_json/stories_data.json"))
    if not stories_data:
        logging.error("❌ Failed to load stories data.")
        return
    
    # Get all entity JSON files
    entity_json_files = [
        Path("_json/gods_data.json"),
        Path("_json/titans_data.json"),
        Path("_json/immortals_data.json"),
        Path("_json/demigods_data.json")
        # Add more entity JSON files as needed
    ]
    
    # Process each entity JSON file
    total_entities = 0
    updated_entities = 0
    
    for entity_json_path in entity_json_files:
        # Load entity data
        entity_data = load_json_data(entity_json_path)
        if not entity_data:
            continue
        
        # Skip if not an entity type
        config = entity_data.get("config", {})
        if config.get("type") != "entity":
            logging.info(f"Skipping {entity_json_path.name} - not an entity type")
            continue
        
        # Find stories that reference each entity
        entity_references = find_entity_references(stories_data, entity_data)
        
        # Get the base path for this entity type
        base_path = entity_data.get("config", {}).get("base_path", "")
        if not base_path:
            logging.warning(f"⚠️ No base path found for {entity_json_path.name}")
            continue
        
        # Update relevant stories tables
        file_name = entity_json_path.name
        entity_count = len(entity_data.get("items", {}))
        total_entities += entity_count
        updated_count = 0
        
        for entity_id, stories in entity_references.items():
            # Construct the path to the entity's directory
            entity_dir = Path(base_path) / entity_id.lower()
            
            # Write the relevant stories table
            if write_stories_table_insert(entity_dir, stories, args.dry_run):
                updated_count += 1
                logging.info(f"  ✅ Updated {entity_id} with {len(stories)} stories")
        
        logging.info(f"  Updated {updated_count} of {entity_count} entities in {file_name}")
    
    logging.info(f"\n✅ Summary: Updated {updated_entities} out of {total_entities} entities.")
    logging.info("Finished insert_relevant_stories.py")

def find_entity_references(stories_data, entity_data):
    """Find all stories that reference each entity based on character_names lists."""
    entity_references = {}
    
    # Skip if entity data is not of type "entity"
    config = entity_data.get("config", {})
    if config.get("type") != "entity":
        logging.info(f"Skipping entity data - not an entity type")
        return entity_references
    
    # Initialize references for all entities
    for entity_key in entity_data.get("items", {}).keys():
        entity_references[entity_key] = []
    
    # Process each entity
    for entity_key, entity_info in entity_data.get("items", {}).items():
        # Get the entity's auto-link strings
        auto_link_strings = entity_info.get("auto_link_strings", [])
        if not auto_link_strings:
            # Use the entity key as fallback
            auto_link_strings = [entity_key]
        
        # Find stories that include this entity in their character_names
        for story_key, story_info in stories_data.get("items", {}).items():
            character_names = story_info.get("character_names", [])
            
            # Check if any of the entity's auto-link strings match a character name
            if any(auto_link in character_names for auto_link in auto_link_strings):
                # Get the story's display name
                story_name = story_key
                if "auto_link_strings" in story_info and story_info["auto_link_strings"]:
                    story_name = story_info["auto_link_strings"][0]
                elif "name" in story_info:
                    story_name = story_info["name"]
                
                # Get the story's path
                story_rel_path = f"../../stories/{story_key.lower()}/index.md"
                
                # Add to the list of stories for this entity
                entity_references[entity_key].append((story_name, story_rel_path))
                logging.info(f"Found story '{story_name}' for entity '{entity_key}'")
    
    return entity_references

if __name__ == "__main__":
    main()