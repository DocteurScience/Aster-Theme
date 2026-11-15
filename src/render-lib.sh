#! /usr/bin/env bash
# Shared helpers to render PNG assets from the SVG sources.
# Renderers tried in order: rsvg-convert (librsvg), rendersvg (resvg), inkscape.

RSVG_CONVERT="$(command -v rsvg-convert)" || true
RENDER_SVG="$(command -v rendersvg)" || true
INKSCAPE="$(command -v inkscape)" || true
OPTIPNG="$(command -v optipng)" || true

has_renderer() {
  [[ -n "${RSVG_CONVERT}" || -n "${RENDER_SVG}" || -n "${INKSCAPE}" ]]
}

# render_png SVG_FILE OBJECT_ID OUT_FILE [SCALE] [X Y WIDTH HEIGHT]
# Skips files that already exist, so partial/cached builds can be resumed.
# When a box (X Y WIDTH HEIGHT, in SVG user units) is given, the sheet is rendered
# through that viewport (the exact canvas of the asset) instead of cropping to the
# painted content of OBJECT_ID. This keeps every asset at its intended size
# whatever the renderer is.
render_png() {
  local src="$1" id="$2" out="$3" scale="${4:-1}"
  local bx="${5:-}" by="${6:-}" bw="${7:-}" bh="${8:-}"

  if [[ -f "$out" ]]; then
    echo "'$out' exists."
    return 0
  fi

  echo "Rendering '$out'"

  if [[ -n "${RSVG_CONVERT}" && -n "$bw" ]]; then
    local tmp
    tmp="$(mktemp --suffix=.svg)"
    # Same sheet, but: viewport = asset box, and everything except the asset itself
    # is moved into <defs> so that neighbours/background are not painted.
    perl -0pe 's/(<svg\b[^>]*?)\swidth="[^"]*"/$1/; s/(<svg\b[^>]*?)\sheight="[^"]*"/$1/; s/(<svg\b[^>]*?)\sviewBox="[^"]*"/$1/; s/<svg\b/<svg width="'"$bw"'" height="'"$bh"'" viewBox="'"$bx $by $bw $bh"'"/; s{</defs>}{</defs><defs>}; s{</svg>}{</defs><use xlink:href="#'"$id"'"/></svg>}' "$src" > "$tmp"
    "$RSVG_CONVERT" -z "$scale" -o "$out" "$tmp" || { rm -f "$out" "$tmp"; return 1; }
    rm -f "$tmp"
  elif [[ -n "${RSVG_CONVERT}" ]]; then
    "$RSVG_CONVERT" -i "#$id" -z "$scale" -o "$out" "$src" || { rm -f "$out"; return 1; }
  elif [[ -n "${RENDER_SVG}" ]]; then
    if [[ "$scale" == "1" ]]; then
      "$RENDER_SVG" --export-id "$id" "$src" "$out" || { rm -f "$out"; return 1; }
    else
      "$RENDER_SVG" --export-id "$id" --dpi 192 --zoom "$scale" "$src" "$out" || { rm -f "$out"; return 1; }
    fi
  else
    local dpi=$((96 * scale))
    "$INKSCAPE" --export-id="$id" --export-id-only --export-dpi="$dpi" \
                --export-filename="$out" "$src" >/dev/null || { rm -f "$out"; return 1; }
    [[ -n "${OPTIPNG}" ]] && "$OPTIPNG" -o7 --quiet "$out"
  fi
  return 0
}
