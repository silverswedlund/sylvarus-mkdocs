#!/bin/bash

# sylvarus_mkdocs_build.sh
# Run all MkDocs build scripts for the Sylvarus D&D campaign

set -e  # Exit on error
echo "🔧 Starting Sylvarus MkDocs Build..."

# List of scripts to run in order
SCRIPTS=(
  "_scripts/generate_god_indexes.py"
  "_scripts/generate_pantheon_indexes.py"
)

for SCRIPT in "${SCRIPTS[@]}"; do
  echo "🚀 Running $SCRIPT..."
  python3 "$SCRIPT"
  echo "✅ Finished $SCRIPT"
  echo "---------------------------"
done

echo "🎉 Sylvarus MkDocs Build Complete!"
