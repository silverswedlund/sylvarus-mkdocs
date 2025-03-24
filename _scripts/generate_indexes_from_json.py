
import os
import json
import subprocess
import argparse
import glob
import shutil

def normalize_name(name):
    return name.lower().replace("'", "").replace(" ", "")

def ensure_directory_and_template(base_path, template_path, folder_name):
    full_path = os.path.join(base_path, folder_name)
    index_path = os.path.join(full_path, "index.md")
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        print(f"📁 Created folder: {full_path}")
    if template_path and os.path.exists(template_path):
        shutil.copy(template_path, index_path)
        print(f"📄 Overwrote template to: {index_path}")
    else:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("")
        print(f"📄 Created blank index.md: {index_path}")
    return index_path

def run_template_fill(json_data, replace_script):
    config = json_data.get("config", {})
    base_path = config.get("base_path")
    template_file = config.get("template")
    items = json_data.get("items", {})

    if not base_path:
        print("❌ Missing 'base_path' in config.")
        return

    all_keys = set()
    for fields in items.values():
        all_keys.update(fields.keys())

    for entry_name, fields in items.items():
        folder_name = normalize_name(entry_name)
        file_path = ensure_directory_and_template(base_path, template_file, folder_name)
        args = [file_path]
        for key in sorted(all_keys):
            value = fields.get(key, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            args.extend([key, value])
        subprocess.run(["python3", replace_script, *args])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic template filler for MkDocs content")
    parser.add_argument("--json_dir", default="_json", help="Directory containing all JSON data files")
    parser.add_argument("--script", default="_scripts/replace_templates.py", help="Path to the replace_templates.py script")
    args = parser.parse_args()
    json_files = glob.glob(os.path.join(args.json_dir, "*.json"))
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        run_template_fill(json_data, args.script)
