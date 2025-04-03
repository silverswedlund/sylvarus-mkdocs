import json
import logging
from pathlib import Path
import sys
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_json_data(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load data from {json_path}: {e}")
        sys.exit(1)

def construct_members_table(pantheon_name, gods_data):
    members = [
        god['name'] for god in gods_data['items'].values()
        if god.get('pantheon') == pantheon_name
    ]
    if not members:
        return "| Members |\n|---------|\n| _No members found_ |"
    
    table_header = "| Members |\n|---------|"
    table_rows = [f"| {member}^god |" for member in members]
    return "\n".join([table_header] + table_rows)

def construct_pantheon_table(pantheons_data):
    table_header = "| Pantheons |\n|-----------|"
    table_rows = [
        f"| {pantheon['name']} |"
        for pantheon in pantheons_data['items'].values()
    ]
    return "\n".join([table_header] + table_rows)

def update_pantheon_index(pantheon_name, pantheon_dir, gods_data):
    index_path = pantheon_dir / "index.md"
    if not index_path.exists():
        logging.warning(f"Index file not found for {pantheon_name}")
        return

    try:
        content = index_path.read_text(encoding="utf-8")
        members_table = construct_members_table(pantheon_name, gods_data)
        updated_content = re.sub(r"\|members_table\|", members_table, content)
        index_path.write_text(updated_content, encoding="utf-8")
        logging.info(f"Updated members table for {pantheon_name}")
    except Exception as e:
        logging.error(f"Failed to update {index_path}: {e}")

def update_pantheon_disambiguation(pantheon_disambiguation_path, pantheons_data):
    try:
        content = pantheon_disambiguation_path.read_text(encoding="utf-8")
        pantheon_table = construct_pantheon_table(pantheons_data)
        updated_content = re.sub(r"\|pantheon_table\|", pantheon_table, content)
        pantheon_disambiguation_path.write_text(updated_content, encoding="utf-8")
        logging.info("Updated pantheon table in pantheon_disambiguation.md")
    except Exception as e:
        logging.error(f"Failed to update {pantheon_disambiguation_path}: {e}")

def ensure_directory_exists(path):
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {path}")
        except Exception as e:
            logging.error(f"Failed to create directory {path}: {e}")
            sys.exit(1)

def main():
    # Paths
    gods_json_path = Path("_json/gods_data.json")
    pantheons_json_path = Path("_json/pantheons_data.json")
    pantheons_base_path = Path("docs/pantheons")
    pantheon_disambiguation_path = pantheons_base_path / "pantheon_disambiguation.md"

    # Load data
    gods_data = load_json_data(gods_json_path)
    pantheons_data = load_json_data(pantheons_json_path)

    # Ensure pantheon directories exist
    for pantheon_name in pantheons_data['items']:
        pantheon_dir = pantheons_base_path / pantheon_name.lower()
        ensure_directory_exists(pantheon_dir)
        update_pantheon_index(pantheon_name, pantheon_dir, gods_data)

    # Update pantheon_disambiguation.md
    update_pantheon_disambiguation(pantheon_disambiguation_path, pantheons_data)

if __name__ == "__main__":
    main()
