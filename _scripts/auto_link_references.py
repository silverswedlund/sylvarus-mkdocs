#!/usr/bin/env python3
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, List

# Logging setup
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Directories
JSON_DIR = Path("_json")
DOCS_DIR = Path("docs")

def load_all_json(json_dir: Path) -> List[Dict]:
    data = []
    for json_file in json_dir.rglob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            data.append(content)
        except Exception as e:
            logging.warning(f"Failed to load {json_file}: {e}")
    return data

def build_link_map(data: List[Dict]) -> Dict[str, Tuple[str, Path]]:
    link_map = {}
    for content in data:
        category = content.get("config", {}).get("subtype") or content.get("config", {}).get("base_path", "").split("/")[-1]
        base_path = Path(content.get("config", {}).get("base_path", f"docs/{category}"))
        for item_key, item in content.get("items", {}).items():
            clean_key = item_key.lower().replace(" ", "").replace("'", "")
            file_name = f"{clean_key}.md"
            for raw in item.get("auto_link_strings", []):
                search = raw  # Use the full string as the key
                if search in link_map:
                    old_path = link_map[search][1]
                    logging.warning(f"Duplicate term '{search}' in {base_path}/{file_name} (previous: {old_path})")
                link_map[search] = (search, base_path / file_name)
    return link_map

def find_markdown_files(docs_dir: Path, include_md_insert: bool = True) -> List[Path]:
    patterns = ["**/*.md"]
    if include_md_insert:
        patterns.append("**/*.md_insert")
    files = []
    for pattern in patterns:
        files.extend(docs_dir.rglob(pattern))
    return files

def strip_existing_links(content: str) -> str:
    return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

def replace_terms_in_markdown(file_path: Path, link_map: Dict[str, Tuple[str, Path]]):
    content = file_path.read_text(encoding="utf-8")
    
    # Strip existing links
    content = strip_existing_links(content)

    def replacement(match):
        prefix = match.group(1)  # Capture the prefix
        word = match.group(2)    # Capture the word
        if word not in link_map:
            return match.group(0)  # Return the original match if no link is found
        
        # Remove the suffix after linking
        base_word = word.split("^", 1)[0]
        display, target_path = link_map[word]
        relative_path = os.path.relpath(target_path, start=file_path.parent).replace("\\", "/")
        return f"{prefix}[{base_word}]({relative_path})"

    # Create a pattern to match all terms in the link_map with specific boundaries
    pattern = r'(\s|^|")(' + "|".join(re.escape(k) for k in sorted(link_map, key=len, reverse=True)) + r')(?=\s|$|,)'
    
    # Replace terms in the content
    content_new = re.sub(pattern, replacement, content)

    # Write back to the file if changes were made
    if content_new != content:
        file_path.write_text(content_new, encoding="utf-8")
        logging.info(f"Rewritten: {file_path}")

if __name__ == "__main__":
    print("Starting auto-link reference script...")
    json_data = load_all_json(JSON_DIR)
    term_map = build_link_map(json_data)
    md_files = find_markdown_files(DOCS_DIR)
    for md_file in md_files:
        replace_terms_in_markdown(md_file, term_map)
