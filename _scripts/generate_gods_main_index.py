import json
import os

# Path to JSON and markdown
json_path = "_json/gods_data.json"
output_md_path = "docs/gods/index.md"

# Load gods data
with open(json_path, "r", encoding="utf-8") as file:
    gods_data = json.load(file)

# Start building the markdown content
md_content = "# Gods of Sylvarus\n\n"

# Add table header
md_content += "| Name | Pantheon | Ascension Epoch |\n"
md_content += "|------|----------|-----------------|\n"

# Iterate through gods to create markdown table rows with links
for god_key, god_info in gods_data["items"].items():
    god_name = god_info["name"]
    pantheon = god_info["pantheon"]
    ascension_epoch = god_info["ascension_epoch"]
    god_path = god_name.lower()
    pantheon_path = pantheon.lower()
    epoch_path = ascension_epoch.lower().replace(' ', '_')
    md_content += (
        f"| [{god_name}](./{god_path}/index.md) "
        f"| [{pantheon}](../pantheons/{pantheon_path}/index.md) "
        f"| [{ascension_epoch}](../history/time_periods/{epoch_path}/index.md) |\n"
    )

# Write markdown content to file
os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
with open(output_md_path, "w", encoding="utf-8") as md_file:
    md_file.write(md_content)

print(f"Index created successfully at {output_md_path}")
