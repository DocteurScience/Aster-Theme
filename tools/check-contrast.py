#!/usr/bin/env python3
"""Check WCAG contrast of the named colors exported by a compiled Aster GTK4 CSS.

Usage:
    tools/check-contrast.py PATH/TO/gtk.css [PATH/TO/gtk-dark.css ...]

The scheme is "dark" for files named *dark*, "light" otherwise.

libadwaita derives the text variants (@accent_color, @success_color, ...) from the
matching *_bg_color in OKLab (lightness capped at 0.5 on light, floored at 0.85 on
dark); this script reproduces that derivation, so the theme must not define those
colors itself. Exit status is 1 when a pair is below its threshold.
"""
import math
import re
import sys

# GNOME's accent colors (libadwaita --accent-*), used when the theme leaves
# @accent_bg_color to the system.
GNOME_ACCENTS = {
    "blue": "#3584e4", "teal": "#2190a4", "green": "#3a944a", "yellow": "#c88800",
    "orange": "#ed5b00", "red": "#e62d42", "pink": "#d56199", "purple": "#9141ac",
    "slate": "#6f8396",
}
# libadwaita's own defaults, for names a theme may leave undefined.
DEFAULTS = {
    "light": {
        "accent_bg_color": "#3584e4", "accent_fg_color": "#ffffff",
        "destructive_bg_color": "#e01b24", "destructive_fg_color": "#ffffff",
        "success_bg_color": "#2ec27e", "success_fg_color": "#ffffff",
        "warning_bg_color": "#e5a50a", "warning_fg_color": "rgba(0,0,0,0.8)",
        "error_bg_color": "#e01b24", "error_fg_color": "#ffffff",
    },
    "dark": {
        "accent_bg_color": "#3584e4", "accent_fg_color": "#ffffff",
        "destructive_bg_color": "#c01c28", "destructive_fg_color": "#ffffff",
        "success_bg_color": "#26a269", "success_fg_color": "#ffffff",
        "warning_bg_color": "#cd9309", "warning_fg_color": "rgba(0,0,0,0.8)",
        "error_bg_color": "#c01c28", "error_fg_color": "#ffffff",
    },
}


def parse_color(value):
    value = value.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{6})([0-9a-f]{2})?", value)
    if m:
        h = m.group(1)
        a = int(m.group(2), 16) / 255 if m.group(2) else 1.0
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)
    m = re.fullmatch(r"#([0-9a-f])([0-9a-f])([0-9a-f])", value)
    if m:
        return tuple(int(c * 2, 16) for c in m.groups()) + (1.0,)
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)(?:[ ,/]+([\d.]+%?))?\s*\)", value)
    if m:
        a = m.group(4)
        a = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    named = {"white": (255, 255, 255, 1.0), "black": (0, 0, 0, 1.0)}
    return named.get(value)


def load_colors(path):
    css = open(path, encoding="utf-8").read()
    raw = dict(re.findall(r"@define-color\s+([\w-]+)\s+([^;]+);", css))
    colors = {}

    def resolve(name, seen=()):
        if name in colors:
            return colors[name]
        v = raw.get(name)
        if v is None or name in seen:
            return None
        v = v.strip()
        if v.startswith("@"):
            c = resolve(v[1:], seen + (name,))
        else:
            c = parse_color(v)
        colors[name] = c
        return c

    for n in raw:
        resolve(n)
    return {k: v for k, v in colors.items() if v}


def over(fg, bg):
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def luminance(c):
    def f(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(fg, bg):
    bg = over(bg, (255, 255, 255, 1.0)) if bg[3] < 1 else bg
    fg = over(fg, bg)
    la, lb = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# --- OKLab (Björn Ottosson) -------------------------------------------------
def _lin(x):
    x /= 255
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def _gamma(x):
    x = max(0.0, min(1.0, x))
    return 255 * (12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055)


def to_oklab(c):
    r, g, b = _lin(c[0]), _lin(c[1]), _lin(c[2])
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def from_oklab(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (_gamma(r), _gamma(g), _gamma(bl), 1.0)


def text_variant(bg_color, scheme):
    """libadwaita: oklab(from @x_bg_color min(l, 0.5) a b) / max(l, 0.85) on dark."""
    L, a, b = to_oklab(bg_color)
    L = min(L, 0.5) if scheme == "light" else max(L, 0.85)
    return from_oklab(L, a, b)


def check(path, scheme, accents):
    colors = load_colors(path)
    get = lambda n: colors.get(n) or parse_color(DEFAULTS[scheme].get(n, ""))
    failures = []
    rows = []

    def add(label, fg, bg, minimum):
        if fg is None or bg is None:
            return
        r = contrast(fg, bg)
        rows.append((label, r, minimum))
        if r < minimum:
            failures.append(label)

    surfaces = {n: get(n) for n in ("window_bg_color", "view_bg_color", "card_bg_color", "sidebar_bg_color")}
    window = surfaces["window_bg_color"]
    # translucent cards (libadwaita dark) sit on the window
    if surfaces["card_bg_color"] and surfaces["card_bg_color"][3] < 1 and window:
        surfaces["card_bg_color"] = over(surfaces["card_bg_color"], window)

    roles = ["accent", "destructive", "success", "warning", "error"]
    bgs = {r: get(f"{r}_bg_color") for r in roles}
    variants = [("", bgs["accent"])] if "accent_bg_color" in colors else \
        [(f"[{n}] ", parse_color(v)) for n, v in accents.items()]

    for tag, accent_bg in variants:
        for role in roles:
            bg = accent_bg if role == "accent" else bgs[role]
            if bg is None:
                continue
            text = text_variant(bg, scheme)
            for sname in ("window_bg_color", "view_bg_color", "card_bg_color"):
                add(f"{tag}{role} text on {sname[:-9]}", text, surfaces[sname], 4.5)
            fgc = get(f"{role}_fg_color")
            if role == "accent" and tag:
                fgc = parse_color(DEFAULTS[scheme]["accent_fg_color"])
            add(f"{tag}{role} button/banner label", fgc, bg, 4.5)

    for fg, bg in (("window_fg_color", "window_bg_color"), ("view_fg_color", "view_bg_color"),
                   ("card_fg_color", "card_bg_color"), ("headerbar_fg_color", "headerbar_bg_color"),
                   ("popover_fg_color", "popover_bg_color"), ("dialog_fg_color", "dialog_bg_color"),
                   ("sidebar_fg_color", "sidebar_bg_color")):
        b = surfaces.get(bg) or get(bg)
        add(f"{fg[:-9]} on {bg[:-9]}", get(fg), b, 4.5)
    return rows, failures


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    status = 0
    verbose = "-v" in argv
    for path in [a for a in argv[1:] if a != "-v"]:
        scheme = "dark" if "dark" in path.lower() else "light"
        rows, failures = check(path, scheme, GNOME_ACCENTS)
        print(f"== {path} ({scheme}): {len(rows)} pairs, {len(failures)} below threshold")
        for label, r, minimum in rows:
            if r < minimum or verbose:
                print(f"   {'FAIL' if r < minimum else 'ok  '} {r:5.2f} (min {minimum})  {label}")
        status |= 1 if failures else 0
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
