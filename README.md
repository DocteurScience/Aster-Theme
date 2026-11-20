# Aster

Aster is a GTK and GNOME Shell theme that keeps the colours and identity of
[Orchis](https://github.com/vinceliuice/Orchis-theme) and brings the shapes,
states and accessibility rules of [Material Design 3](https://m3.material.io).

![Aster light](images/screenshot-light.png?raw=true)
![Aster dark](images/screenshot-dark.png?raw=true)

## What Aster changes

**Kept from Orchis**
- Grey surfaces and the blue accent palette (plus the purple, pink, red, orange,
  yellow, green, teal and grey variants, and the Nord / Dracula colour schemes).
- The floating, accent-tinted sidebar card whose selected row blends into the content.
- Floating, translucent top bar.

**From Material 3**
- 40 px pill buttons, 52×32 switches with a growing handle, filled text fields.
- M3 state layers: hover 8 %, focus and press 10 %, drag 16 %.
- Matching switch artwork in GNOME Shell (quick settings, Do Not Disturb), M3 sliders.

**Fixes for recent GTK 4 / libadwaita**
- The libadwaita colour variables (`--accent-bg-color`, palette, …) are defined
  correctly, so `var(--x)` and `@x` give the same colour.
- Accent, success, warning and error text colours are left to libadwaita, which
  derives readable variants from the background colours.
- Text contrast checked automatically (`tools/check-contrast.py`): every pair
  reaches 4.5:1 in light and dark, including the destructive red (#D32F2F).

![Aster default vs classic Orchis look](images/aster-vs-classic.png?raw=true)

Prefer the original Orchis look? Install with `--tweaks classic`.

## Requirements

- GTK `>= 3.20` (GTK 4 / libadwaita supported through `-l`, see below)
- `gnome-themes-extra` (or `gnome-themes-standard`)
- Murrine engine for GTK 2 (`gtk-engine-murrine` on Arch, `gtk-murrine-engine` on Fedora,
  `gtk2-engine-murrine` on openSUSE, `gtk2-engines-murrine` on Debian/Ubuntu)
- `sassc` (build)
- An SVG renderer to generate the PNG assets at install time:
  `rsvg-convert` (`librsvg2-bin` on Debian/Ubuntu, `librsvg2-tools` on Fedora) with `perl`,
  or `resvg`, or `inkscape`

## Installation

```sh
git clone https://github.com/DocteurScience/aster-theme.git
cd aster-theme
./install.sh            # all colour and size variants into ~/.themes
./install.sh -l         # also link the theme for libadwaita (GTK 4) apps
```

Then select **Aster** in GNOME Tweaks (applications and, with the User Themes
extension, GNOME Shell).

### Common options

| Option | Effect |
|---|---|
| `-t blue\|purple\|…\|all` | Accent colour variant |
| `-c light\|dark` | Light or dark variant only |
| `-s compact` | Compact size |
| `-l` | Link the GTK 4 theme to `~/.config/gtk-4.0` for libadwaita apps |
| `--tweaks classic` | Original Orchis look (Orchis shapes) |
| `--tweaks clear` | Fully transparent top bar, text and icons with a drop shadow |
| `--tweaks solid` | Opaque top bar |
| `--tweaks compact` | Top bar attached to the screen edge instead of floating |
| `--tweaks black` | Pure black dark variant |
| `--tweaks nord` / `dracula` | Nord or Dracula colour scheme |
| `--round N` | Window corner radius in px |
| `-r` | Uninstall |

![Default and clear top bar](images/panel-clear.png?raw=true)

Run `./install.sh -h` for the full list.

### libadwaita (GNOME 42 and later)

libadwaita apps do not load GTK themes on their own. `./install.sh -l` links the
selected Aster `gtk-4.0` folder to `~/.config/gtk-4.0`, which libadwaita reads:

```sh
./install.sh -c dark -l            # dark variant
./install.sh -c dark -t purple -l  # dark purple variant
```

The theme can then no longer be switched from GNOME Tweaks for these apps; run the
command again to change variant.

### Flatpak

```sh
sudo flatpak override --filesystem=xdg-config/gtk-3.0
sudo flatpak override --filesystem=xdg-config/gtk-4.0
```

## Extensions

- [Sanket](https://github.com/narkagni/sanket): notification island, compact Quick Settings and calendar are styled with Aster's colours (pinned notifications, toasts, pills).
- [Blur my Shell](https://github.com/aunetx/blur-my-shell) and Dash to Dock: styles inherited from Orchis.

## Status

- Tested on GTK 4.24 / libadwaita 1.10, Nautilus 46 and GNOME Shell 46.
- GNOME Shell 47 and later: versions 48+ use the 48 stylesheet; not yet verified on a real 48–50 session.
- GTK 3 apps still use the Orchis styles.

## Development

- Sass sources: `src/_sass` (`_colors.scss`, `_variables.scss`, `gtk/`, `gnome-shell/`).
- The Material 3 shapes are controlled by `$material` / `$m3` in `src/_sass/_tweaks.scss`.
- Contrast test: `python3 tools/check-contrast.py <gtk.css> <gtk-dark.css>`.
- `install.sh` returns 0 even when Sass fails: check its output for `error`.

## Credits and license

Aster is a fork of [Orchis-theme](https://github.com/vinceliuice/Orchis-theme) by
vinceliuice, itself based on [materia-theme](https://github.com/nana-4/materia-theme)
by nana-4. Distributed under the GNU GPL v3 (see `COPYING`).
