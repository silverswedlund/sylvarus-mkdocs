import json
import os
import re
from pathlib import Path

# === PATHS ===
base_docs = Path("")
stories_json_path = Path("_json/stories_data.json")

def process_stories():
    print("Processing stories...")
    
    # Load stories data from JSON
    with open(stories_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Get base path from config
    stories_base_path = base_docs / data.get("config", {}).get("base_path", "stories").lstrip("/")
    print(f"Stories base path: {stories_base_path}")
    
    stories = data.get("items", {})
    
    # Process each story
    for story_key, info in stories.items():
        story_name = info["name"]
        story_path = info.get("story_path", "")
        
        if not story_path:
            print(f"Warning: No story_path defined for {story_name}")
            continue
        
        # Find the generated story file - handle both direct files and directories with index.md
        story_file_path = stories_base_path / f"{story_key}.md"
        story_index_path = stories_base_path / story_key / "index.md"
        
        if story_file_path.exists():
            target_file = story_file_path
        elif story_index_path.exists():
            target_file = story_index_path
        else:
            print(f"Warning: Generated story file not found at {story_file_path} or {story_index_path}")
            continue
        
        # Handle both absolute and relative paths for story source
        if os.path.isabs(story_path):
            story_source_path = Path(story_path)
        else:
            # Check if the path is relative to the story directory
            story_dir_source = stories_base_path / story_key / story_path
            if story_dir_source.exists():
                story_source_path = story_dir_source
            else:
                # Try relative to project root
                story_source_path = Path(story_path)
        
        if not story_source_path.exists():
            print(f"Error: Story source file not found at {story_source_path}")
            continue
            
        try:
            # Read the story content
            story_content = story_source_path.read_text(encoding="utf-8")
            
            # Read the generated story file
            story_file_content = target_file.read_text(encoding="utf-8")
            
            # Replace the placeholder with the actual story content
            updated_content = story_file_content.replace("|story_placeholder|", story_content)
            
            # Write the updated content back to the file
            target_file.write_text(updated_content, encoding="utf-8")
            
            print(f"✅ Updated story content for: {story_name} ({target_file})")
            
        except Exception as e:
            print(f"Error processing story {story_name}: {e}")
    
    print("✅ Story content insertion complete.")

if __name__ == "__main__":
    process_stories()
