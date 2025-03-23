# _scripts/generate_god_index.py

import json
from pathlib import Path

from mkdocs_gen_files import new_page

# Load god metadata from your JSON
with open("_json/gods_data.json") as f:
    gods = json.load(f)

# Sort however you like
gods.sort(key=lambda g: g["name"].lower())

# Build raw HTML table
table_rows = [
    "<tr><th>Name</th><th>Species</th><th>Pantheon</th><th>Link</th></tr>"
]
for god in gods:
    slug = god["name"].lower().replace(" ", "")
    link = f"./{slug}/index.md"
    table_rows.append(
        f"<tr><td>{god['name']}</td><td>{god['species']}</td><td>{god['pantheon']}</td><td><a href='{link}'>View</a></td></tr>"
    )

html_table = "<table>\n<thead>\n{}\n</thead>\n<tbody>\n{}\n</tbody>\n</table>".format(
    table_rows[0], "\n".join(table_rows[1:])
)

# JS for sorting
sort_js = """
<script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>
<script>
  window.addEventListener('load', function () {
    new Tablesort(document.querySelector("table"));
  });
</script>
"""

# Final content
output = "# Gods Index\n\nSort by clicking headers.\n\n" + html_table + "\n" + sort_js

# Write the file to the virtual files system (becomes docs/gods/index.md)
path = Path("gods/index.md")
new_page(str(path), output)