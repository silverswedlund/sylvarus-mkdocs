#!/bin/bash

# sylvarus_mkdocs_build.sh
# Run all MkDocs build scripts for the Sylvarus D&D campaign

set -e  # Exit on error
echo "🔧 Starting Sylvarus MkDocs Build..."

# List of scripts to run in order
SCRIPTS=(
  "_scripts/generate_indexes_from_json.py"
  "_scripts/generate_main_gods_main.py"
  "_scripts/generate_main_pantheon_index.py"
  "_scripts/generate_pantheon_indexes.py"
  "_scripts/insert_identifier_tables.py"
  "_scripts/auto_link_references.py"
)

# Run Scripts
for SCRIPT in "${SCRIPTS[@]}"; do
  echo "🚀 Running $SCRIPT..."
  python3 "$SCRIPT"
  echo "✅ Finished $SCRIPT"
  echo "---------------------------"
done

echo "🎉 Sylvarus MkDocs Build Complete!"

#!/bin/bash

echo "🔄 Converting non-JPG images to JPG and trashing originals..."

find . -type f \( -iname "*.png" -o -iname "*.jpeg" -o -iname "*.webp" \) -print0 | while IFS= read -r -d '' img; do
  new="${img%.*}.jpg"

  echo "📷 Converting: $img → $new"
  if magick "$img" "$new"; then
    echo "🗑️ Trashing original: $img"
    trash "$img"
  else
    echo "❌ Failed to convert: $img"
  fi
done

echo ""
echo "🔤 Renaming files (lowercase + replace spaces with underscores)..."

find docs/ -type f -print0 | while IFS= read -r -d '' file; do
  base=$(basename "$file")

  # Only rename if filename contains uppercase letters or spaces
  if echo "$base" | grep -q '[A-Z ]'; then
    echo $basename
    dir=$(dirname "$file")
    new_base=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
    new_path="$dir/$new_base"

    echo "✏️ Renaming: $file → $new_path"
    mv "$file" "$new_path"
  fi
done

echo ""
echo "✅ Done!"
