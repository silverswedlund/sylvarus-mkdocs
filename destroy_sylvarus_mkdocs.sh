#!/bin/bash

# sylvarus_mkdocs_destroy.sh
# Deletes generated index.md files for gods and pantheons

set -e

echo "⚠️  Destroying generated index.md files..."

# Delete index.md in each god folder
echo "🧹 Cleaning docs/gods/*/index.md..."
find docs/entities/gods/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each pantheon folder
echo "🧹 Cleaning docs/pantheons/*/index.md..."
find docs/pantheons/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each demigod folder
echo "🧹 Cleaning docs/demigods/*/index.md..."
find docs/entities/demigods/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each titan folder
echo "🧹 Cleaning docs/titans/*/index.md..."
find docs/entities/titans/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each territories folder
echo "🧹 Cleaning docs/planes/material/sylvarus/locations/territories/*/index.md..."
find docs/planes/material/sylvarus/locations/territories/*/ -type f -name "index.md" -exec rm -v {} \;

# Delete index.md in each cities folder
echo "🧹 Cleaning docs/planes/material/sylvarus/locations/cities/*/index.md..."
find docs/planes/material/sylvarus/locations/cities/*/ -type f -name "index.md" -exec rm -v {} \;

# Clear all .md_insert files except content.md_insert
echo "🧹 Clearing all .md_insert files except content.md_insert..."
find docs/ -type f -name "*.md_insert" ! -name "*content.md_insert" -exec sh -c 'echo "" > "$1"' sh {} \;

# Delete index.md in each time_periods folder
echo "🧹 Cleaning docs/history/time_periods/*/index.md..."
find docs/history/time_periods/*/ -type f -name "index.md" -exec rm -v {} \;

echo "🔥 All specified index.md files deleted."

if [ -d "_scripts/pickles" ] && [ "$(ls -A _scripts/pickles/)" ]; then
    trash _scripts/pickles/*
    echo "🔥🥒 All pickles deleted."
fi
