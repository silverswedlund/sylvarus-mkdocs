# a script to sort the items in a json file by the key

import json
import os
from pathlib import Path

# Files to skip (don't sort these)
SKIP_FILES = [
    # Add filenames here to skip them
    # Example: "special_order.json"
]

def sort_json_file(file_path):
    """
    Reads a JSON file, sorts the items alphabetically, and writes back to the file.
    Returns True if file was processed, False if skipped.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check if file has 'items' field
        if 'items' not in data:
            print(f"Skipping {file_path} - no 'items' field found")
            return False
            
        # Sort the items
        sorted_items = dict(sorted(data['items'].items()))
        data['items'] = sorted_items
        
        # Write back to file with consistent formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Sorted {file_path}")
        return True
        
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    # Get the directory containing the script
    script_dir = Path(__file__).parent.parent
    json_dir = script_dir / '_json'
    
    if not json_dir.exists():
        print(f"Error: {json_dir} directory not found")
        return
        
    processed_count = 0
    skipped_count = 0
    
    # Process all JSON files in the directory
    for file_path in json_dir.glob('*.json'):
        if file_path.name in SKIP_FILES:
            print(f"Skipping {file_path.name} (in skip list)")
            skipped_count += 1
            continue
            
        if sort_json_file(file_path):
            processed_count += 1
        else:
            skipped_count += 1
    
    print(f"\nComplete! Processed {processed_count} files, skipped {skipped_count} files")

if __name__ == "__main__":
    main()

