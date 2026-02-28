"""
Authentication module
Handles admin login and session management
"""

import streamlit as st
import hashlib
import os
import base64
from pathlib import Path
from typing import Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API key validation function
try:
    from ai_engine import validate_api_key
except ImportError:
    # Fallback if import fails
    def validate_api_key(key):
        return {"valid": True, "message": "Validation skipped", "quota_warning": False, "quota_message": ""}


class AuthManager:
    """Manages authentication and session handling"""
    
    # Session timeout: 12 hours of inactivity
    SESSION_TIMEOUT_HOURS = 12
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return AuthManager.hash_password(password) == password_hash
    
    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user
        Returns: (success, message)
        """
        admin_username = os.getenv("ADMIN_USERNAME", "kss_admin")
        admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH", hashlib.sha256(b"kss_@admin.com").hexdigest())
        
        if username != admin_username:
            return False, "Invalid username"
        
        if not AuthManager.verify_password(password, admin_password_hash):
            return False, "Invalid password"
        
        return True, "Login successful"
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is logged in and session is valid"""
        is_auth = st.session_state.get("authenticated", False)
        if not is_auth:
            return False
        
        # Check session timeout
        login_time = st.session_state.get("login_time")
        if login_time is None:
            return False
        
        elapsed = (datetime.now() - login_time).total_seconds() / 3600
        if elapsed > AuthManager.SESSION_TIMEOUT_HOURS:
            st.session_state.authenticated = False
            st.session_state.login_time = None
            return False
        
        return True
    
    @staticmethod
    def set_authenticated(value: bool):
        """Set authentication status and track login time"""
        st.session_state.authenticated = value
        if value:
            st.session_state.login_time = datetime.now()
        else:
            st.session_state.login_time = None
    
    @staticmethod
    def logout():
        """Logout user and clear session. Keeps _logged_out flag so the
        cookie-restore logic in app.py cannot immediately re-authenticate."""
        st.session_state.clear()           # wipe everything first
        st.session_state.authenticated = False
        st.session_state.login_time = None
        st.session_state["_logged_out"] = True   # survive the next rerun


def show_login_page(cookie_manager=None):
    """Display premium login page"""
    # NOTE: set_page_config is called once in app.py — do NOT call it here again.

    # Load logo
    logo_b64 = ""
    try:
        logo_path = Path(__file__).parent.parent / "assets" / "volunteers kss insta profil pic.png"
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    except Exception:
        pass

    logo_tag = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'style="width:90px;height:90px;border-radius:50%;'
        f'border:3px solid #E2A822;object-fit:cover;'
        f'box-shadow:0 6px 24px rgba(196,18,47,0.45);margin-bottom:16px;" />'
        if logo_b64 else
        '<div style="font-size:48px;margin-bottom:16px;">\u2764\ufe0f</div>'
    )

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,700&display=swap');

/* ══ FORCE LIGHT BACKGROUND — overrides Streamlit Cloud dark theme ══ */
html, body { background-color: #F8F5F0 !important; color: #1A0A0F !important; }
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stMain"],
[data-testid="block-container"],
section.main,
section.main > div,
div.main { background: linear-gradient(135deg, #FEF8F3 0%, #FAF3E6 50%, #F8F5F0 100%) !important; }
[data-testid="stHeader"],
[data-testid="stToolbar"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }

/* ══ LUXURY TITLE ══ */
.login-title {
    text-align: center;
    font-family: 'Cormorant Garamond', 'Palatino Linotype', Georgia, serif !important;
    font-size: 38px;
    font-weight: 700;
    letter-spacing: 3px;
    white-space: nowrap;
    background: linear-gradient(135deg, #8B0010 0%, #C4122F 30%, #E2A822 50%, #C4122F 70%, #8B0010 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 6px;
}
.login-sub {
    text-align: center;
    font-size: 11px;
    color: rgba(26, 10, 15, 0.50) !important;
    margin-bottom: 28px;
    letter-spacing: 4px;
    text-transform: uppercase;
    font-weight: 500;
}

/* ══ INPUT LABELS ══ */
[data-testid="stTextInput"] label,
[data-testid="stTextInput"] label p {
    color: rgba(26, 10, 15, 0.80) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
}

/* ══ INPUT FIELDS ══ */
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] div[data-baseweb="input"] input {
    background: #FFFFFF !important;
    border: 2px solid rgba(196, 18, 47, 0.22) !important;
    border-radius: 12px !important;
    color: #1A0A0F !important;
    font-size: 15px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #C4122F !important;
    box-shadow: 0 0 0 3px rgba(196, 18, 47, 0.15) !important;
}
/* Input wrapper backgrounds */
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] div[data-baseweb="input"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}

/* ══ FORM SUBMIT BUTTON (st.form_submit_button) ══ */
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] > button,
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #C4122F 0%, #E2A822 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    box-shadow: 0 8px 24px rgba(196, 18, 47, 0.40) !important;
    transition: all 0.25s ease !important;
    padding: 14px !important;
    width: 100% !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 32px rgba(196, 18, 47, 0.55) !important;
}

/* ══ FORM CONTAINER (remove default Streamlit form border) ══ */
[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

/* ══ EXPANDER ══ */
[data-testid="stExpander"] {
    border: 1.5px solid rgba(226, 168, 34, 0.22) !important;
    border-radius: 12px !important;
    background: rgba(255, 248, 238, 0.60) !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: rgba(26, 10, 15, 0.70) !important;
}

/* ══ ANIMATIONS ══ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes kss-shimmer {
    0%   { background-position: -300% center; }
    100% { background-position:  300% center; }
}
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 4px 16px rgba(196,18,47,0.18), inset 0 1px 0 rgba(226,168,34,0.20); }
    50%       { box-shadow: 0 6px 24px rgba(196,18,47,0.32), inset 0 1px 0 rgba(226,168,34,0.28); }
}
[data-testid="column"] { animation: fadeUp 0.5s ease 0.1s both; }
</style>
""", unsafe_allow_html=True)

    # ── Luxury Premium Banner ────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin: 12px 0 24px 0;">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #FFF8EE 0%, #FEF3E0 50%, #FFF8EE 100%);
            border: 2px solid rgba(196,18,47,0.22);
            border-radius: 60px;
            padding: 10px 40px;
            box-shadow: 0 4px 16px rgba(196,18,47,0.12), inset 0 1px 0 rgba(226,168,34,0.20);
            animation: glow-pulse 3s ease-in-out infinite;
        ">
            <span style="
                font-family: 'Cormorant Garamond', 'Palatino Linotype', Georgia, serif;
                font-size: 19px;
                font-weight: 700;
                font-style: italic;
                letter-spacing: 5px;
                text-transform: uppercase;
                background: linear-gradient(90deg,
                    #8B0010 0%, #C4122F 20%, #E2A822 42%,
                    #B8860B 50%,
                    #E2A822 58%, #C4122F 80%, #8B0010 100%);
                background-size: 300% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: kss-shimmer 5s linear infinite;
            ">✦&ensp;Jai Shree Sita Ram&ensp;✦</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top decorative separator ────────────────────────────────────
    st.markdown("""
    <div style="
        text-align: center;
        margin: 0 0 28px 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(196,18,47,0.15), transparent);
    "></div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        # ── Luxury Logo & Title Container ────────────────────────────────
        st.markdown(
            f'<div style="text-align:center;padding:16px 0 8px 0;">{logo_tag}</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="login-title">KSS Body Evolution</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Wellness Evaluation System</div>', unsafe_allow_html=True)

        # ── Visual separator ─────────────────────────────────────────────
        st.markdown("""
        <div style="
            margin: 20px 0 24px 0;
            height: 2px;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(196,18,47,0.12) 25%, 
                rgba(226,168,34,0.15) 50%, 
                rgba(196,18,47,0.12) 75%, 
                transparent 100%);
            border-radius: 1px;
        "></div>
        """, unsafe_allow_html=True)

        # ── Login Form (st.form prevents Enter-key auto-submit) ─────────
        with st.form("login_form", clear_on_submit=False):
            username_col, password_col = st.columns(2, gap="medium")

            with username_col:
                username = st.text_input("\U0001f464  Username",
                                         placeholder="Enter username")

            with password_col:
                password = st.text_input("\U0001f511  Password", type="password",
                                         placeholder="Enter password")

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

            # ── Optional Gemini API Keys ──────────────────────────────────
            with st.expander("⚙️  Gemini API Keys  (optional — uses built-in key if left blank)"):
                st.markdown(
                    "<div style='font-size:12px;color:rgba(26,10,15,0.55);margin-bottom:12px;line-height:1.7;'>"
                    "Provide your own Gemini API keys for higher rate limits.<br/>"
                    "Leave blank to use the system's built-in key as fallback."
                    "</div>",
                    unsafe_allow_html=True,
                )
                gen_key = st.text_input(
                    "🤖  Generation API Key",
                    type="password",
                    placeholder="AIzaSy… (leave blank to use default)",
                    help="Used to generate AI health reports, wellness analysis, and assessment text."
                         " → Powers: patient analysis, risk reports, health summaries.",
                )
                trans_key = st.text_input(
                    "🌐  Translation API Key",
                    type="password",
                    placeholder="AIzaSy… (leave blank to use default)",
                    help="Used to translate generated reports between languages "
                         "(English ↔ Gujarati, Hindi, etc.)"
                         " → Powers: PDF language selection (Gujarati / Hindi).",
                )
                st.markdown(
                    "<div style='font-size:11px;color:rgba(26,10,15,0.40);margin-top:8px;line-height:1.6;'>"
                    "💡 <b>Generation API</b> — Generates AI text: reports, analysis, chat replies.<br/>"
                    "💡 <b>Translation API</b> — Translates text between languages (English ↔ Gujarati / Hindi).<br/>"
                    "Both keys can be the same Gemini key if you prefer."
                    "</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            # ── Submit button (only click triggers submission) ────────────
            submitted = st.form_submit_button(
                "Sign In  →",
                use_container_width=True,
                type="primary",
            )

        # ── Handle form submission (OUTSIDE form block) ──────────────────
        if submitted:
            username_trimmed = username.strip() if username else ""
            password_trimmed = password.strip() if password else ""

            if username_trimmed and password_trimmed:
                success, message = AuthManager.login(username_trimmed, password_trimmed)
                if success:
                    validation_passed = True
                    validation_messages = []

                    if gen_key and gen_key.strip():
                        with st.spinner("🔑 Validating Generation API Key..."):
                            gen_validation = validate_api_key(gen_key.strip())
                            if not gen_validation["valid"]:
                                validation_passed = False
                                validation_messages.append(f"❌ Generation API: {gen_validation['message']}")
                                if gen_validation["quota_warning"]:
                                    validation_messages.append(f"   → {gen_validation['quota_message']}")
                            else:
                                validation_messages.append("✅ Generation API: Valid")

                    if trans_key and trans_key.strip():
                        with st.spinner("🔑 Validating Translation API Key..."):
                            trans_validation = validate_api_key(trans_key.strip())
                            if not trans_validation["valid"]:
                                validation_passed = False
                                validation_messages.append(f"❌ Translation API: {trans_validation['message']}")
                                if trans_validation["quota_warning"]:
                                    validation_messages.append(f"   → {trans_validation['quota_message']}")
                            else:
                                validation_messages.append("✅ Translation API: Valid")

                    if validation_messages:
                        for msg in validation_messages:
                            st.info(msg)

                    if validation_passed:
                        AuthManager.set_authenticated(True)
                        st.session_state["user_generation_api_key"]  = gen_key.strip()   if gen_key   else ""
                        st.session_state["user_translation_api_key"] = trans_key.strip() if trans_key else ""
                        if cookie_manager is not None:
                            try:
                                cookie_manager.set(
                                    "wellness_auth", "authenticated",
                                    max_age=8 * 3600
                                )
                            except Exception:
                                pass
                        st.rerun()
                    else:
                        st.error("⚠️ API key validation failed. Please check your keys or leave them blank to use the system key.")
                else:
                    st.error("✘ " + message)
            else:
                st.warning("⚠️ Please enter both username and password")




def require_authentication():
    """Decorator to require authentication for pages"""
    if not AuthManager.is_authenticated():
        show_login_page()
        st.stop()
