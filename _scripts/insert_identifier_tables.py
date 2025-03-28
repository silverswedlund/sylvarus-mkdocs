import json
import os
import re
from pathlib import Path

# === CONFIGURABLE EXCEPTIONS ===
EXCLUDED_PATHS = [
    "docs/identifiers",  # Don't search identifier pages themselves
    # Add more full paths to exclude as needed, e.g.:
    # "docs/templates",
    # "docs/system", 
]

# === PATHS ===
base_docs = Path("docs")
identifier_json_path = Path("_json/identifiers_data.json")
identifiers_base_path = base_docs / "identifiers"

# === LOAD IDENTIFIERS FROM JSON ===
with open(identifier_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
identifiers = data.get("items", {})

# === HELPER: Extract title from index.md (fallback to folder name) ===
def extract_title(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    return match.group(1).strip() if match else path.parent.name

# === HELPER: Check if path should be excluded ===
def should_exclude(path: Path) -> bool:
    path_str = str(path)
    return any(excl in path_str for excl in EXCLUDED_PATHS)

# === PROCESS EACH IDENTIFIER ===
for identifier_key, info in identifiers.items():
    identifier_name = info["name"]
    identifier_dir = identifiers_base_path / identifier_name.lower()
    identifier_index = identifier_dir / "index.md"
    if not identifier_index.exists():
        continue

    matches = []

    # Search ALL index.md files in docs directory
    for index_file in base_docs.rglob("index.md"):
        if should_exclude(index_file):
            continue
            
        try:
            content = index_file.read_text(encoding="utf-8").lower()
            if identifier_name.lower() in content:
                print(f"Found match in: {index_file}")
                title = extract_title(index_file)
                rel_path = os.path.relpath(index_file, identifier_dir)
                matches.append(f"| [{title}]({rel_path}) |")
        except Exception as e:
            print(f"Error processing {index_file}: {e}")

    # Build markdown table (single column)
    table = ["| Related Pages |", "|----------------|"] + matches if matches else ["| Related Pages |", "|----------------|", "| _No references found_ |"]
    table_md = "\n".join(table)

    # Insert table into identifier index
    index_text = identifier_index.read_text(encoding="utf-8")
    updated_text = index_text.replace("|people_table|", table_md)
    identifier_index.write_text(updated_text, encoding="utf-8")

print("✅ Identifier index files updated with linked references.")
