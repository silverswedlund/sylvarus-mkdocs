
#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

# 🔧 Add any extra markdown files you want processed here
ADDITIONAL_MD_FILES = [
    "docs/articles_of_olympus/pact_of_olympus.md",
]
def normalize_name(name):
    return name.lower().replace("'", "").replace(" ", "")

def load_all_json_items(json_dir):
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

            all_index_paths.append(index_path)

            auto_links = item.get("auto_link_strings", [])
            if name and auto_links:
                link_targets.append({
                    "name": name,
                    "index_path": index_path,
                    "auto_link_strings": auto_links
                })

    return link_targets, all_index_paths

def linkify_safely(content, string, link, added_links):
    """Replace strings surrounded by whitespace, ignoring already-linked or special cases."""
    escaped = re.escape(string)
    pattern = re.compile(rf'(\s|,)({escaped})(\s|,)', flags=re.IGNORECASE)

    def safe_replacer(match):
        added_links.append((match.group(0), link))
        return f"{match.group(1)}[{match.group(2).strip()}]({link}){match.group(3)}"

    return pattern.sub(safe_replacer, content)

def process_autolinks(link_targets, all_index_paths):
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
                continue

            for alias in target["auto_link_strings"]:
                rel_link = os.path.relpath(target_path, start=index_path.parent)
                content = linkify_safely(content, alias, rel_link, added_links)

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

    # 🔁 Include additional markdown files from the constant list
    additional_paths = [Path(p).resolve() for p in ADDITIONAL_MD_FILES]
    all_index_paths.extend(additional_paths)

    # 🧹 Deduplicate just in case
    all_index_paths = list(set(all_index_paths))

    process_autolinks(link_targets, all_index_paths)
    print("✅ Auto-linking complete.")
