import json
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_species_data(species_json_path):
    try:
        with open(species_json_path, "r", encoding="utf-8") as f:
            species_data = json.load(f)
        return species_data.get("items", {})
    except Exception as e:
        logging.error(f"Failed to load species data: {e}")
        sys.exit(1)

def construct_species_table(species_items):
    table_header = "| Species Name | Type |\n|--------------|------|"
    table_rows = [
        f"| {info['name']} | {info['type']} |"
        for info in species_items.values()
    ]
    return "\n".join([table_header] + table_rows)

def write_species_table_insert(insert_file_path, species_table):
    try:
        # Create parent directories if they don't exist
        insert_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the table to the insert file
        insert_file_path.write_text(species_table, encoding="utf-8")
        logging.info(f"Species table written to {insert_file_path}")
    except Exception as e:
        logging.error(f"Failed to write to {insert_file_path}: {e}")
        sys.exit(1)

def main(species_json_path, insert_file_path):
    species_items = load_species_data(species_json_path)
    species_table = construct_species_table(species_items)
    write_species_table_insert(insert_file_path, species_table)

if __name__ == "__main__":
    # Default paths
    species_json_path = Path("_json/species_data.json")
    insert_file_path = Path("docs/species/species_table.md_insert")

    # Run the main function
    main(species_json_path, insert_file_path)
