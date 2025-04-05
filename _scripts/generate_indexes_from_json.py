#!/usr/bin/env python3
import os
import json
import subprocess
import argparse
import glob
import shutil
import pickle
import re
import tempfile

PICKLE_DIR = "_scripts/pickles"
PICKLE_EXCLUDED_JSON_FILES = ["identifiers_data.json"]  # JSON files to exclude from pickle tracking

def normalize_name(name):
    return name.lower().replace("'", "").replace(" ", "")

def ensure_directory_and_template(base_path, template_path, folder_name):
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
    if os.path.exists(pickle_path):
        try:
            with open(pickle_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"❌ Error loading pickle file {pickle_path}: {e}")
    return {}

def save_pickle(pickle_path, data):
    os.makedirs(os.path.dirname(pickle_path), exist_ok=True)
    try:
        with open(pickle_path, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"❌ Error saving pickle file {pickle_path}: {e}")

def has_git_changes(path):
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
        return True

def protect_jinja_includes(file_path):
    """Encode Jinja includes with special markers"""
    if not os.path.exists(file_path):
        return file_path, False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all {% include ... %} patterns
    include_pattern = r'{%\s*include\s+(.*?)\s*%}'
    
    # Check if there are any includes to process
    if not re.search(include_pattern, content):
        return file_path, False
    
    # Replace includes with markers
    modified_content = re.sub(
        include_pattern,
        r"|include_prefix|\1|include_postfix|",
        content
    )
    
    # Create a temporary file with encoded includes
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
    temp_path = temp_file.name
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    return temp_path, True

def restore_jinja_includes(file_path):
    """Restore Jinja includes from markers"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace markers with original Jinja syntax
    modified_content = content.replace("|include_prefix|", "{% include ").replace("|include_postfix|", " %}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

def run_template_fill(json_file, json_data, replace_script):
    config = json_data.get("config", {})
    base_path = config.get("base_path")
    if(not config.get("template")):
        print("🌕 Missing 'template' in config - skipping")
        return
    template_file = config.get("template")
    items = json_data.get("items", {})

    if not base_path:
        print("❌ Missing 'base_path' in config.")
        return

    json_filename = os.path.basename(json_file)
    pickle_path = os.path.join(PICKLE_DIR, f"{json_filename}.pkl")
    exclude_from_pickle = json_filename in PICKLE_EXCLUDED_JSON_FILES

    current_template_text = ""
    if template_file and os.path.exists(template_file):
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                current_template_text = f.read()
        except Exception as e:
            print(f"❌ Error reading template file {template_file}: {e}")

    previous_data = load_pickle(pickle_path) if not exclude_from_pickle else {}
    previous_config = previous_data.get("config", {})
    previous_template_text = previous_data.get("template_text", "")
    previous_items = previous_data.get("items", {})

    config_changed = previous_config != config
    template_changed = previous_template_text != current_template_text
    global_change = config_changed or template_changed

    new_items_state = {}

    all_keys = set()
    for fields in items.values():
        all_keys.update(fields.keys())

    for entry_name, fields in items.items():
        folder_name = normalize_name(entry_name)
        serialized_item = json.dumps(fields, sort_keys=True)
        new_items_state[folder_name] = serialized_item

        item_changed = (previous_items.get(folder_name) != serialized_item)

        index_path = os.path.join(base_path, folder_name, "index.md")
        dest_folder = os.path.dirname(index_path)
        folder_has_changes = has_git_changes(dest_folder)

        if global_change or item_changed or folder_has_changes:
            file_path = ensure_directory_and_template(base_path, template_file, folder_name)
            
            # Protect Jinja includes before processing
            temp_file, has_includes = protect_jinja_includes(file_path)
            
            args = [temp_file]
            for key in sorted(all_keys):
                value = fields.get(key, "")
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                args.extend([key, value])
            print(f"✏️ Running template fill for '{entry_name}' in {file_path}")
            try:
                subprocess.run(["python3", replace_script, *args], check=True)
                
                # If we used a temp file, copy it back to the original
                if temp_file != file_path:
                    shutil.copy(temp_file, file_path)
                    os.unlink(temp_file)
                
                # Restore Jinja includes if needed
                if has_includes:
                    restore_jinja_includes(file_path)
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running replace script for '{entry_name}': {e}")
                # Clean up temp file if there was an error
                if temp_file != file_path and os.path.exists(temp_file):
                    os.unlink(temp_file)
        else:
            print(f"Skipping '{entry_name}': no changes detected.")

    if not exclude_from_pickle:
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
    
    # Find all JSON files recursively in the json directory
    json_files = []
    for root, _, files in os.walk(args.json_dir):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))

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
