#!/usr/bin/env python3
import os
import json
import subprocess
import argparse
import glob
import shutil
import pickle

PICKLE_DIR = "_scripts/pickles"

def normalize_name(name):
    """Normalize folder names by lowercasing and removing spaces and apostrophes."""
    return name.lower().replace("'", "").replace(" ", "")

def ensure_directory_and_template(base_path, template_path, folder_name):
    """
    Ensure that the destination folder exists and that an index.md is created.
    If a template file is provided, copy it to index.md; otherwise, create a blank file.
    """
    full_path = os.path.join(base_path, folder_name)
    index_path = os.path.join(full_path, "index.md")
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        print(f"📁 Created folder: {full_path}")
    if template_path and os.path.exists(template_path):
        try:
            shutil.copy(template_path, index_path)
            print(f"📄 Overwrote template to: {index_path}")
        except Exception as e:
            print(f"❌ Error copying template: {e}")
    else:
        if not os.path.exists(index_path):
            try:
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write("")
                print(f"📄 Created blank index.md: {index_path}")
            except Exception as e:
                print(f"❌ Error creating blank index.md: {e}")
    return index_path

def load_pickle(pickle_path):
    """Load the pickle file if it exists; otherwise, return an empty dict."""
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"❌ Error loading pickle file {pickle_path}: {e}")
    return {}

def save_pickle(pickle_path, data):
    """Save data to the pickle file, ensuring the containing directory exists."""
    os.makedirs(os.path.dirname(pickle_path), exist_ok=True)
    try:
        with open(pickle_path, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"❌ Error saving pickle file {pickle_path}: {e}")

def has_git_changes(path):
    """
    Check if there are any uncommitted changes in the given directory using git status.
    If the directory doesn't exist, we treat that as a change.
    """
    if not os.path.exists(path):
        return True
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", path],
            capture_output=True, text=True, check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"❌ Git status error in {path}: {e}")
        # Conservatively assume there are changes if git fails.
        return True

def run_template_fill(json_file, json_data, replace_script):
    """
    Process each item in the JSON file conditionally:
      - If the global config or template has changed, process all items.
      - Otherwise, process only the items that have been updated (or whose destination folder shows changes).
    Update the pickle file with the new state afterward.
    """
    config = json_data.get("config", {})
    base_path = config.get("base_path")
    template_file = config.get("template")
    items = json_data.get("items", {})

    if not base_path:
        print("❌ Missing 'base_path' in config.")
        return

    # Prepare pickle file path for this JSON file
    json_filename = os.path.basename(json_file)
    pickle_path = os.path.join(PICKLE_DIR, f"{json_filename}.pkl")

    # Read current template text (if provided)
    current_template_text = ""
    if template_file and os.path.exists(template_file):
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                current_template_text = f.read()
        except Exception as e:
            print(f"❌ Error reading template file {template_file}: {e}")

    # Load previous state from pickle
    previous_data = load_pickle(pickle_path)
    previous_config = previous_data.get("config", {})
    previous_template_text = previous_data.get("template_text", "")
    previous_items = previous_data.get("items", {})

    # Determine if global changes occurred (config or template changed)
    config_changed = previous_config != config
    template_changed = previous_template_text != current_template_text
    global_change = config_changed or template_changed

    # Prepare a new dictionary to store the state of items for later
    new_items_state = {}

    # Collect all keys across all items to ensure uniform arguments
    all_keys = set()
    for fields in items.values():
        all_keys.update(fields.keys())

    for entry_name, fields in items.items():
        folder_name = normalize_name(entry_name)
        # Serialize the item data for comparison
        serialized_item = json.dumps(fields, sort_keys=True)
        new_items_state[folder_name] = serialized_item

        # Check if this specific item has changed
        item_changed = (previous_items.get(folder_name) != serialized_item)

        # Determine the destination folder for this item
        index_path = os.path.join(base_path, folder_name, "index.md")
        dest_folder = os.path.dirname(index_path)
        folder_has_changes = has_git_changes(dest_folder)

        if global_change or item_changed or folder_has_changes:
            # Create or update the destination folder and index.md
            file_path = ensure_directory_and_template(base_path, template_file, folder_name)
            args = [file_path]
            for key in sorted(all_keys):
                value = fields.get(key, "")
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                args.extend([key, value])
            print(f"✏️ Running template fill for '{entry_name}' in {file_path}")
            try:
                subprocess.run(["python3", replace_script, *args], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running replace script for '{entry_name}': {e}")
        else:
            print(f"Skipping '{entry_name}': no changes detected.")

    # Update the pickle file with the new state
    new_state = {
        "config": config,
        "template_text": current_template_text,
        "items": new_items_state
    }
    save_pickle(pickle_path, new_state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic template filler for MkDocs content")
    parser.add_argument("--json_dir", default="_json", help="Directory containing all JSON data files")
    parser.add_argument("--script", default="_scripts/replace_templates.py", help="Path to the replace_templates.py script")
    args = parser.parse_args()
    json_files = glob.glob(os.path.join(args.json_dir, "*.json"))

    if not json_files:
        print("No JSON files found in the specified directory.")
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"❌ Error processing JSON file {json_file}: {e}")
            continue
        run_template_fill(json_file, json_data, args.script)
