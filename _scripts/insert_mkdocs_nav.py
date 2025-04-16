#!/usr/bin/env python3
"""
Script to generate navigation structure for mkdocs.yml
"""

import os
import yaml
from pathlib import Path

MKDOCS_FILE = "mkdocs.yml"
DOCS_DIR = "docs"

def is_leaf_dir(path):
    """Check if a directory is a leaf directory (has no subdirectories)."""
    return not any(os.path.isdir(os.path.join(path, d)) for d in os.listdir(path))

def get_valid_md_files(files):
    """Get valid markdown files (excluding .md_insert files)."""
    return [f for f in files if f.endswith(".md") and not f.endswith(".md_insert")]

def get_nav_paths(base_dir):
    """Get all navigation paths from the docs directory."""
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

        # Process disambiguation pages first - make sure we're finding them correctly
        disambig_files = [f for f in valid_mds if "_disambiguation.md" in f]
        for f in disambig_files:
            rel_path = os.path.join(rel_root, f).replace("\\", "/")
            print(f"Found disambiguation page: {rel_path}")  # Debug print
            nav_entries.append((parts, "Overview", rel_path, True))
            
        # Then process index files for leaf directories
        if is_leaf and "index.md" in valid_mds:
            rel_path = os.path.join(rel_root, "index.md").replace("\\", "/")
            label = parts[-1].replace("_", " ").title() if parts else "Home"
            nav_entries.append((parts[:-1], label, rel_path, False))
        
        # Finally process other markdown files
        other_files = [f for f in valid_mds if "_disambiguation.md" not in f and f != "index.md"]
        for f in sorted(other_files):
            rel_path = os.path.join(rel_root, f).replace("\\", "/")
            label = os.path.splitext(f)[0].replace("_", " ").title()
            nav_entries.append((parts, label, rel_path, False))
    
    # Debug print to see all entries        
    for parts, label, path, is_disambig in nav_entries:
        if is_disambig:
            print(f"Nav entry: {'/'.join(parts)}, {label}, {path}, {is_disambig}")
            
    return nav_entries

def build_nav_structure(entries):
    """Build the navigation structure from the entries."""
    nav = {}
    for parts, label, path, is_disambig in entries:
        current_level = nav
        for i, part in enumerate(parts):
            name = part.replace("_", " ").title()
            
            if not isinstance(current_level, dict):
                print(f"Warning: Cannot add {path} to nav structure - encountered non-dictionary at {'.'.join(parts[:i])}")
                break
                
            if name not in current_level:
                current_level[name] = {}
            current_level = current_level[name]
        
        else:  # This else belongs to the for loop, executes when no break occurs
            if isinstance(current_level, dict):
                if is_disambig:
                    current_level[label] = path
                else:
                    current_level[label] = path
            else:
                print(f"Warning: Cannot add {path} to nav structure - parent is not a dictionary")
    
    return nav

def convert_nav_dict_to_list(nav_dict):
    """Convert the navigation dictionary to a list format for mkdocs."""
    nav_list = []
    for key, value in sorted(nav_dict.items()):
        if isinstance(value, dict):
            # Check if "Overview" is in the dictionary and move it to the top
            overview_path = None
            if "Overview" in value:
                overview_path = value["Overview"]
                del value["Overview"]
            
            # Convert the rest of the dictionary
            sublist = convert_nav_dict_to_list(value)
            
            # If we have an overview, add it to the beginning
            if overview_path:
                sublist.insert(0, {"Overview": overview_path})
                
            nav_list.append({key: sublist})
        else:
            nav_list.append({key: value})
    return nav_list

def update_mkdocs_nav(nav_data):
    """Update the mkdocs.yml file with the new navigation structure."""
    if not os.path.exists(MKDOCS_FILE):
        raise FileNotFoundError(f"❌ Could not find {MKDOCS_FILE}")

    with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config['nav'] = nav_data

    with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)

def main():
    """Main function to update the mkdocs navigation."""
    nav_paths = get_nav_paths(DOCS_DIR)
    nav_structure = build_nav_structure(nav_paths)
    nav_list = convert_nav_dict_to_list(nav_structure)
    update_mkdocs_nav(nav_list)
    print("✅ mkdocs.yml nav updated successfully.")

if __name__ == "__main__":
    main()