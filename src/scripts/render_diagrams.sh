#!/usr/bin/env bash
# 本地渲染 Markdown 中的 Mermaid 图为 SVG
# 用法: bash render_diagrams.sh <file.md>
#        bash render_diagrams.sh requirements/REQ-NNN-<topic>/99-review/diagrams.md
set -euo pipefail

INPUT="${1:-}"
if [ -z "$INPUT" ] || [ ! -f "$INPUT" ]; then
    echo "Usage: render_diagrams.sh <markdown-file.md>"
    echo "Render all Mermaid blocks in a Markdown file to inline SVG images."
    exit 1
fi

OUTPUT="${INPUT%.md}-rendered.md"
DIR=$(dirname "$INPUT")
NAME=$(basename "$INPUT" .md)

# Method 1: mermaid-cli (mmdc) — best for Markdown→rendered Markdown
if command -v mmdc &> /dev/null; then
    echo "✅ Using mermaid-cli (mmdc)..."
    mmdc -i "$INPUT" -o "$OUTPUT" -s 2
    echo "✅ Rendered: $OUTPUT"
    exit 0
fi

# Method 2: diagram (Rust) — render each mermaid block to separate SVG
if command -v diagram &> /dev/null; then
    echo "✅ Using diagram CLI..."
    # Extract mermaid blocks and render individually
    awk '/```mermaid/{flag=1; i++; next} /```/{flag=0; next} flag{print > sprintf("'$DIR'/'$NAME'_%d.mmd", i)}' "$INPUT"
    count=0
    for mmd in "$DIR"/"$NAME"_*.mmd; do
        [ -f "$mmd" ] || continue
        diagram render "$mmd" --output "${mmd%.mmd}.svg"
        rm "$mmd"
        count=$((count+1))
    done
    echo "✅ Rendered $count diagrams to SVG in $DIR/"
    exit 0
fi

# Method 3: npx (no install, one-shot)
echo "⚠️  No diagram CLI found. Trying npx..."
npx -p @mermaid-js/mermaid-cli mmdc -i "$INPUT" -o "$OUTPUT" -s 2 && echo "✅ Rendered: $OUTPUT" && exit 0

echo "❌ Failed to render diagrams. Install one of:"
echo "   npm install -g @mermaid-js/mermaid-cli"
echo "   cargo install --git https://github.com/yingkitw/diagram"
exit 1
