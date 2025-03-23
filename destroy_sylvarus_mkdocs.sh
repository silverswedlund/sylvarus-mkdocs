#!/bin/bash

# sylvarus_mkdocs_destroy.sh
# Deletes generated index.md files for gods and pantheons

set -e

echo "⚠️  Destroying generated index.md files..."

# Delete index.md in each god folder
echo "🧹 Cleaning docs/gods/*/index.md..."
find docs/gods/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each pantheon folder
echo "🧹 Cleaning docs/pantheons/*/index.md..."
find docs/pantheons/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each demigod folder
echo "🧹 Cleaning docs/demigods/*/index.md..."
find docs/demigods/*/ -type f -name "index.md" -exec rm -v {} \;

echo "🔥 All specified index.md files deleted."