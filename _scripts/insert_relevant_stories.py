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
def write_stories_table_insert(entity_path, stories, dry_run=False):
    """Write the stories table to an insert file."""
    insert_file_path = entity_path.parent / "stories_table.md_insert"
    
    # Generate the story table
    story_table = generate_story_table(stories)
    
    # Create parent directories if they don't exist
    if not dry_run:
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to the insert file
    if not dry_run:
        with open(insert_file_path, "w", encoding="utf-8") as f:
            f.write(story_table)
        logging.info(f"✅ Updated stories table for {entity_path.parent.name}")
    else:
        logging.info(f"🔍 Would update stories table for {entity_path.parent.name}")
        logging.info(f"Table content would be:\n{story_table}")
    
    return True

# === MAIN FUNCTION ===
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate story tables for entities.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        logging.info("🔍 DRY RUN: No files will be modified")
    
    logging.info("🔍 Starting insert_relevant_stories.py")
    
    # Load stories data
    stories_data = load_json_data(STORIES_JSON_PATH)
    if not stories_data:
        logging.error("❌ Failed to load stories data.")
        return
    
    # Get all JSON data files
    json_files = [f for f in JSON_DIR.glob("*.json") if f.name != "stories_data.json"]
    
    # Track statistics
    total_entities = 0
    updated_entities = 0
    
    # Process each JSON file
    for json_file in json_files:
        file_name = json_file.name
        logging.info(f"Processing {file_name}...")
        
        # Load the JSON data
        try:
            data = load_json_data(json_file)
        except Exception as e:
            logging.error(f"❌ Error loading {json_file}: {e}")
            continue
        
        # Get the base path from the config
        base_path = data.get("config", {}).get("base_path", "")
        if not base_path:
            logging.warning(f"⚠️ No base path found in {json_file}")
            continue
        
        # Process each item in the JSON file
        entity_count = 0
        updated_count = 0
        
        for item_id, item_data in data.get("items", {}).items():
            total_entities += 1
            entity_count += 1
            
            # Get the auto-linking strings
            auto_links = item_data.get("auto_link_strings", [])
            if not auto_links:
                continue
            
            # Construct the path to the entity's markdown file
            entity_path = Path(base_path) / item_id / "index.md"
            
            # Skip if file doesn't exist
            if not entity_path.exists():
                continue
            
            # Find stories for this entity
            stories = find_stories_for_entity(auto_links, stories_data)
            
            # Write the stories table to an insert file
            if write_stories_table_insert(entity_path, stories, args.dry_run):
                updated_entities += 1
                updated_count += 1
                logging.info(f"  ✅ Updated {item_id} with {len(stories)} stories")
        
        logging.info(f"  Updated {updated_count} of {entity_count} entities in {file_name}")
    
    logging.info(f"\n✅ Summary: Updated {updated_entities} out of {total_entities} entities.")
    logging.info("Finished insert_relevant_stories.py")

if __name__ == "__main__":
    main()