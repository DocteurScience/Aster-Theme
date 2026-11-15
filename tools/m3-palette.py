#!/usr/bin/env python3
"""Material 3 tonal palettes (HCT) for Aster, stdlib only.

    tools/m3-palette.py '#6750A4'            # print the roles, light and dark
    tools/m3-palette.py '#6750A4' --scss     # emit SCSS maps ($m3-light / $m3-dark)

HCT = CAM16 hue and chroma + CIE L* tone. The palettes follow the Material
Color Utilities "TonalSpot" scheme (primary C=36, secondary 16, tertiary 24
hue+60, neutral 6, neutral variant 8, error from hue 25 / C=84).
"""
import math
import sys

# ---- sRGB / XYZ --------------------------------------------------------------
M_RGB2XYZ = ((0.41233895, 0.35762064, 0.18051042),
             (0.2126, 0.7152, 0.0722),
             (0.01932141, 0.11916382, 0.95034478))
M_XYZ2RGB = ((3.2413774792388685, -1.5376652402851851, -0.49885366846268053),
             (-0.9691452513005321, 1.8758853451067872, 0.04156585616912061),
             (0.05562093689691305, -0.20395524564742123, 1.0571799111220335))
WHITE = (95.047, 100.0, 108.883)


def lin(c):
    c /= 255
    return 100 * (c / 12.92 if c <= 0.040449936 else ((c + 0.055) / 1.055) ** 2.4)


def delin(v):
    v /= 100
    c = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return max(0, min(255, round(c * 255)))


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % rgb


def lstar(y):
    y /= 100
    f = y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116
    return 116 * f - 16


def y_from_lstar(l):
    fy = (l + 16) / 116
    return (fy ** 3 if fy ** 3 > 216 / 24389 else (116 * fy - 16) / (24389 / 27)) * 100


# ---- CAM16 (default viewing conditions) -----------------------------------
_adapt = 200 / math.pi * y_from_lstar(50) / 100
_n = y_from_lstar(50) / WHITE[1]
_c, _nc, _f = 0.69, 1.0, 1.0
_rw = [0.401288 * WHITE[0] + 0.650173 * WHITE[1] - 0.051461 * WHITE[2],
       -0.250268 * WHITE[0] + 1.204414 * WHITE[1] + 0.045854 * WHITE[2],
       -0.002079 * WHITE[0] + 0.048952 * WHITE[1] + 0.953127 * WHITE[2]]
_d = max(0, min(1, _f * (1 - (1 / 3.6) * math.exp((-_adapt - 42) / 92))))
_dr = [_d * WHITE[1] / v + 1 - _d for v in _rw]
_k = 1 / (5 * _adapt + 1)
_fl = (_k ** 4 * _adapt + 0.1 * (1 - _k ** 4) ** 2 * (5 * _adapt) ** (1 / 3))
_nbb = _ncb = 0.725 / _n ** 0.2
_z = 1.48 + math.sqrt(_n)
_aw = None


def _adapted(v):
    x = (_fl * abs(v) / 100) ** 0.42
    return math.copysign(400 * x / (x + 27.13), v)


_aw = (2 * _adapted(_rw[0] * _dr[0]) + _adapted(_rw[1] * _dr[1]) + 0.05 * _adapted(_rw[2] * _dr[2])) * _nbb


def cam16(rgb):
    x, y, z = (sum(M_RGB2XYZ[i][j] * lin(rgb[j]) for j in range(3)) for i in range(3))
    rc = _dr[0] * (0.401288 * x + 0.650173 * y - 0.051461 * z)
    gc = _dr[1] * (-0.250268 * x + 1.204414 * y + 0.045854 * z)
    bc = _dr[2] * (-0.002079 * x + 0.048952 * y + 0.953127 * z)
    ra, ga, ba = _adapted(rc), _adapted(gc), _adapted(bc)
    a = (11 * ra - 12 * ga + ba) / 11
    b = (ra + ga - 2 * ba) / 9
    u = (20 * ra + 20 * ga + 21 * ba) / 20
    p2 = (40 * ra + 20 * ga + ba) / 20
    hue = math.degrees(math.atan2(b, a)) % 360
    ac = p2 * _nbb
    j = 100 * (ac / _aw) ** (_c * _z)
    t = (50000 / 13 * (0.25 * (math.cos(math.radians(hue) + 2) + 3.8)) * _nc * _ncb
         * math.hypot(a, b) / (u + 0.305))
    alpha = t ** 0.9 * (1.64 - 0.29 ** _n) ** 0.73
    chroma = alpha * math.sqrt(j / 100)
    return hue, chroma, lstar(y)


def from_jch(j, chroma, hue):
    """CAM16 J, C, h -> XYZ (D65, 0..100)."""
    if j <= 0:
        return (0.0, 0.0, 0.0)
    alpha = chroma / math.sqrt(j / 100)
    t = (alpha / (1.64 - 0.29 ** _n) ** 0.73) ** (1 / 0.9)
    h = math.radians(hue)
    et = 0.25 * (math.cos(h + 2) + 3.8)
    ac = _aw * (j / 100) ** (1 / _c / _z)
    p1 = 50000 / 13 * et * _nc * _ncb
    p2 = ac / _nbb
    hs, hc = math.sin(h), math.cos(h)
    gamma = 23 * (p2 + 0.305) * t / (23 * p1 + 11 * t * hc + 108 * t * hs)
    a, b = gamma * hc, gamma * hs
    ra = (460 * p2 + 451 * a + 288 * b) / 1403
    ga = (460 * p2 - 891 * a - 261 * b) / 1403
    ba = (460 * p2 - 220 * a - 6300 * b) / 1403

    def unadapt(v):
        m = max(0, 27.13 * abs(v) / (400 - abs(v)))
        return math.copysign(100 / _fl * m ** (1 / 0.42), v)

    rc, gc, bc = unadapt(ra) / _dr[0], unadapt(ga) / _dr[1], unadapt(ba) / _dr[2]
    x = 1.86206786 * rc - 1.01125463 * gc + 0.14918677 * bc
    y = 0.38752654 * rc + 0.62144744 * gc - 0.00897398 * bc
    z = -0.01584150 * rc - 0.03412294 * gc + 1.04996444 * bc
    return (x, y, z)


def hct_to_rgb(hue, chroma, tone):
    """Solve for sRGB with the given CAM16 hue/chroma and L* tone (clip chroma)."""
    if chroma < 0.0001 or tone < 0.0001 or tone > 99.9999:
        v = delin(y_from_lstar(max(0, min(100, tone))))
        return (v, v, v)
    y_target = y_from_lstar(tone)
    lo, hi = 0.0, chroma
    best = None

    def solve(c):
        # find J such that Y matches the tone, for chroma c
        jl, jh = 0.0, 100.0
        for _ in range(40):
            j = (jl + jh) / 2
            x, y, z = xyz_from_jch(j, c, hue)
            if y < y_target:
                jl = j
            else:
                jh = j
        return xyz_from_jch((jl + jh) / 2, c, hue)

    def in_gamut(xyz):
        rgb = [sum(M_XYZ2RGB[i][k] * xyz[k] for k in range(3)) for i in range(3)]
        return all(-0.5 <= v <= 100.5 for v in rgb), rgb

    ok, rgb = in_gamut(solve(chroma))
    if not ok:
        for _ in range(30):
            mid = (lo + hi) / 2
            ok, rgb = in_gamut(solve(mid))
            if ok:
                lo, best = mid, rgb
            else:
                hi = mid
        rgb = best if best else in_gamut(solve(0))[1]
    return tuple(delin(v) for v in rgb)


xyz_from_jch = from_jch


# ---- Material 3 scheme ---------------------------------------------------------
def palettes(source):
    hue, chroma, _ = cam16(hex_to_rgb(source))
    return {
        "primary": (hue, 36),
        "secondary": (hue, 16),
        "tertiary": ((hue + 60) % 360, 24),
        "neutral": (hue, 6),
        "neutral-variant": (hue, 8),
        "error": (25, 84),
    }


def tone(pal, name, t):
    h, c = pal[name]
    return rgb_to_hex(hct_to_rgb(h, c, t))


def scheme(source, dark):
    p = palettes(source)
    T = lambda n, t: tone(p, n, t)
    if not dark:
        return {
            "primary": T("primary", 40), "on-primary": T("primary", 100),
            "primary-container": T("primary", 90), "on-primary-container": T("primary", 10),
            "secondary": T("secondary", 40), "on-secondary": T("secondary", 100),
            "secondary-container": T("secondary", 90), "on-secondary-container": T("secondary", 10),
            "tertiary": T("tertiary", 40), "on-tertiary": T("tertiary", 100),
            "tertiary-container": T("tertiary", 90), "on-tertiary-container": T("tertiary", 10),
            "error": T("error", 40), "on-error": T("error", 100),
            "error-container": T("error", 90), "on-error-container": T("error", 10),
            "surface": T("neutral", 98), "on-surface": T("neutral", 10),
            "surface-dim": T("neutral", 87), "surface-bright": T("neutral", 98),
            "surface-container-lowest": T("neutral", 100), "surface-container-low": T("neutral", 96),
            "surface-container": T("neutral", 94), "surface-container-high": T("neutral", 92),
            "surface-container-highest": T("neutral", 90),
            "on-surface-variant": T("neutral-variant", 30), "outline": T("neutral-variant", 50),
            "outline-variant": T("neutral-variant", 80),
            "inverse-surface": T("neutral", 20), "inverse-on-surface": T("neutral", 95),
            "inverse-primary": T("primary", 80),
        }
    return {
        "primary": T("primary", 80), "on-primary": T("primary", 20),
        "primary-container": T("primary", 30), "on-primary-container": T("primary", 90),
        "secondary": T("secondary", 80), "on-secondary": T("secondary", 20),
        "secondary-container": T("secondary", 30), "on-secondary-container": T("secondary", 90),
        "tertiary": T("tertiary", 80), "on-tertiary": T("tertiary", 20),
        "tertiary-container": T("tertiary", 30), "on-tertiary-container": T("tertiary", 90),
        "error": T("error", 80), "on-error": T("error", 20),
        "error-container": T("error", 30), "on-error-container": T("error", 90),
        "surface": T("neutral", 6), "on-surface": T("neutral", 90),
        "surface-dim": T("neutral", 6), "surface-bright": T("neutral", 24),
        "surface-container-lowest": T("neutral", 4), "surface-container-low": T("neutral", 10),
        "surface-container": T("neutral", 12), "surface-container-high": T("neutral", 17),
        "surface-container-highest": T("neutral", 22),
        "on-surface-variant": T("neutral-variant", 80), "outline": T("neutral-variant", 60),
        "outline-variant": T("neutral-variant", 30),
        "inverse-surface": T("neutral", 90), "inverse-on-surface": T("neutral", 20),
        "inverse-primary": T("primary", 40),
    }


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    source = args[0]
    out = {"light": scheme(source, False), "dark": scheme(source, True)}
    if "--scss" in argv:
        for mode, roles in out.items():
            print(f"$m3-{mode}: (")
            print(",\n".join(f"  '{k}': {v}" for k, v in roles.items()))
            print(");\n")
    else:
        for mode, roles in out.items():
            print(f"[{mode}]")
            for k, v in roles.items():
                print(f"  {k:28s}{v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
