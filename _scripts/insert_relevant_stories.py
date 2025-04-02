#!/usr/bin/env python3

import json
import os
import re
from pathlib import Path

# === CONFIGURABLE SETTINGS ===
STORY_TABLE_MARKER = "|relevant_story_table|"
JSON_DIR = Path("_json")
STORIES_JSON_PATH = JSON_DIR / "stories_data.json"

# === CONFIGURABLE EXCEPTIONS ===
EXCLUDED_PATHS = [
    "docs/stories",  # Don't search story pages themselves
    # Add more full paths to exclude as needed
]

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
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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
                    story_name = story_info.get("name", story_id.replace("_", " ").title())
                    story_path = f"../../../../stories/{story_id}"
                    matching_stories.append((story_name, story_path))
                    break  # Found a match, no need to check other auto-links
        except Exception as e:
            print(f"Error reading story index for {story_id}: {e}")
    
    return matching_stories

# === HELPER: Generate story table ===
def generate_story_table(stories):
    """Generate an HTML table of stories."""
    if not stories:
        return '<table>\n  <thead>\n    <tr>\n      <th>Stories</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td><em>No stories found featuring this character</em></td>\n    </tr>\n  </tbody>\n</table>'
    
    # Create the HTML table
    html = '<table>\n  <thead>\n    <tr>\n      <th>Stories</th>\n    </tr>\n  </thead>\n  <tbody>'
    
    # Add each story as a row
    for story_name, story_path in sorted(stories):  # Sort stories alphabetically
        html += f'\n    <tr>\n      <td><a href="{story_path}">{story_name}</a></td>\n    </tr>'
    
    # Close the table
    html += '\n  </tbody>\n</table>'
    
    return html

# === MAIN FUNCTION ===
def main():
    print("🔍 Starting insert_story_tables.py")
    print(f"Looking for marker: {STORY_TABLE_MARKER}")
    
    # Load stories data
    stories_data = load_json_data(STORIES_JSON_PATH)
    if not stories_data:
        print("❌ Failed to load stories data.")
        return
    
    # Get all JSON data files
    json_files = [f for f in JSON_DIR.glob("*.json") if f.name != "stories_data.json"]
    
    # Track statistics
    total_entities = 0
    updated_entities = 0
    
    # Process each JSON file
    for json_file in json_files:
        file_name = json_file.name
        print(f"Processing {file_name}...")
        
        # Load the JSON data
        try:
            data = load_json_data(json_file)
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
            continue
        
        # Get the base path from the config
        base_path = data.get("config", {}).get("base_path", "")
        if not base_path:
            print(f"⚠️ No base path found in {json_file}")
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
            
            # Check if file contains the marker or an existing stories table
            try:
                content = entity_path.read_text(encoding='utf-8')
                
                # Check for marker or existing table
                has_marker = STORY_TABLE_MARKER in content
                has_existing_table = '<table>' in content and '<th>Stories</th>' in content
                
                if not (has_marker or has_existing_table):
                    continue
                
                # Find stories for this entity
                stories = find_stories_for_entity(auto_links, stories_data)
                
                # Generate the story table
                story_table = generate_story_table(stories)
                
                updated_content = content
                
                # Replace the marker if it exists
                if has_marker:
                    updated_content = updated_content.replace(STORY_TABLE_MARKER, story_table)
                
                # Replace existing table if it exists
                if has_existing_table and not has_marker:
                    # Find and replace the existing table
                    table_start = updated_content.find('<table>')
                    table_end = updated_content.find('</table>', table_start) + 8  # +8 to include '</table>'
                    
                    if table_start >= 0 and table_end > table_start:
                        existing_table = updated_content[table_start:table_end]
                        # Only replace if it's a stories table
                        if '<th>Stories</th>' in existing_table:
                            updated_content = updated_content.replace(existing_table, story_table)
                
                # Write the updated content back to the file
                entity_path.write_text(updated_content, encoding='utf-8')
                
                updated_entities += 1
                updated_count += 1
                print(f"  ✅ Updated {item_id} with {len(stories)} stories")
            except Exception as e:
                print(f"  ❌ Error processing {item_id}: {e}")
        
        print(f"  Updated {updated_count} of {entity_count} entities in {file_name}")
    
    print(f"\n✅ Summary: Updated {updated_entities} out of {total_entities} entities.")
    print("Finished insert_story_tables.py")

if __name__ == "__main__":
    main()