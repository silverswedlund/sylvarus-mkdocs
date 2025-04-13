from pathlib import Path
import os
import yaml

MKDOCS_FILE = "mkdocs.yml"
DOCS_DIR = "docs"

def is_leaf_dir(path):
    return not any(os.path.isdir(os.path.join(path, d)) for d in os.listdir(path))

def get_valid_md_files(files):
    return [f for f in files if f.endswith(".md") and not f.endswith(".md_insert")]

def get_nav_paths(base_dir):
    nav_entries = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        valid_mds = get_valid_md_files(files)
        if not valid_mds:
            continue

        full_root = os.path.abspath(root)
        rel_root = os.path.relpath(full_root, base_dir)
        parts = rel_root.split(os.sep) if rel_root != '.' else []

        is_leaf = is_leaf_dir(full_root)

        if is_leaf and "index.md" in valid_mds:
            rel_path = os.path.join(rel_root, "index.md").replace("\\", "/")
            label = parts[-1].replace("_", " ").capitalize() if parts else "Home"
            nav_entries.append((parts[:-1], label, rel_path, False))
        else:
            for f in sorted(valid_mds):
                rel_path = os.path.join(rel_root, f).replace("\\", "/")
                is_disambig = f.endswith("disambiguation.md")
                label = None if is_disambig else os.path.splitext(f)[0].replace("_", " ").capitalize()
                nav_entries.append((parts, label, rel_path, is_disambig))
    return nav_entries

def build_nav_structure(entries):
    nav = {}
    for parts, label, path, is_disambig in entries:
        current_level = nav
        for part in parts:
            name = part.replace("_", " ").capitalize()
            if name not in current_level:
                current_level[name] = {}
            current_level = current_level[name]
        if is_disambig:
            # Change the label for disambiguation files to "sylvarus"
            current_level.setdefault("Sylvarus", []).append(path)
        else:
            current_level[label] = path
    return nav

def convert_nav_dict_to_list(nav_dict):
    nav_list = []
    for key, value in sorted(nav_dict.items()):
        if isinstance(value, dict):
            sublist = []
            if "Sylvarus" in value:
                sublist.extend(value["Sylvarus"])
                del value["Sylvarus"]
            sublist.extend(convert_nav_dict_to_list(value))
            nav_list.append({key: sublist})
        else:
            nav_list.append({key: value})
    return nav_list

def update_mkdocs_nav(nav_data):
    if not os.path.exists(MKDOCS_FILE):
        raise FileNotFoundError(f"❌ Could not find {MKDOCS_FILE}")

    with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config['nav'] = nav_data

    with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)

def main():
    nav_paths = get_nav_paths(DOCS_DIR)
    nav_structure = build_nav_structure(nav_paths)
    nav_list = convert_nav_dict_to_list(nav_structure)
    update_mkdocs_nav(nav_list)
    print("✅ mkdocs.yml nav updated successfully.")

main()
