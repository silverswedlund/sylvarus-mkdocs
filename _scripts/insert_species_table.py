import json
import logging
from pathlib import Path
import sys
import re

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
        f"| [{info['name']}](./{info['name'].lower()}/index.md) | {info['type']} |"
        for info in species_items.values()
    ]
    return "\n".join([table_header] + table_rows)

def update_species_md(species_md_path, species_table):
    try:
        species_md_content = species_md_path.read_text(encoding="utf-8")
        
        # Use regex to find and replace the existing table
        table_pattern = r"\| Species Name \| Type \|\n\|--------------\|------\|(?:\n\| .+ \| .+ \|)*"
        updated_content = re.sub(table_pattern, species_table, species_md_content)
        
        species_md_path.write_text(updated_content, encoding="utf-8")
        logging.info("Species table inserted into species.md.")
    except Exception as e:
        logging.error(f"Failed to update species.md: {e}")
        sys.exit(1)

def main(species_json_path, species_md_path):
    species_items = load_species_data(species_json_path)
    species_table = construct_species_table(species_items)
    update_species_md(species_md_path, species_table)

if __name__ == "__main__":
    # Default paths
    species_json_path = Path("_json/species_data.json")
    species_md_path = Path("docs/species/species.md")

    # Run the main function
    main(species_json_path, species_md_path)
