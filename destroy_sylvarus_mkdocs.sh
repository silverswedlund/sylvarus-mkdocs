#!/bin/bash

# sylvarus_mkdocs_destroy.sh
# Deletes generated index.md files for gods and pantheons

set -e

echo "⚠️  Destroying generated .md and .md_insert files..."

# Delete all .md_insert files
echo "🧹 Deleting all .md_insert files..."
find docs/ -type f -name "*.md_insert" -delete

# Delete all .md files
echo "🧹 Deleting all .md files except for disambiguation files..."
find docs/ -type f -name "*.md" ! -name "*sylvarus_disambiguation.md" -delete

echo "🔥 All .md and .md_insert files deleted."

if [ -d "_scripts/pickles" ] && [ "$(ls -A _scripts/pickles/)" ]; then
    trash _scripts/pickles/*
    echo "🔥🥒 All pickles deleted."
fi
