# generate_pantheon_indexes.py

import json
import os

# Define paths (adjust if necessary)
gods_json_path = os.path.join("_json", "gods_data.json")
pantheon_index_md_path = os.path.join("docs", "pantheons", "pantheon_disambiguation.md")

# Load gods data
with open(gods_json_path, 'r') as file:
    gods_data = json.load(file)

# Extract unique pantheons
pantheons = set()
for god in gods_data["items"].values():
    pantheon = god.get("pantheon", "").strip()
    if pantheon:
        pantheons.add(pantheon)

# Sort pantheons alphabetically
sorted_pantheons = sorted(pantheons)

# Generate markdown content
md_content = """# Pantheons

Pantheons are coalitions of gods, akin to political parties. These divine groups are self-enforcing, governed internally but adhering loosely to the overarching decisions made by Olympus.

## List of Pantheons

| Pantheon |
|----------|
"""

# Add table rows
for pantheon in sorted_pantheons:
    pantheon_link = pantheon.lower().replace(' ', '_')
    md_content += f"| [{pantheon}]({pantheon_link}/index.md) |\n"

# Ensure directory exists
dirname = os.path.dirname(pantheon_index_md_path)
os.makedirs(dirname, exist_ok=True)

# Save markdown to index.md
with open(pantheon_index_md_path, 'w') as file:
    file.write(md_content)

print(f"Pantheon index generated successfully at {pantheon_index_md_path}")
