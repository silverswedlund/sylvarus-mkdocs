
#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

def normalize_name(name):
    return name.lower().replace("'", "").replace(" ", "")

def load_all_json_items(json_dir):
    """Load all items from all JSON files, collecting both link targets and all index paths."""
    link_targets = []
    all_index_paths = []

    json_files = Path(json_dir).glob("*.json")
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        config = data.get("config", {})
        base_path = config.get("base_path")
        if not base_path:
            continue
        items = data.get("items", {})

        for key, item in items.items():
            name = item.get("name")
            folder_name = normalize_name(key)
            index_path = (Path(base_path) / folder_name / "index.md").resolve()

            # Track all index files to scan
            all_index_paths.append(index_path)

            # Track items that define auto_link_strings as link targets
            auto_links = item.get("auto_link_strings", [])
            if name and auto_links:
                link_targets.append({
                    "name": name,
                    "index_path": index_path,
                    "auto_link_strings": auto_links
                })

    return link_targets, all_index_paths

def linkify(content, string, link, added_links):
    """Replace unlinked occurrences of a string with a Markdown link (case-insensitive)."""
    escaped = re.escape(string)
    pattern = r'(?<!\[)(' + escaped + r')(?![^\]]*\))'

    def replacer(match):
        matched_text = match.group(1)
        added_links.append((matched_text, link))
        return f"[{matched_text}]({link})"

    return re.sub(pattern, replacer, content, flags=re.IGNORECASE)

def process_autolinks(link_targets, all_index_paths):
    """For each index.md file, attempt to link to any known targets by alias."""
    for index_path in all_index_paths:
        if not index_path.exists():
            continue

        try:
            content = index_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ Failed to read {index_path}: {e}")
            continue

        original_content = content
        added_links = []

        for target in link_targets:
            target_path = target["index_path"]
            if index_path.resolve() == target_path.resolve():
                continue  # Don't link to self

            for alias in target["auto_link_strings"]:
                rel_link = os.path.relpath(target_path, start=index_path.parent)
                content = linkify(content, alias, rel_link, added_links)

        if content != original_content:
            try:
                index_path.write_text(content, encoding="utf-8")
                print(f"✅ Linked {len(added_links)} term(s) in {index_path}")
                for text, link in added_links:
                    print(f"   → Linked '{text}' → [{text}]({link})")
            except Exception as e:
                print(f"❌ Failed to write updated content to {index_path}: {e}")

if __name__ == "__main__":
    json_dir = "_json"
    link_targets, all_index_paths = load_all_json_items(json_dir)
    process_autolinks(link_targets, all_index_paths)
    print("✅ Auto-linking complete.")
