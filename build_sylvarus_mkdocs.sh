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
)

# Run Scripts
for SCRIPT in "${SCRIPTS[@]}"; do
  echo "🚀 Running $SCRIPT..."
  python3 "$SCRIPT"
  echo "✅ Finished $SCRIPT"
  echo "---------------------------"
done

echo "🎉 Sylvarus MkDocs Build Complete!"

# Convert non-jpg images into jpg and trash the non-jpg
find . -type f \( -iname "*.png" -o -iname "*.jpeg" -o -iname "*.webp" \) -exec sh -c '
  for img; do
    new="${img%.*}.jpg"
    magick "$img" "$new" && trash "$img"
  done
' sh {} +

# Rename every file name with spaces to use underscore and make name lowercase
find . -type f | while read -r file; do
  dir=$(dirname "$file")
  base=$(basename "$file")
  new_base=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
  new_path="$dir/$new_base"
  [ "$file" != "$new_path" ] && mv "$file" "$new_path"
done
