#! /usr/bin/env bash

# Usage: ONLY_COLOR='-Dark' ONLY_TYPE='-Nord' ./render-assets-default-radio.sh  (optional filters)

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
source ../../render-lib.sh

has_renderer || { echo "ERROR: install rsvg-convert (librsvg), resvg or inkscape" >&2; exit 1; }

INDEX="assets-default-radio.txt"

COLORS=('' '-Dark')
TYPES=('' '-Nord' '-Dracula')
[[ -v ONLY_COLOR ]] && COLORS=("$ONLY_COLOR")
[[ -v ONLY_TYPE ]] && TYPES=("$ONLY_TYPE")

for color in "${COLORS[@]}"; do
  for type in "${TYPES[@]}"; do

    ASSETS_DIR="assets-default-radio${color}${type}"
    SRC_FILE="assets-default-radio${color}${type}.svg"

    # [[ -d $ASSETS_DIR ]] && rm -rf $ASSETS_DIR
    mkdir -p $ASSETS_DIR

    if [[ "$type" == '-Nord' ]]; then
      assets_color_light='#8bd9b4'
      assets_color_dark='#60a684'
    elif [[ "$type" == '-Dracula' ]]; then
      assets_color_light='#66ffb5'
      assets_color_dark='#48db94'
    fi

    if [[ "$type" != '' ]]; then
      cp -r "assets-default-radio${color}.svg" "assets-default-radio${color}${type}.svg"
      if [[ "$color" == '' ]]; then
        sed -i "s/#0F9D58/${assets_color_light}/g" "assets-default-radio${color}${type}.svg"
      else
        sed -i "s/#81C995/${assets_color_dark}/g" "assets-default-radio${color}${type}.svg"
      fi
    fi

    while read -r i bx by bw bh; do
      render_png "$SRC_FILE" "$i" "$ASSETS_DIR/$i.png" 1 "$bx" "$by" "$bw" "$bh" || exit 1
    done < "assets-default-radio${color}.boxes"
  done
done

for color in "${COLORS[@]}"; do
  for type in '-Nord' '-Dracula'; do
    ASSETS_FILE="assets-default-radio${color}${type}.svg"
    rm -rf "${ASSETS_FILE}"
  done
done

echo -e "DONE!"
