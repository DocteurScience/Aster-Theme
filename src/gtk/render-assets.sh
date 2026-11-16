#! /usr/bin/env bash
# Render the GTK3/GTK4 PNG assets from assets.svg.
# Each asset is rendered through its box (assets.boxes: id x y width height, in SVG units).
# Usage: ./render-assets.sh                                   (all variants)
#        ONLY_THEME='-Red' ONLY_TYPE='-Nord' ./render-assets.sh   (a single variant)

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
source ../render-lib.sh

has_renderer || { echo "ERROR: install rsvg-convert (librsvg), resvg or inkscape" >&2; exit 1; }

THEMES=('' '-Purple' '-Pink' '-Red' '-Orange' '-Yellow' '-Green' '-Teal' '-Grey')
TYPES=('' '-Nord' '-Dracula')
[[ -v ONLY_THEME ]] && THEMES=("$ONLY_THEME")
[[ -v ONLY_TYPE ]] && TYPES=("$ONLY_TYPE")

./make-assets.sh

for theme in "${THEMES[@]}"; do
  for type in "${TYPES[@]}"; do
    ASSETS_DIR="assets${theme}${type}"
    SRC_FILE="assets${theme}${type}.svg"

    mkdir -p "$ASSETS_DIR"

    while read -r i bx by bw bh; do
      render_png "$SRC_FILE" "$i" "$ASSETS_DIR/$i.png" 1 "$bx" "$by" "$bw" "$bh" || exit 1
      render_png "$SRC_FILE" "$i" "$ASSETS_DIR/$i@2.png" 2 "$bx" "$by" "$bw" "$bh" || exit 1
    done < assets.boxes

    if [[ "${theme}" != '' || "${type}" != '' ]]; then
      rm -f "${SRC_FILE}"
    fi
  done
done

echo -e "DONE!"
