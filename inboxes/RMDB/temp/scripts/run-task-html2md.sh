#!/usr/bin/env bash
# One-click: re-parse all raw HTML files to Markdown in docs/tasks.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$SCRIPT_DIR/probHTML2MD"
OUT_DIR="$(dirname "$SCRIPT_DIR")/docs/tasks"

cd "$PROJ_DIR"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/task-*.md

count=0
for f in raw-html/task-*.html; do
    name=$(basename "$f" .html)
    python3 html2md.py "$f" -o "$OUT_DIR/${name}.md"
    echo "  -> ${name}.md"
    count=$((count + 1))
done

echo ""
echo "Done — ${count} files written to ${OUT_DIR}"
