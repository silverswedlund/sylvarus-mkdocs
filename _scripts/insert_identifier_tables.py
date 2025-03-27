import json
import os
import re
from pathlib import Path

# === CONFIGURABLE LIST OF DIRECTORIES TO SEARCH ===
search_dirs = ["gods", "demigods"]  # Add more like "immortals" if needed

# === PATHS ===
base_docs = Path("docs")
search_paths = [base_docs / d for d in search_dirs]
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

# === PROCESS EACH IDENTIFIER ===
for identifier_key, info in identifiers.items():
    identifier_name = info["name"]
    identifier_dir = identifiers_base_path / identifier_name.lower()
    identifier_index = identifier_dir / "index.md"
    if not identifier_index.exists():
        continue

    matches = []

    # Search for identifier name in content of other index.md files
    for search_path in search_paths:
        for index_file in search_path.rglob("index.md"):
            content = index_file.read_text(encoding="utf-8").lower()
            if identifier_name in content:
                print("replacing!", search_path, index_file)
                title = extract_title(index_file)
                rel_path = os.path.relpath(index_file, identifier_dir)
                matches.append(f"| [{title}]({rel_path}) |")

    # Build markdown table (single column)
    table = ["| Related Pages |", "|----------------|"] + matches if matches else ["| Related Pages |", "|----------------|", "| _No references found_ |"]
    table_md = "\n".join(table)

    # Insert table into identifier index
    index_text = identifier_index.read_text(encoding="utf-8")
    updated_text = index_text.replace("|people_table|", table_md)
    identifier_index.write_text(updated_text, encoding="utf-8")

print("✅ Identifier index files updated with linked references.")
