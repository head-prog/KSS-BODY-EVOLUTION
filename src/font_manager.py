"""
Font Manager — registers Unicode TTF/TTC fonts for Indic script PDF rendering.
Windows ships Nirmala.ttc which covers both Devanagari (Hindi) & Gujarati.
Falls back to downloading Noto fonts if Windows fonts are unavailable.
"""

import urllib.request
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_REGISTERED: dict = {}   # cache so we only register once

# ── Windows TTC candidates (subfont 0 = Regular, 1 = Bold) ───────────────────
# Nirmala.ttc is present on all modern Windows (10/11) installs.
# It covers Devanagari (Hindi), Gujarati, and many other Indic scripts.
_WIN_TTC_CANDIDATES = [
    Path("C:/Windows/Fonts/Nirmala.ttc"),     # Windows 10/11 — primary
]

# Fallback plain TTF candidates (no subfontIndex needed)
_WIN_TTF_CANDIDATES = [
    Path("C:/Windows/Fonts/Mangal.ttf"),      # Hindi/Devanagari only
    Path("C:/Windows/Fonts/Aparajita.ttf"),
    Path("C:/Windows/Fonts/Kokila.ttf"),
    Path("C:/Windows/Fonts/Utsaah.ttf"),
]

# Google Noto fonts (reliable Unicode TTF — no shaping dependencies for basic use)
_NOTO_DEVANAGARI_URL = (
    "https://github.com/googlefonts/noto-fonts/raw/main/"
    "hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
)
_NOTO_GUJARATI_URL = (
    "https://github.com/googlefonts/noto-fonts/raw/main/"
    "hinted/ttf/NotoSansGujarati/NotoSansGujarati-Regular.ttf"
)


def _assets_fonts_dir() -> Path:
    d = Path(__file__).parent.parent / "assets" / "fonts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            dest.write_bytes(resp.read())
        return dest.exists() and dest.stat().st_size > 10_000
    except Exception:
        return False


def _register_ttc(path: Path, font_name: str, bold_name: str) -> bool:
    """Try to register a TTC file. Returns True on success."""
    try:
        pdfmetrics.registerFont(TTFont(font_name, str(path), subfontIndex=0))
        pdfmetrics.registerFont(TTFont(bold_name,  str(path), subfontIndex=1))
        pdfmetrics.registerFontFamily(font_name, normal=font_name, bold=bold_name,
                                      italic=font_name, boldItalic=bold_name)
        return True
    except Exception:
        try:
            # Some TTCs only have 1 valid subfont
            pdfmetrics.registerFont(TTFont(font_name, str(path), subfontIndex=0))
            pdfmetrics.registerFontFamily(font_name, normal=font_name, bold=font_name,
                                          italic=font_name, boldItalic=font_name)
            return True
        except Exception:
            return False


def _register_ttf(path: Path, font_name: str) -> bool:
    """Try to register a plain TTF file. Returns True on success."""
    try:
        pdfmetrics.registerFont(TTFont(font_name, str(path)))
        pdfmetrics.registerFontFamily(font_name, normal=font_name, bold=font_name,
                                      italic=font_name, boldItalic=font_name)
        return True
    except Exception:
        return False


def get_font_for_language(language: str) -> str:
    """
    Return a ReportLab font name suitable for the given language.
    Returns 'Helvetica' for English (built-in, no registration needed).
    For Hindi / Gujarati, registers and returns a Unicode TTF/TTC font name.
    """
    if language == "English":
        return "Helvetica"

    cache_key = "indic"
    if cache_key in _REGISTERED:
        return _REGISTERED[cache_key]

    # 1 ── Windows TTC fonts (Nirmala.ttc covers Hindi + Gujarati)
    for p in _WIN_TTC_CANDIDATES:
        if p.exists():
            if _register_ttc(p, "IndicFont", "IndicFont-Bold"):
                _REGISTERED[cache_key] = "IndicFont"
                return "IndicFont"

    # 2 ── Windows plain TTF fonts
    for p in _WIN_TTF_CANDIDATES:
        if p.exists():
            if _register_ttf(p, "IndicFont"):
                _REGISTERED[cache_key] = "IndicFont"
                return "IndicFont"

    # 3 ── Download Noto fonts (language-specific)
    fonts_dir = _assets_fonts_dir()
    url = _NOTO_GUJARATI_URL if language == "Gujarati" else _NOTO_DEVANAGARI_URL
    fname = "NotoSansGujarati-Regular.ttf" if language == "Gujarati" else "NotoSansDevanagari-Regular.ttf"
    local = fonts_dir / fname

    if not local.exists():
        _download(url, local)

    if local.exists():
        if _register_ttf(local, "IndicFont"):
            _REGISTERED[cache_key] = "IndicFont"
            return "IndicFont"

    # 4 ── Absolute fallback (PDF won't crash but Indic chars will be blank)
    _REGISTERED[cache_key] = "Helvetica"
    return "Helvetica"
