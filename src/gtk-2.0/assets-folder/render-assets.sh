#! /usr/bin/env bash
# Render the GTK2 PNG assets from the SVG sources.
# Each asset is rendered through its box (*.boxes: id x y width height, in SVG units).
# Usage: ./render-assets.sh                                   (all variants)
#        ONLY_THEME='-Red' ONLY_COLOR='-Dark' ONLY_TYPE='' ./render-assets.sh   (one variant)

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
source ../../render-lib.sh

has_renderer || { echo "ERROR: install rsvg-convert (librsvg), resvg or inkscape" >&2; exit 1; }

THEMES=('' '-Purple' '-Pink' '-Red' '-Orange' '-Yellow' '-Green' '-Teal' '-Grey')
COLORS=('' '-Dark')
TYPES=('' '-Nord' '-Dracula')
[[ -v ONLY_THEME ]] && THEMES=("$ONLY_THEME")
[[ -v ONLY_COLOR ]] && COLORS=("$ONLY_COLOR")
[[ -v ONLY_TYPE ]] && TYPES=("$ONLY_TYPE")

./make-assets.sh

# render_set SRC_SVG BOXES_FILE OUT_DIR
render_set() {
  local src="$1" boxes="$2" dir="$3"
  mkdir -p "$dir"
  while read -r i bx by bw bh; do
    render_png "$src" "$i" "$dir/$i.png" 1 "$bx" "$by" "$bw" "$bh" || exit 1
  done < "$boxes"
}

for color in "${COLORS[@]}"; do
  for type in "${TYPES[@]}"; do
    render_set "assets-common${color}${type}.svg" "assets-common${color}.boxes" "assets-common${color}${type}"
  done
done

for theme in "${THEMES[@]}"; do
  for color in "${COLORS[@]}"; do
    for type in "${TYPES[@]}"; do
      render_set "assets${theme}${color}${type}.svg" "assets${color}.boxes" "assets${theme}${color}${type}"
    done
  done
done

# Remove the generated (recolored) sources, keep the tracked base ones
for theme in "${THEMES[@]}"; do
  for color in "${COLORS[@]}"; do
    for type in "${TYPES[@]}"; do
      if [[ "${theme}" != '' || "${type}" != '' ]]; then
        rm -f "assets${theme}${color}${type}.svg"
      fi
    done
  done
done

for color in "${COLORS[@]}"; do
  for type in '-Nord' '-Dracula'; do
    if [[ "${type}" != '' ]]; then
      rm -f "assets-common${color}${type}.svg"
    fi
  done
done

./render-assets-default-radio.sh

echo -e "DONE!"
