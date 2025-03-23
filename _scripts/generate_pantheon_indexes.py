import os
import json
from pathlib import Path

# === Config ===
GODS_JSON_PATH = "_json/gods_data.json"
PANTHEONS_DIR = "docs/pantheons"
GODS_BASE_PATH = "../../gods"

# === Helper Functions ===
def slugify(name):
    return name.strip().lower().replace(" ", "_")

def generate_markdown(pantheon_name, god_names):
    lines = [f"# {pantheon_name}\n", "## Members\n"]
    for god in sorted(god_names):
        slug = slugify(god)
        lines.append(f"- [{god}]({GODS_BASE_PATH}/{slug}/)\n")
    return "".join(lines)

# === Main Script ===
def main():
    # Load JSON data
    with open(GODS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    gods = data.get("items", {})

    pantheon_members = {}

    # Group gods by pantheon
    for god_key, god_data in gods.items():
        pantheon = god_data.get("pantheon", "").strip()
        name = god_data.get("name", god_key).strip()

        if not pantheon:
            continue  # skip gods without pantheon

        pantheon_members.setdefault(pantheon, []).append(name)

    # Create index files per pantheon
    for pantheon, members in pantheon_members.items():
        pantheon_slug = slugify(pantheon)
        pantheon_path = Path(PANTHEONS_DIR) / pantheon_slug
        pantheon_path.mkdir(parents=True, exist_ok=True)

        index_md_path = pantheon_path / "index.md"
        content = generate_markdown(pantheon, members)

        with open(index_md_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Generated: {index_md_path}")

if __name__ == "__main__":
    main()
