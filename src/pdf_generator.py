"""
PDF Report Generation Module
Generates A4-formatted printable wellness reports in English, Hindi, and Gujarati.
All platforms → PIL + HarfBuzz + FreeType image-based PDF (proper Indic glyph shaping).
Fonts: Windows system fonts (Nirmala.ttc) OR auto-downloaded Noto fonts (cloud-safe).
Fallback → ReportLab PDF if Pillow is not installed.
"""

from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
import os
import re
import urllib.request
import platform
from pathlib import Path

from font_manager import get_font_for_language


# ──────────────────────────────────────────────────────────────────────────────
# PLATFORM — try PIL+HarfBuzz rendering everywhere; fall back to ReportLab only
# if Pillow is not installed.  uharfbuzz + freetype-py are cross-platform.
# ──────────────────────────────────────────────────────────────────────────────
_IS_WINDOWS = platform.system() == "Windows"
try:
    from PIL import Image as _pil_test
    _USE_PIL = True
except ImportError:
    _USE_PIL = False


# ── Label dictionaries ────────────────────────────────────────────────────────
_LABELS = {
    "English": {
        "report_title":    "Wellness Evaluation Report",
        "patient_info":    "Patient Information",
        "name":            "Name",
        "patient_id":      "Patient ID",
        "age":             "Age",
        "gender":          "Gender",
        "height":          "Height",
        "mobile":          "Mobile",
        "area":            "Area",
        "email":           "Email",
        "years":           "years",
        "cm":              "cm",
        "metrics_title":   "Body Composition & Health Metrics",
        "metric":          "Metric",
        "value":           "Value",
        "category":        "Category",
        "status":          "Status",
        "risk_title":      "Risk Assessment Summary",
        "overall_risk":    "Overall Risk Level",
        "wellness_score":  "Wellness Score",
        "key_findings":    "Key Findings",
        "bmi_status":      "BMI Status",
        "body_fat_lbl":    "Body Fat",
        "visceral_fat_lbl": "Visceral Fat",
        "muscle_mass_lbl": "Muscle Mass",
        "body_age_lbl":    "Body Age Status",
        "ai_title":        "Wellness Analysis & Recommendations",
        "report_date":     "Report Date",
        "report_id":       "Report ID",
        "footer_generated": "Report Generated",
        "disclaimer_title": "Disclaimer",
        "disclaimer_body": (
            "This wellness report is for informational purposes only. "
            "It is not a medical diagnosis and does not replace professional medical advice. "
            "Please consult with a qualified healthcare professional for any health concerns."
        ),
        "higher_risk":     "Higher score = Higher risk",
        "male":            "Male",
        "female":          "Female",
    },
    "Hindi": {
        "report_title":    "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u092e\u0942\u0932\u094d\u092f\u093e\u0902\u0915\u0928 \u0930\u093f\u092a\u094b\u0930\u094d\u091f",
        "patient_info":    "\u0930\u094b\u0917\u0940 \u0915\u0940 \u091c\u093e\u0928\u0915\u093e\u0930\u0940",
        "name":            "\u0928\u093e\u092e",
        "patient_id":      "\u0930\u094b\u0917\u0940 ID",
        "age":             "\u0909\u092e\u094d\u0930",
        "gender":          "\u0932\u093f\u0902\u0917",
        "height":          "\u090a\u0902\u091a\u093e\u0908",
        "mobile":          "\u092e\u094b\u092c\u093e\u0907\u0932",
        "area":            "\u0915\u094d\u0937\u0947\u0924\u094d\u0930",
        "email":           "\u0908\u092e\u0947\u0932",
        "years":           "\u0935\u0930\u094d\u0937",
        "cm":              "\u0938\u0947\u092e\u0940",
        "metrics_title":   "\u0936\u0930\u0940\u0930 \u0938\u0902\u0930\u091a\u0928\u093e \u0914\u0930 \u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u092e\u093e\u092a\u0926\u0902\u0921",
        "metric":          "\u092e\u093e\u092a\u0926\u0902\u0921",
        "value":           "\u092e\u093e\u0928",
        "category":        "\u0936\u094d\u0930\u0947\u0923\u0940",
        "status":          "\u0938\u094d\u0925\u093f\u0924\u093f",
        "risk_title":      "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u091c\u094b\u0916\u093f\u092e \u0938\u093e\u0930\u093e\u0902\u0936",
        "overall_risk":    "\u0915\u0941\u0932 \u091c\u094b\u0916\u093f\u092e \u0938\u094d\u0924\u0930",
        "wellness_score":  "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u0938\u094d\u0915\u094b\u0930",
        "key_findings":    "\u092e\u0941\u0916\u094d\u092f \u0928\u093f\u0937\u094d\u0915\u0930\u094d\u0937",
        "bmi_status":      "BMI \u0938\u094d\u0925\u093f\u0924\u093f",
        "body_fat_lbl":    "\u0936\u0930\u0940\u0930 \u0915\u0940 \u091a\u0930\u094d\u092c\u0940",
        "visceral_fat_lbl": "\u0906\u0902\u0924\u0930\u093f\u0915 \u091a\u0930\u094d\u092c\u0940",
        "muscle_mass_lbl": "\u092e\u093e\u0902\u0938\u092a\u0947\u0936\u093f\u092f\u093e\u0902",
        "body_age_lbl":    "\u0936\u0930\u0940\u0930 \u0915\u0940 \u0909\u092e\u094d\u0930 \u0938\u094d\u0925\u093f\u0924\u093f",
        "ai_title":        "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f \u0935\u093f\u0936\u094d\u0932\u0947\u0937\u0923 \u0914\u0930 \u0938\u0941\u091d\u093e\u0935",
        "report_date":     "\u0930\u093f\u092a\u094b\u0930\u094d\u091f \u0924\u093e\u0930\u0940\u0916",
        "report_id":       "\u0930\u093f\u092a\u094b\u0930\u094d\u091f ID",
        "footer_generated": "\u0930\u093f\u092a\u094b\u0930\u094d\u091f \u0924\u0948\u092f\u093e\u0930",
        "disclaimer_title": "\u0905\u0938\u094d\u0935\u0940\u0915\u0930\u0923",
        "disclaimer_body": (
            "\u092f\u0939 \u0930\u093f\u092a\u094b\u0930\u094d\u091f \u0915\u0947\u0935\u0932 \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0915\u0947 \u0932\u093f\u090f \u0939\u0948\u0964 "
            "\u092f\u0939 \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e \u0928\u093f\u0926\u093e\u0928 \u0928\u0939\u0940\u0902 \u0939\u0948\u0964 "
            "\u0915\u0943\u092a\u092f\u093e \u092f\u094b\u0917\u094d\u092f \u0921\u093e\u0915\u094d\u091f\u0930 \u0938\u0947 \u0938\u0932\u093e\u0939 \u0932\u0947\u0902\u0964"
        ),
        "higher_risk":     "\u0905\u0927\u093f\u0915 \u0938\u094d\u0915\u094b\u0930 = \u0905\u0927\u093f\u0915 \u091c\u094b\u0916\u093f\u092e",
        "male":            "\u092a\u0941\u0930\u0941\u0937",
        "female":          "\u092e\u0939\u093f\u0932\u093e",
    },
    "Gujarati": {
        "report_title":    "\u0ab8\u0acd\u0ab5\u0abe\u0ab8\u0acd\u0aa5\u0acd\u0aaf \u0aae\u0ac2\u0ab2\u0acd\u0aaf\u0abe\u0a82\u0a95\u0aa8 \u0a85\u0ab9\u0ac7\u0ab5\u0abe\u0ab2",
        "patient_info":    "\u0aa6\u0ab0\u0acd\u0aa6\u0ac0\u0aa8\u0ac0 \u0aae\u0abe\u0ab9\u0abf\u0aa4\u0ac0",
        "name":            "\u0aa8\u0abe\u0aae",
        "patient_id":      "\u0aa6\u0ab0\u0acd\u0aa6\u0ac0 ID",
        "age":             "\u0a89\u0a82\u0aae\u0ab0",
        "gender":          "\u0a9c\u0abe\u0aa4\u0abf",
        "height":          "\u0a8a\u0a9a\u0abe\u0a88",
        "mobile":          "\u0aae\u0acb\u0aac\u0abe\u0a87\u0ab2",
        "area":            "\u0ab5\u0abf\u0ab8\u0acd\u0aa4\u0abe\u0ab0",
        "email":           "\u0a88-\u0aae\u0ac7\u0a87\u0ab2",
        "years":           "\u0ab5\u0ab0\u0acd\u0ab7",
        "cm":              "\u0ab8\u0ac7.\u0aae\u0ac0.",
        "metrics_title":   "\u0ab6\u0abe\u0ab0\u0ac0\u0ab0\u0abf\u0a95 \u0aac\u0a82\u0aa7\u0abe\u0ab0\u0aa3 \u0a85\u0aa8\u0ac7 \u0ab8\u0acd\u0ab5\u0abe\u0ab8\u0acd\u0aa5\u0acd\u0aaf \u0aae\u0abe\u0aaa",
        "metric":          "\u0aae\u0abe\u0aaa",
        "value":           "\u0aae\u0ac2\u0ab2\u0acd\u0aaf",
        "category":        "\u0ab6\u0acd\u0ab0\u0ac7\u0aa3\u0ac0",
        "status":          "\u0ab8\u0acd\u0aa5\u0abf\u0aa4\u0abf",
        "risk_title":      "\u0ab8\u0acd\u0ab5\u0abe\u0ab8\u0acd\u0aa5\u0acd\u0aaf \u0a9c\u0acb\u0a96\u0aae \u0ab8\u0abe\u0ab0\u0abe\u0a82\u0ab6",
        "overall_risk":    "\u0a95\u0ac1\u0ab2 \u0a9c\u0acb\u0a96\u0aae \u0ab8\u0acd\u0aa4\u0ab0",
        "wellness_score":  "\u0ab8\u0acd\u0ab5\u0abe\u0ab8\u0acd\u0aa5\u0acd\u0aaf \u0ab8\u0acd\u0a95\u0acb\u0ab0",
        "key_findings":    "\u0aae\u0ac1\u0a96\u0acd\u0aaf \u0aa4\u0abe\u0ab0\u0aa3\u0acb",
        "bmi_status":      "BMI \u0ab8\u0acd\u0aa5\u0abf\u0aa4\u0abf",
        "body_fat_lbl":    "\u0ab6\u0ab0\u0ac0\u0ab0\u0aa8\u0ac0 \u0a9a\u0ab0\u0aac\u0ac0",
        "visceral_fat_lbl": "\u0a86\u0a82\u0aa4\u0ab0\u0abf\u0a95 \u0a9a\u0ab0\u0aac\u0ac0",
        "muscle_mass_lbl": "\u0ab8\u0acd\u0aa8\u0abe\u0aaf\u0ac1",
        "body_age_lbl":    "\u0ab6\u0ab0\u0ac0\u0ab0\u0aa8\u0ac0 \u0a89\u0a82\u0aae\u0ab0 \u0ab8\u0acd\u0aa5\u0abf\u0aa4\u0abf",
        "ai_title":        "\u0ab8\u0acd\u0ab5\u0abe\u0ab8\u0acd\u0aa5\u0acd\u0aaf \u0ab5\u0abf\u0ab6\u0acd\u0ab2\u0ac7\u0ab7\u0aa3 \u0a85\u0aa8\u0ac7 \u0ab8\u0ac2\u0a9a\u0aa8\u0acb",
        "report_date":     "\u0a85\u0ab9\u0ac7\u0ab5\u0abe\u0ab2 \u0aa4\u0abe\u0ab0\u0ac0\u0a96",
        "report_id":       "\u0a85\u0ab9\u0ac7\u0ab5\u0abe\u0ab2 ID",
        "footer_generated": "\u0a85\u0ab9\u0ac7\u0ab5\u0abe\u0ab2 \u0aa4\u0ac8\u0aaf\u0abe\u0ab0",
        "disclaimer_title": "\u0a85\u0ab8\u0acd\u0ab5\u0ac0\u0a95\u0ac3\u0aa4\u0abf",
        "disclaimer_body": (
            "\u0a86 \u0a85\u0ab9\u0ac7\u0ab5\u0abe\u0ab2 \u0aab\u0a95\u0acd\u0aa4 \u0aae\u0abe\u0ab9\u0abf\u0aa4\u0ac0 \u0aae\u0abe\u0a9f\u0ac7 \u0a9b\u0ac7. "
            "\u0a86 \u0a95\u0acb\u0a88 \u0aa4\u0aac\u0ac0\u0aac\u0ac0 \u0aa8\u0abf\u0aa6\u0abe\u0aa8 \u0aa8\u0aa5\u0ac0. "
            "\u0a95\u0ac3\u0aaa\u0abe \u0aaf\u0acb\u0a97\u0acd\u0aaf \u0aa1\u0ac9\u0a95\u0acd\u0a9f\u0ab0\u0aa8\u0ac0 \u0ab8\u0ab2\u0abe\u0ab9 \u0ab2\u0acb."
        ),
        "higher_risk":     "\u0ab5\u0aa7\u0abe\u0ab0\u0ac7 \u0ab8\u0acd\u0a95\u0acb\u0ab0 = \u0ab5\u0aa7\u0abe\u0ab0\u0ac7 \u0a9c\u0acb\u0a96\u0aae",
        "male":            "\u0aaa\u0ac1\u0ab0\u0ac1\u0ab7",
        "female":          "\u0ab8\u0acd\u0aa4\u0acd\u0ab0\u0ac0",
    },
}

def _translate_gender(value: str, lbl: dict) -> str:
    """Return translated gender value using the current language's label dict."""
    v = str(value).strip().lower()
    if v == "male":
        return lbl.get("male", value)
    if v == "female":
        return lbl.get("female", value)
    return value


# ── Category-string translations (English RuleEngine → Hindi / Gujarati) ─────
# The RuleEngine always returns English category labels.  These are displayed
# in the metrics table and risk-summary section of the PDF.  We translate them
# here so Indic-language reports never show English status strings.
_CATEGORY_TR = {
    "Hindi": {
        # BMI
        "Normal Weight":     "\u0938\u093e\u092e\u093e\u0928\u094d\u092f \u0935\u091c\u0928",
        "Underweight":       "\u0915\u092e \u0935\u091c\u0928",
        "Overweight":        "\u0905\u0927\u093f\u0915 \u0935\u091c\u0928",
        "Obesity Grade 1":   "\u092e\u094b\u091f\u093e\u092a\u093e \u0917\u094d\u0930\u0947\u0921 1",
        "High Obesity Risk": "\u0909\u091a\u094d\u091a \u092e\u094b\u091f\u093e\u092a\u093e \u091c\u094b\u0916\u093f\u092e",
        # Visceral / body fat / muscle
        "Normal":            "\u0938\u093e\u092e\u093e\u0928\u094d\u092f",
        "High":              "\u0909\u091a\u094d\u091a",
        "Very High Risk":    "\u0905\u0924\u094d\u092f\u0927\u093f\u0915 \u091c\u094b\u0916\u093f\u092e",
        "Low (Lean)":        "\u0915\u092e (\u0926\u0941\u092c\u0932\u093e)",
        "Moderate":          "\u092e\u0927\u094d\u092f\u092e",
        "High Risk":         "\u0909\u091a\u094d\u091a \u091c\u094b\u0916\u093f\u092e",
        "Low":               "\u0915\u092e",
        "High (Athletic)":   "\u0909\u091a\u094d\u091a (\u090f\u0925\u0932\u0947\u091f\u093f\u0915)",
        # Overall risk
        "Low Risk":          "\u0915\u092e \u091c\u094b\u0916\u093f\u092e",
        "Moderate Risk":     "\u092e\u0927\u094d\u092f\u092e \u091c\u094b\u0916\u093f\u092e",
        # Body age
        "Excellent (5+ years younger)":            "\u0909\u0924\u094d\u0915\u0943\u0937\u094d\u091f (5+ \u0935\u0930\u094d\u0937 \u092f\u0941\u0935\u093e)",
        "Good (younger than actual age)":          "\u0905\u091a\u094d\u091b\u093e (\u0935\u093e\u0938\u094d\u0924\u0935\u093f\u0915 \u0909\u092e\u094d\u0930 \u0938\u0947 \u092f\u0941\u0935\u093e)",
        "Matched with actual age":                 "\u0935\u093e\u0938\u094d\u0924\u0935\u093f\u0915 \u0909\u092e\u094d\u0930 \u0915\u0947 \u0938\u092e\u093e\u0928",
        "Slightly elevated (up to 5 years older)": "\u0925\u094b\u095c\u093e \u0905\u0927\u093f\u0915 (5 \u0935\u0930\u094d\u0937 \u0924\u0915)",
        "Significantly elevated (5+ years older)": "\u0915\u093e\u092b\u0940 \u0905\u0927\u093f\u0915 (5+ \u0935\u0930\u094d\u0937)",
    },
    "Gujarati": {
        # BMI
        "Normal Weight":     "\u0ab8\u0abe\u0aae\u0abe\u0aa8\u0acd\u0aaf \u0ab5\u0a9c\u0aa8",
        "Underweight":       "\u0a93\u0a9b\u0ac1\u0a82 \u0ab5\u0a9c\u0aa8",
        "Overweight":        "\u0ab5\u0aa7\u0ac1 \u0ab5\u0a9c\u0aa8",
        "Obesity Grade 1":   "\u0ab8\u0acd\u0aa5\u0ac2\u0ab3\u0aa4\u0abe \u0a97\u0acd\u0ab0\u0ac7\u0aa1 1",
        "High Obesity Risk": "\u0ab5\u0aa7\u0abe\u0ab0\u0ac7 \u0ab8\u0acd\u0aa5\u0ac2\u0ab3\u0aa4\u0abe \u0a9c\u0acb\u0a96\u0aae",
        # Visceral / body fat / muscle
        "Normal":            "\u0ab8\u0abe\u0aae\u0abe\u0aa8\u0acd\u0aaf",
        "High":              "\u0a89\u0a9a\u0acd\u0a9a",
        "Very High Risk":    "\u0a96\u0ac2\u0aac \u0a89\u0a9a\u0acd\u0a9a \u0a9c\u0acb\u0a96\u0aae",
        "Low (Lean)":        "\u0a93\u0a9b\u0ac1\u0a82 (\u0aa6\u0ac1\u0aac\u0ab3\u0ac1\u0a82)",
        "Moderate":          "\u0aae\u0aa7\u0acd\u0aaf\u0aae",
        "High Risk":         "\u0a89\u0a9a\u0acd\u0a9a \u0a9c\u0acb\u0a96\u0aae",
        "Low":               "\u0a93\u0a9b\u0ac1\u0a82",
        "High (Athletic)":   "\u0a89\u0a9a\u0acd\u0a9a (\u0a8f\u0aa5\u0acd\u0ab2\u0ac7\u0a9f\u0abf\u0a95)",
        # Overall risk
        "Low Risk":          "\u0a93\u0a9b\u0ac1\u0a82 \u0a9c\u0acb\u0a96\u0aae",
        "Moderate Risk":     "\u0aae\u0aa7\u0acd\u0aaf\u0aae \u0a9c\u0acb\u0a96\u0aae",
        # Body age
        "Excellent (5+ years younger)":            "\u0a89\u0aa4\u0acd\u0a95\u0ac3\u0ab7\u0acd\u0a9f (5+ \u0ab5\u0ab0\u0acd\u0ab7 \u0aaf\u0ac1\u0ab5\u0abe\u0aa8)",
        "Good (younger than actual age)":          "\u0ab8\u0abe\u0ab0\u0ac1\u0a82 (\u0ab5\u0abe\u0ab8\u0acd\u0aa4\u0ab5\u0abf\u0a95 \u0a89\u0a82\u0aae\u0ab0\u0aa5\u0ac0 \u0aaf\u0ac1\u0ab5\u0abe\u0aa8)",
        "Matched with actual age":                 "\u0ab5\u0abe\u0ab8\u0acd\u0aa4\u0ab5\u0abf\u0a95 \u0a89\u0a82\u0aae\u0ab0 \u0ab8\u0aae\u0abe\u0aa8",
        "Slightly elevated (up to 5 years older)": "\u0aa5\u0acb\u0aa1\u0ac1\u0a82 \u0ab5\u0aa7\u0ac1 (5 \u0ab5\u0ab0\u0acd\u0ab7 \u0ab8\u0ac1\u0aa7\u0ac0)",
        "Significantly elevated (5+ years older)": "\u0a96\u0ac2\u0aac \u0ab5\u0aa7\u0ac1 (5+ \u0ab5\u0ab0\u0acd\u0ab7)",
    },
}


def _translate_cat(value: str, language: str) -> str:
    """Return the localized category string, or the original if no translation found."""
    if str(value) in ("Not Measured", "N/A", "-"):
        return str(value)  # keep as-is (language-neutral)
    tr = _CATEGORY_TR.get(language, {})
    return tr.get(str(value), str(value))


# ── PIL-based renderer for Hindi / Gujarati ───────────────────────────────────
class IndicPDFRenderer:
    """
    Renders Hindi/Gujarati wellness reports using Pillow.
    Text is shaped with HarfBuzz (uharfbuzz) and rasterized with FreeType
    (freetype-py) for correct Indic conjuncts, matras, and ligatures.
    Output: image-based multi-page PDF via PIL's built-in PDF writer.
    """
    # A4 at 150 DPI
    PW, PH = 1240, 1754
    DPI    = 150
    MG     = 65     # margin in pixels

    RED   = (196, 18,  47)
    GOLD  = (226, 168, 34)
    DARK  = (26,  10,  15)
    LIGHT = (251, 248, 244)
    WHITE = (255, 255, 255)
    GREY  = (140, 140, 140)
    LGREY = (220, 213, 204)

    # ── Font resolution (Windows + cloud/Linux) ─────────────────────────────
    @staticmethod
    def _resolve_font(language: str = "English"):
        """
        Returns (font_path, font_index) for the requested language.
        Priority:
          1. Windows system fonts  (local dev)
          2. assets/fonts/ Noto   (bundled — cloud-safe)
          3. Auto-download Noto   (first run on a fresh cloud instance)
        Returns (None, 0) if everything fails — caller uses load_default().
        """
        fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"

        if language == "Hindi":
            windows_candidates = [("C:/Windows/Fonts/Nirmala.ttc", 0)]
            noto_filename = "NotoSansDevanagari-Regular.ttf"
            noto_url = ("https://github.com/googlefonts/noto-fonts/raw/main/"
                        "hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf")
        elif language == "Gujarati":
            windows_candidates = [("C:/Windows/Fonts/Nirmala.ttc", 0)]
            noto_filename = "NotoSansGujarati-Regular.ttf"
            noto_url = ("https://github.com/googlefonts/noto-fonts/raw/main/"
                        "hinted/ttf/NotoSansGujarati/NotoSansGujarati-Regular.ttf")
        else:  # English and any other
            windows_candidates = [
                ("C:/Windows/Fonts/arial.ttf",   0),
                ("C:/Windows/Fonts/Nirmala.ttc", 0),
            ]
            noto_filename = "NotoSans-Regular.ttf"
            noto_url = ("https://github.com/googlefonts/noto-fonts/raw/main/"
                        "hinted/ttf/NotoSans/NotoSans-Regular.ttf")

        # 1. Windows system fonts
        for fp, idx in windows_candidates:
            if os.path.exists(fp):
                return fp, idx

        # 2. Bundled assets/fonts/
        bundled = fonts_dir / noto_filename
        if bundled.exists():
            return str(bundled), 0

        # 3. Auto-download Noto font
        try:
            fonts_dir.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(
                noto_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            if len(data) > 10_000:
                bundled.write_bytes(data)
                return str(bundled), 0
        except Exception:
            pass

        return None, 0  # Caller must use ImageFont.load_default()

    @staticmethod
    def _resolve_bold_font(language: str = "English"):
        """
        Returns (bold_font_path, font_index) for the bold variant.
        Nirmala.ttc index 1 is NirmalaBold on Windows (covers Hindi & Gujarati).
        Falls back to bundled Noto Bold, then auto-download, then None.
        """
        fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"

        if language in ("Hindi", "Gujarati"):
            windows_candidates = [("C:/Windows/Fonts/Nirmala.ttc", 1)]  # index 1 = bold
            noto_filename = (
                "NotoSansDevanagari-Bold.ttf" if language == "Hindi"
                else "NotoSansGujarati-Bold.ttf"
            )
            noto_url = (
                "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/"
                "NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
                if language == "Hindi" else
                "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/"
                "NotoSansGujarati/NotoSansGujarati-Bold.ttf"
            )
        else:
            windows_candidates = [
                ("C:/Windows/Fonts/arialbd.ttf", 0),
                ("C:/Windows/Fonts/Nirmala.ttc", 1),
            ]
            noto_filename = "NotoSans-Bold.ttf"
            noto_url = ("https://github.com/googlefonts/noto-fonts/raw/main/"
                        "hinted/ttf/NotoSans/NotoSans-Bold.ttf")

        for fp, idx in windows_candidates:
            if os.path.exists(fp):
                return fp, idx

        bundled = fonts_dir / noto_filename
        if bundled.exists():
            return str(bundled), 0

        try:
            fonts_dir.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(noto_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            if len(data) > 10_000:
                bundled.write_bytes(data)
                return str(bundled), 0
        except Exception:
            pass

        return None, 0  # Caller falls back to regular font

    def render(self, patient, health_record, health_categories, ai_analysis, lbl,
               language: str = "English"):
        from PIL import Image, ImageDraw, ImageFont
        self._language = language  # stored so section helpers can localize categories
        font_path, font_index = self._resolve_font(language)
        bold_path, bold_index = self._resolve_bold_font(language)
        try:
            if font_path is None:
                raise OSError("No font found")
            f_sm = ImageFont.truetype(font_path, 22, index=font_index)
            f_md = ImageFont.truetype(font_path, 27, index=font_index)
            f_lg = ImageFont.truetype(font_path, 35, index=font_index)
            f_xl = ImageFont.truetype(font_path, 46, index=font_index)
            # Bold variants — fall back to regular font if bold unavailable
            _bp = bold_path if bold_path else font_path
            _bi = bold_index if bold_path else font_index
            f_sm_b = ImageFont.truetype(_bp, 22, index=_bi)
            f_md_b = ImageFont.truetype(_bp, 27, index=_bi)
        except Exception:
            f_sm = f_md = f_lg = f_xl = ImageFont.load_default()
            f_sm_b = f_md_b = f_sm
        fonts = {"sm": f_sm, "md": f_md, "lg": f_lg, "xl": f_xl,
                 "sm_b": f_sm_b, "md_b": f_md_b}

        # ── HarfBuzz shaping setup (Gujarati / Hindi only) ────────────────────
        self._font_bytes  = None     # raw bytes for HarfBuzz face construction
        self._font_meta   = {}       # id(pil_font) → (px_size, font_path, font_index)
        self._current_img = None     # active PIL Image for glyph compositing
        _fp   = font_path   or ""
        self._font_path = _fp        # used as cache-key in _draw_shaped / _shaped_width
        _bp_r = bold_path   or font_path or ""
        _bi_r = bold_index  if bold_path else font_index
        if _fp and language != "English":
            with open(_fp, "rb") as _fh:
                self._font_bytes = _fh.read()
        self._font_meta = {
            id(f_sm):   (22, _fp,   font_index),
            id(f_md):   (27, _fp,   font_index),
            id(f_lg):   (35, _fp,   font_index),
            id(f_xl):   (46, _fp,   font_index),
            id(f_sm_b): (22, _bp_r, _bi_r),
            id(f_md_b): (27, _bp_r, _bi_r),
        }

        pages = [self._page1(patient, health_record, health_categories, lbl, fonts)]
        pages += self._ai_pages(ai_analysis, lbl, fonts)

        buf = BytesIO()
        pages[0].save(buf, format="PDF", resolution=self.DPI,
                      save_all=True, append_images=pages[1:])
        buf.seek(0)
        return buf.getvalue()

    # ── Page 1: header + patient info + metrics + risk ────────────────────────
    def _page1(self, patient, health_record, health_categories, lbl, fonts):
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (self.PW, self.PH), self.WHITE)
        self._current_img = img
        d   = ImageDraw.Draw(img)
        y   = self.MG

        # Red header bar
        d.rectangle([0, y, self.PW, y + 96], fill=self.RED)
        # Logo on left side of header
        _logo_path = Path(__file__).parent.parent / "assets" / "volunteers kss insta profil pic.png"
        if _logo_path.exists():
            try:
                _logo = Image.open(str(_logo_path)).convert("RGBA")
                _lh = 88
                _lw = int(_logo.width * _lh / _logo.height)
                _logo = _logo.resize((_lw, _lh), Image.LANCZOS)
                img.paste(_logo, (self.MG, y + 4), _logo)
            except Exception:
                pass
        self._center(d, "KSS Body Evolution Wellness Center", y + 26, fonts["lg"], self.WHITE)
        y += 108

        # Report title
        self._center(d, lbl["report_title"], y, fonts["xl"], self.RED)
        y += 62

        # Date / ID line
        self._txt(d, f"{lbl['report_date']}: {datetime.now().strftime('%d %B %Y')}", y, fonts["sm"], self.DARK)
        self._txt(d, f"{lbl['report_id']}: {health_record.get('id','N/A')}", y, fonts["sm"], self.DARK, right=True)
        y += 34
        d.rectangle([self.MG, y, self.PW - self.MG, y + 3], fill=self.RED)
        y += 20

        y = self._section_patient(d, patient, lbl, fonts, y)
        d.rectangle([self.MG, y, self.PW - self.MG, y + 3], fill=self.RED)
        y += 20

        y = self._section_metrics(d, health_record, health_categories, lbl, fonts, y)
        d.rectangle([self.MG, y, self.PW - self.MG, y + 3], fill=self.RED)
        y += 20

        if y + 280 < self.PH - self.MG:
            self._section_risk(d, health_categories, lbl, fonts, y)

        self._footer(d, lbl, fonts)
        return img

    # ── AI analysis pages ─────────────────────────────────────────────────────
    def _ai_pages(self, ai_analysis, lbl, fonts):
        from PIL import Image, ImageDraw
        pages = []
        img = Image.new("RGB", (self.PW, self.PH), self.WHITE)
        self._current_img = img
        d   = ImageDraw.Draw(img)

        d.rectangle([0, self.MG, self.PW, self.MG + 60], fill=self.RED)
        self._center(d, lbl["ai_title"], self.MG + 13, fonts["lg"], self.WHITE)
        d.rectangle([self.MG, self.MG + 66, self.PW - self.MG, self.MG + 69], fill=self.GOLD)
        y = self.MG + 86
        max_y = self.PH - self.MG - 55

        def new_page():
            nonlocal img, d, y
            self._footer(d, lbl, fonts)
            pages.append(img)
            img = Image.new("RGB", (self.PW, self.PH), self.WHITE)
            self._current_img = img
            d   = ImageDraw.Draw(img)
            y   = self.MG + 20

        for raw in ai_analysis.split("\n"):
            line = raw.strip()
            if not line:
                y += 24; continue

            if y > max_y:
                new_page()

            if line.startswith("## "):
                y += 20
                if y > max_y: new_page()
                d.rectangle([self.MG, y, self.PW - self.MG, y + 48], fill=self.RED)
                # Strip ** markers from headings (already visually prominent)
                heading_text = re.sub(r'\*\*(.+?)\*\*', r'\1', line[3:])
                self._txt(d, heading_text, y + 11, fonts["md"], self.WHITE, x=self.MG + 16)
                y += 66

            elif line.startswith("* ") or line.startswith("- "):
                bullet_content = "\u2022  " + line[2:]
                for wl in self._wrap(d, bullet_content, fonts["sm"], self.PW - 2*self.MG - 30):
                    if y > max_y: new_page()
                    self._draw_rich_line(d, wl, y, fonts["sm"], fonts["sm_b"],
                                         self.DARK, x=self.MG + 22)
                    y += 36

            elif len(line) > 2 and line[0].isdigit() and line[1] in ".)": 
                y += 16
                if y > max_y: new_page()
                d.rectangle([self.MG, y, self.PW - self.MG, y + 44], fill=self.LIGHT)
                # Strip ** markers from numbered headers (bold colour already highlights them)
                numbered_text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                self._txt(d, numbered_text, y + 10, fonts["md"], self.RED, x=self.MG + 12)
                y += 62

            else:
                for wl in self._wrap(d, line, fonts["sm"], self.PW - 2*self.MG):
                    if y > max_y: new_page()
                    self._draw_rich_line(d, wl, y, fonts["sm"], fonts["sm_b"],
                                         self.DARK, x=self.MG)
                    y += 34

        self._footer(d, lbl, fonts)
        pages.append(img)
        return pages

    # ── Section helpers ────────────────────────────────────────────────────────
    def _section_patient(self, d, patient, lbl, fonts, y):
        self._txt(d, lbl["patient_info"], y, fonts["lg"], self.RED)
        y += 44
        col2 = self.PW // 2
        RH   = 46
        rows = [
            (lbl["name"],   str(patient.get("name","N/A")),
             lbl["patient_id"], str(patient.get("patient_id","N/A"))),
            (lbl["age"],    f"{patient.get('age','N/A')} {lbl['years']}",
             lbl["gender"], _translate_gender(patient.get("gender","N/A"), lbl)),
            (lbl["height"], f"{patient.get('height','N/A')} {lbl['cm']}",
             lbl["mobile"], str(patient.get("mobile","N/A"))),
            (lbl["area"],   str(patient.get("area","N/A")),
             lbl["email"],  str(patient.get("email","N/A") or "N/A")),
        ]
        total = RH * len(rows) + 20
        d.rectangle([self.MG-4, y-4, self.PW-self.MG+4, y+total],
                    fill=self.LIGHT, outline=self.LGREY)
        for i, (l1, v1, l2, v2) in enumerate(rows):
            ry = y + 12 + i * RH
            self._txt(d, f"{l1}: {v1}", ry, fonts["md"], self.DARK, x=self.MG+14)
            self._txt(d, f"{l2}: {v2}", ry, fonts["md"], self.DARK, x=col2+14)
        return y + total + 20

    def _section_metrics(self, d, hr, hc, lbl, fonts, y):
        self._txt(d, lbl["metrics_title"], y, fonts["lg"], self.RED)
        y += 44
        CW = [380, 155, 305, 100]
        CX = [self.MG]
        for w in CW[:-1]: CX.append(CX[-1] + w)
        RH = 42

        d.rectangle([self.MG, y, self.PW-self.MG, y+RH], fill=self.RED)
        for i, h in enumerate([lbl["metric"], lbl["value"], lbl["category"], lbl["status"]]):
            self._txt(d, h, y+11, fonts["sm"], self.WHITE, x=CX[i]+8)
        y += RH

        def st(cat):
            if not cat: return "ok"
            c = str(cat).lower()
            if "not measured" in c or "not detected" in c: return "neutral"
            if any(w in c for w in ("normal","good","excellent")): return "ok"
            if any(w in c for w in ("high","risk","low","underweight","overweight","obesity")): return "warn"
            return "neutral"

        lang = getattr(self, '_language', 'English')

        def _val(v, suffix=""):
            """Return formatted value or 'N/A' when not detected."""
            return "N/A" if v is None else f"{v}{suffix}"

        rows = [
            ("Weight",               f"{hr.get('weight', 0)} kg",                       "-",                                                                       "ok"),
            ("BMI",                  str(hr.get("bmi", 0)),                             _translate_cat(hc.get("bmi_category", "N/A"), lang),       st(hc.get("bmi_category", ""))),
            (lbl["body_fat_lbl"],    _val(hr.get("body_fat"),  "%"),                    _translate_cat(hc.get("body_fat_category", "N/A"), lang),  st(hc.get("body_fat_category", ""))),
            (lbl["visceral_fat_lbl"],_val(hr.get("visceral_fat")),                      _translate_cat(hc.get("visceral_fat_category", "N/A"), lang),st(hc.get("visceral_fat_category", ""))),
            (lbl["muscle_mass_lbl"], _val(hr.get("muscle_mass"), "%"),                  _translate_cat(hc.get("muscle_mass_category", "N/A"), lang),st(hc.get("muscle_mass_category", ""))),
            (lbl["body_age_lbl"],    _val(hr.get("body_age"),   f" {lbl['years']}"),    _translate_cat(hc.get("body_age_status", "N/A"), lang),    "neutral"),
            ("BMR",                  _val(hr.get("bmr"),        " kcal"),               "-",                                                                       "ok"),
            ("TSF",                  _val(hr.get("tsf")),                               "-",                                                                       "ok"),
        ]
        for j, row in enumerate(rows):
            bg = self.WHITE if j % 2 == 0 else self.LIGHT
            d.rectangle([self.MG, y, self.PW-self.MG, y+RH], fill=bg, outline=self.LGREY)
            for i, cell in enumerate(row):
                if i == 3:
                    self._status_dot(d, CX[i] + 20, y, RH, str(cell))
                else:
                    self._txt(d, str(cell), y+11, fonts["sm"], self.DARK, x=CX[i]+8)
            y += RH
        return y + 24

    def _section_risk(self, d, hc, lbl, fonts, y):
        self._txt(d, lbl["risk_title"], y, fonts["lg"], self.RED)
        y += 44
        ws = hc.get("wellness_score", 0)
        lang = getattr(self, '_language', 'English')
        lines = [
            f"{lbl['overall_risk']}: {_translate_cat(hc.get('overall_risk_level','N/A'), lang)}",
            f"{lbl['wellness_score']}: {ws}/10   ({lbl['higher_risk']})",
            "",
            f"{lbl['key_findings']}:",
            f"   \u2022  {lbl['bmi_status']}: {_translate_cat(hc.get('bmi_category','N/A'), lang)}",
            f"   \u2022  {lbl['body_fat_lbl']}: {_translate_cat(hc.get('body_fat_category','N/A'), lang)}",
            f"   \u2022  {lbl['visceral_fat_lbl']}: {_translate_cat(hc.get('visceral_fat_category','N/A'), lang)}",
            f"   \u2022  {lbl['muscle_mass_lbl']}: {_translate_cat(hc.get('muscle_mass_category','N/A'), lang)}",
            f"   \u2022  {lbl['body_age_lbl']}: {_translate_cat(hc.get('body_age_status','N/A'), lang)}",
        ]
        total = sum(38 if l else 20 for l in lines) + 24
        d.rectangle([self.MG-4, y-4, self.PW-self.MG+4, y+total],
                    fill=self.LIGHT, outline=self.LGREY)
        for line in lines:
            if line:
                self._txt(d, line, y+6, fonts["md"], self.DARK, x=self.MG+14)
            y += 38 if line else 20

    # ── Drawing primitives ─────────────────────────────────────────────────────

    def _draw_shaped(self, img, text: str, xy, size: int, color,
                     font_path: str = "", font_index: int = 0):
        """
        Render Indic text using HarfBuzz shaping + FreeType glyph rasterization.
        Properly forms Gujarati/Hindi conjuncts, matras, and ligatures.
        """
        import uharfbuzz as hb
        import freetype as ft
        from PIL import Image as _PILImg
        fp = font_path or self._font_path
        fi = font_index
        if not fp:
            return
        x0, y0 = int(xy[0]), int(xy[1])
        # Raw bytes: re-use cached copy for the regular font
        raw = self._font_bytes if (fp == self._font_path) else open(fp, "rb").read()
        # ── HarfBuzz: shape the Unicode string ───────────────────────────────
        hb_face = hb.Face(raw, index=fi)
        hb_font = hb.Font(hb_face)
        hb_font.scale = (size * 64, size * 64)   # positions in 26.6 fixed-point
        buf = hb.Buffer()
        buf.add_str(str(text))
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)
        g_infos = buf.glyph_infos
        g_pos   = buf.glyph_positions
        # ── FreeType: rasterize each shaped glyph ────────────────────────────
        ft_face = ft.Face(fp, index=fi)
        ft_face.set_pixel_sizes(0, size)
        ascender   = ft_face.size.ascender >> 6      # pixels above baseline
        baseline_y = y0 + ascender
        rv, gv, bv = color[0], color[1], color[2]
        cur_x = x0
        for info, pos in zip(g_infos, g_pos):
            gid   = info.codepoint
            x_adv = pos.x_advance >> 6
            x_off = pos.x_offset  >> 6
            y_off = pos.y_offset  >> 6
            ft_face.load_glyph(gid, ft.FT_LOAD_RENDER)
            glyph = ft_face.glyph
            bm    = glyph.bitmap
            if bm.width > 0 and bm.rows > 0:
                gx = cur_x + x_off + glyph.bitmap_left
                gy = baseline_y - glyph.bitmap_top - y_off
                alpha   = _PILImg.frombytes("L", (bm.width, bm.rows), bytes(bm.buffer))
                overlay = _PILImg.new("RGBA", (bm.width, bm.rows), (rv, gv, bv, 0))
                overlay.putalpha(alpha)
                # Clip to image bounds
                cx0 = max(0, -gx);  cy0 = max(0, -gy)
                px  = max(0, gx);   py  = max(0, gy)
                if cx0 < overlay.width and cy0 < overlay.height and px < img.width and py < img.height:
                    cropped = overlay.crop((cx0, cy0, overlay.width, overlay.height))
                    img.paste(cropped, (px, py), cropped)
            cur_x += x_adv

    def _shaped_width(self, text: str, size: int,
                      font_path: str = "", font_index: int = 0) -> int:
        """Return pixel width of text after HarfBuzz shaping."""
        import uharfbuzz as hb
        fp  = font_path or self._font_path
        fi  = font_index
        if not fp or not self._font_bytes:
            return 0
        raw     = self._font_bytes if (fp == self._font_path) else open(fp, "rb").read()
        hb_face = hb.Face(raw, index=fi)
        hb_font = hb.Font(hb_face)
        hb_font.scale = (size * 64, size * 64)
        buf = hb.Buffer()
        buf.add_str(str(text))
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)
        return sum(p.x_advance >> 6 for p in buf.glyph_positions)

    def _txt(self, d, text, y, font, color, x=None, right=False):
        meta = self._font_meta.get(id(font)) if self._font_bytes else None
        if meta and self._current_img is not None:
            size, fp, fi = meta
            if right:
                w = self._shaped_width(str(text), size, fp, fi)
                x = self.PW - self.MG - w
            if x is None:
                x = self.MG
            self._draw_shaped(self._current_img, str(text), (x, y), size, color, fp, fi)
            return
        if right:
            bb = d.textbbox((0, 0), str(text), font=font)
            x = self.PW - self.MG - (bb[2] - bb[0])
        if x is None:
            x = self.MG
        d.text((x, y), str(text), font=font, fill=color)

    def _center(self, d, text, y, font, color):
        meta = self._font_meta.get(id(font)) if self._font_bytes else None
        if meta and self._current_img is not None:
            size, fp, fi = meta
            w = self._shaped_width(str(text), size, fp, fi)
            x = (self.PW - w) // 2
            self._draw_shaped(self._current_img, str(text), (x, y), size, color, fp, fi)
            return
        bb = d.textbbox((0, 0), str(text), font=font)
        x  = (self.PW - (bb[2] - bb[0])) // 2
        d.text((x, y), str(text), font=font, fill=color)

    def _draw_rich_line(self, d, text: str, y: int, font_reg, font_bold, color,
                         x: int = None):
        """
        Draw a line that may contain **bold** segments.
        Bold-marked spans are rendered with font_bold; the rest with font_reg.
        """
        if x is None:
            x = self.MG
        # Split on **...**  — odd-indexed segments are bold
        segments = re.split(r'\*\*(.+?)\*\*', str(text))
        cx = x
        for i, seg in enumerate(segments):
            if not seg:
                continue
            font = font_bold if (i % 2 == 1) else font_reg
            meta = self._font_meta.get(id(font)) if self._font_bytes else None
            if meta and self._current_img is not None:
                size, fp, fi = meta
                self._draw_shaped(self._current_img, seg, (cx, y), size, color, fp, fi)
                cx += self._shaped_width(seg, size, fp, fi)
                continue
            d.text((cx, y), seg, font=font, fill=color)
            bb = d.textbbox((cx, y), seg, font=font)
            cx += bb[2] - bb[0]

    def _wrap(self, d, text, font, max_w):
        """Word-wrap text; strips ** markers only for width measurement."""
        words = str(text).split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            # Measure without ** so bold markers don't inflate the width estimate
            test_plain = re.sub(r'\*\*', '', test)
            if d.textbbox((0, 0), test_plain, font=font)[2] > max_w and cur:
                lines.append(cur); cur = w
            else:
                cur = test
        if cur: lines.append(cur)
        return lines or [str(text)]

    def _status_dot(self, d, x, y_row, row_h, status):
        """Draw a filled coloured circle in the status column — font-independent."""
        r  = 9
        cy = y_row + row_h // 2
        if status == "ok":
            fill = (34, 139, 34)    # green
        elif status == "warn":
            fill = (196, 18,  47)   # brand red
        else:
            fill = (160, 160, 160)  # grey / neutral
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=fill, outline=fill)

    def _footer(self, d, lbl, fonts):
        fy = self.PH - self.MG - 38
        d.rectangle([self.MG, fy, self.PW - self.MG, fy + 2], fill=self.RED)
        txt = (f"{lbl['footer_generated']}: {datetime.now().strftime('%d %B %Y')}  "
               f"|  KSS Body Evolution Wellness Center")
        self._center(d, txt, fy + 8, fonts["sm"], self.GREY)


class PDFReportGenerator:
    """Generates professional A4 wellness reports in PDF format (English / Hindi / Gujarati)"""

    CLINIC_NAME    = "KSS Body Evolution Wellness Center"
    CLINIC_ADDRESS = "Your Clinic Address Here"
    CLINIC_PHONE   = "Your Phone Number"
    CLINIC_EMAIL   = "your-email@clinic.com"

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._current_font = None

    # ── Public API ─────────────────────────────────────────────────────────────
    def generate_report(
        self,
        patient: Dict,
        health_record: Dict,
        health_categories: Dict,
        ai_analysis: str,
        language: str = "English",
    ) -> bytes:
        lbl = _LABELS.get(language, _LABELS["English"])

        # ── Try PIL+HarfBuzz rendering (works on Windows AND Linux/Cloud) ─────
        if _USE_PIL:
            try:
                return IndicPDFRenderer().render(
                    patient, health_record, health_categories, ai_analysis, lbl,
                    language=language
                )
            except Exception as e:
                # If PIL fails on Windows, fall through to ReportLab
                import streamlit as st
                st.warning(f"⚠️ PIL rendering failed: {str(e)[:100]}. Using ReportLab fallback.")

        # ── ReportLab (works everywhere — primary on Cloud) ────────────────────
        font = get_font_for_language(language)
        self._ensure_styles(font)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=0.5 * inch, leftMargin=0.5 * inch,
            topMargin=0.5 * inch,  bottomMargin=0.5 * inch,
        )
        story: list = []
        story.extend(self._create_header(patient, health_record, lbl, font))
        story.extend(self._create_patient_info_section(patient, lbl, font))
        story.extend(self._create_metrics_table(health_record, health_categories, lbl, font))
        story.extend(self._create_risk_assessment_section(health_categories, lbl, font))
        story.extend(self._create_ai_analysis_section(ai_analysis, lbl, font))
        story.extend(self._create_footer(health_record, lbl, font))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # ── Style helpers ──────────────────────────────────────────────────────────
    def _ensure_styles(self, font: str):
        if self._current_font == font:
            return
        self._current_font = font
        bf = "Helvetica-Bold" if font == "Helvetica" else font

        for name in ["CustomTitle", "CustomHeading", "WellnessBody",
                     "Footer", "AISection", "BulletItem"]:
            if name in self.styles.byName:
                del self.styles.byName[name]

        self.styles.add(ParagraphStyle(
            name="CustomTitle", parent=self.styles["Heading1"],
            fontSize=18, textColor=colors.HexColor("#C4122F"),
            spaceAfter=10, alignment=TA_CENTER, fontName=bf,
        ))
        self.styles.add(ParagraphStyle(
            name="CustomHeading", parent=self.styles["Heading2"],
            fontSize=13, textColor=colors.HexColor("#1A0A0F"),
            spaceAfter=8, spaceBefore=10, fontName=bf,
        ))
        self.styles.add(ParagraphStyle(
            name="WellnessBody", fontSize=9.5, fontName=font,
            alignment=TA_JUSTIFY, spaceAfter=6, leading=14,
        ))
        self.styles.add(ParagraphStyle(
            name="Footer", fontSize=8, fontName=font,
            textColor=colors.grey, alignment=TA_CENTER, spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="AISection", fontSize=11, fontName=bf,
            textColor=colors.HexColor("#C4122F"),
            spaceAfter=5, spaceBefore=12,
        ))
        self.styles.add(ParagraphStyle(
            name="BulletItem", fontSize=9.5, fontName=font,
            leftIndent=16, spaceAfter=4, leading=14,
        ))

    # ── Section builders ───────────────────────────────────────────────────────
    def _create_header(self, patient, health_record, lbl, font):
        bf = "Helvetica-Bold" if font == "Helvetica" else font
        tiny = ParagraphStyle("_tiny", fontName=font, fontSize=9.5, spaceAfter=3)
        story = [
            Paragraph(self.CLINIC_NAME, self.styles["CustomTitle"]),
            Paragraph(lbl["report_title"], self.styles["CustomHeading"]),
            Paragraph(f"<b>{lbl['report_date']}:</b> {datetime.now().strftime('%d %B %Y')}", tiny),
            Paragraph(f"<b>{lbl['report_id']}:</b> {health_record.get('id', 'N/A')}", tiny),
            Spacer(1, 0.18 * inch),
            self._h_line(),
            Spacer(1, 0.18 * inch),
        ]
        return story

    def _create_patient_info_section(self, patient, lbl, font):
        cell = ParagraphStyle("_cell", fontName=font, fontSize=9.5)
        data = [
            [Paragraph(f"<b>{lbl['name']}:</b> {patient['name']}", cell),
             Paragraph(f"<b>{lbl['patient_id']}:</b> {patient['patient_id']}", cell)],
            [Paragraph(f"<b>{lbl['age']}:</b> {patient['age']} {lbl['years']}", cell),
             Paragraph(f"<b>{lbl['gender']}:</b> {patient['gender']}", cell)],
            [Paragraph(f"<b>{lbl['height']}:</b> {patient['height']} {lbl['cm']}", cell),
             Paragraph(f"<b>{lbl['mobile']}:</b> {patient['mobile']}", cell)],
            [Paragraph(f"<b>{lbl['area']}:</b> {patient['area']}", cell),
             Paragraph(f"<b>{lbl['email']}:</b> {patient.get('email') or 'N/A'}", cell)],
        ]
        tbl = Table(data, colWidths=[3.5 * inch, 3.5 * inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FBF8F4")),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E4DDD4")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]))
        return [
            Paragraph(lbl["patient_info"], self.styles["CustomHeading"]),
            tbl,
            Spacer(1, 0.15 * inch),
        ]

    def _create_metrics_table(self, health_record, health_categories, lbl, font):
        bf = "Helvetica-Bold" if font == "Helvetica" else font
        hdr  = ParagraphStyle("_mh", fontName=bf, fontSize=9, textColor=colors.white)
        cell = ParagraphStyle("_mc", fontName=font, fontSize=9)

        rows = [
            [lbl["metric"],        lbl["value"],                              lbl["category"],                                          lbl["status"]],
            ["Weight",             f"{health_record.get('weight',0)} kg",     "-",                                                      self._st(None)],
            ["BMI",                f"{health_record.get('bmi',0)}",           health_categories.get("bmi_category","N/A"),               self._st(health_categories.get("bmi_category",""))],
            [lbl["body_fat_lbl"],  f"{health_record.get('body_fat',0)}%",     health_categories.get("body_fat_category","N/A"),          self._st(health_categories.get("body_fat_category",""))],
            [lbl["visceral_fat_lbl"], f"{health_record.get('visceral_fat',0)}", health_categories.get("visceral_fat_category","N/A"),    self._st(health_categories.get("visceral_fat_category",""))],
            [lbl["muscle_mass_lbl"], f"{health_record.get('muscle_mass',0)}%", health_categories.get("muscle_mass_category","N/A"),     self._st(health_categories.get("muscle_mass_category",""))],
            [lbl["body_age_lbl"],  f"{health_record.get('body_age',0)} {lbl['years']}", health_categories.get("body_age_status","N/A"), "-"],
            ["BMR",                f"{health_record.get('bmr',0)} kcal",      "-",                                                      "✓"],
            ["TSF",                f"{health_record.get('tsf',0)}",           "-",                                                      "✓"],
        ]

        table_data = [[Paragraph(str(c), hdr) for c in rows[0]]]
        for row in rows[1:]:
            table_data.append([Paragraph(str(c), cell) for c in row])

        tbl = Table(table_data, colWidths=[2.1*inch, 1.4*inch, 2.5*inch, 0.75*inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  colors.HexColor("#C4122F")),
            ("ALIGN",         (0,0),(-1,-1), "CENTER"),
            ("GRID",          (0,0),(-1,-1), 0.5, colors.HexColor("#E4DDD4")),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#FBF8F4")]),
        ]))
        return [
            Paragraph(lbl["metrics_title"], self.styles["CustomHeading"]),
            tbl,
            Spacer(1, 0.15 * inch),
        ]

    def _create_risk_assessment_section(self, health_categories, lbl, font):
        body = ParagraphStyle("_rb", fontName=font, fontSize=9.5, leading=16, spaceAfter=4)
        ws   = health_categories.get("wellness_score", 0)
        lines = [
            f"<b>{lbl['overall_risk']}:</b> {health_categories.get('overall_risk_level','N/A')}",
            f"<b>{lbl['wellness_score']}:</b> {ws}/10  ({lbl['higher_risk']})",
            f"<br/><b>{lbl['key_findings']}:</b>",
            f"&bull; {lbl['bmi_status']}: {health_categories.get('bmi_category','N/A')}",
            f"&bull; {lbl['body_fat_lbl']}: {health_categories.get('body_fat_category','N/A')}",
            f"&bull; {lbl['visceral_fat_lbl']}: {health_categories.get('visceral_fat_category','N/A')}",
            f"&bull; {lbl['muscle_mass_lbl']}: {health_categories.get('muscle_mass_category','N/A')}",
            f"&bull; {lbl['body_age_lbl']}: {health_categories.get('body_age_status','N/A')}",
        ]
        return [
            Paragraph(lbl["risk_title"], self.styles["CustomHeading"]),
            Paragraph("<br/>".join(lines), body),
            Spacer(1, 0.15 * inch),
        ]

    def _create_ai_analysis_section(self, ai_analysis: str, lbl, font) -> list:
        story = [
            Spacer(1, 0.2 * inch),
            Paragraph(lbl["ai_title"], self.styles["CustomHeading"]),
            self._h_line(),
            Spacer(1, 0.12 * inch),
        ]
        for line in ai_analysis.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("##"):
                story.append(Spacer(1, 0.05 * inch))
                story.append(Paragraph(self._md(stripped.lstrip("#").strip()), self.styles["AISection"]))
            elif stripped.startswith("* ") or stripped.startswith("- "):
                story.append(Paragraph(f"\u2022\u00a0\u00a0{self._md(stripped[2:].strip())}", self.styles["BulletItem"]))
            elif len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in ".)":
                story.append(Spacer(1, 0.05 * inch))
                story.append(Paragraph(self._md(stripped), self.styles["AISection"]))
            else:
                story.append(Paragraph(self._md(stripped), self.styles["WellnessBody"]))
        story.append(Spacer(1, 0.2 * inch))
        return story

    def _create_footer(self, health_record, lbl, font) -> list:
        fs = ParagraphStyle("_fs", fontName=font, fontSize=7.5,
                            textColor=colors.grey, alignment=TA_CENTER, leading=12)
        text = (
            f"<b>{lbl['footer_generated']}:</b> {datetime.now().strftime('%d %B %Y at %H:%M')}<br/>"
            f"<b>{lbl['report_id']}:</b> {health_record.get('id','N/A')}<br/><br/>"
            f"<b>{lbl['disclaimer_title']}:</b> {lbl['disclaimer_body']}<br/><br/>"
            f"{self.CLINIC_NAME} | {self.CLINIC_ADDRESS}<br/>"
            f"Phone: {self.CLINIC_PHONE} | Email: {self.CLINIC_EMAIL}"
        )
        return [self._h_line(), Spacer(1, 0.1 * inch), Paragraph(text, fs)]

    # ── Utilities ──────────────────────────────────────────────────────────────
    @staticmethod
    def _h_line() -> Table:
        tbl = Table([["",""]], colWidths=[7*inch, 0.2*inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#C4122F")),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ]))
        return tbl

    @staticmethod
    def _st(category) -> str:
        if not category:
            return "✓"
        cl = str(category).lower()
        if any(w in cl for w in ("normal","good","excellent")):
            return "✓"
        if any(w in cl for w in ("high","risk","low","underweight","overweight","obesity")):
            return "!"
        return "-"

    @staticmethod
    def _md(text: str) -> str:
        text = re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"^\*\s*", "", text)
        return text
