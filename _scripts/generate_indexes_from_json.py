import os
import json
import subprocess
import argparse
import glob
import shutil

def normalize_name(name):
    """Sanitize folder names: lowercase, no apostrophes or spaces."""
    return name.lower().replace("'", "").replace(" ", "")

def ensure_directory_and_template(base_path, template_path, folder_name):
    """Ensure the folder exists and always overwrite index.md from template or blank."""
    full_path = os.path.join(base_path, folder_name)
    index_path = os.path.join(full_path, "index.md")

    if not os.path.exists(full_path):
        os.makedirs(full_path)
        print(f"📁 Created folder: {full_path}")

    # Always overwrite index.md
    if template_path and os.path.exists(template_path):
        shutil.copy(template_path, index_path)
        print(f"📄 Overwrote template to: {index_path}")
    else:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("")
        print(f"📄 Overwrote blank index.md: {index_path}")

    return index_path

def run_template_fill(json_data, replace_script):
    config = json_data.get("config", {})
    base_path = config.get("base_path")
    template_file = config.get("template")
    items = json_data.get("items", {})

    if not base_path:
        print("❌ Missing 'base_path' in config.")
        return

    for entry_name, fields in items.items():
        folder_name = normalize_name(entry_name)
        file_path = ensure_directory_and_template(base_path, template_file, folder_name)

        args = [file_path]
        for key, value in fields.items():
            args.extend([key, value])

        result = subprocess.run(["python3", replace_script] + args)

        if result.returncode == 0:
            print(f"✅ Updated: {entry_name}")
        else:
            print(f"⚠️  Error updating {entry_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic template filler for MkDocs content")
    parser.add_argument("--json_dir", default="_json", help="Directory containing all JSON data files")
    parser.add_argument("--script", default="_scripts/replace_templates.py", help="Path to the replace_templates.py script")

    args = parser.parse_args()

    json_files = glob.glob(os.path.join(args.json_dir, "*.json"))

    if not json_files:
        print(f"❌ No JSON files found in {args.json_dir}")
        exit(1)

    for json_file in json_files:
        print(f"\n📦 Processing: {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        run_template_fill(json_data, args.script)

    print("\n🎉 Finished filling all templates.")
