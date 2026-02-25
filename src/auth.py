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
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH", hashlib.sha256(b"admin123").hexdigest())
        
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
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.login_time = None
        st.session_state.clear()


def show_login_page(cookie_manager=None):
    """Display premium login page"""
    st.set_page_config(page_title="Body Evolution \u2013 Login", layout="centered",
                       page_icon="\u2764\ufe0f")

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1A0A0F 0%, #2D0D18 50%, #1A0A0F 100%) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.login-title {
    text-align:center; font-size:22px; font-weight:700;
    background:linear-gradient(135deg,#E2A822,#ffffff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:4px;
}
.login-sub {
    text-align:center; font-size:11px; color:rgba(245,230,208,0.5);
    margin-bottom:26px; letter-spacing:1.5px; text-transform:uppercase;
}
[data-testid="stTextInput"] label { color:rgba(245,230,208,0.75) !important; font-size:13px !important; }
[data-testid="stTextInput"] input {
    background:rgba(255,255,255,0.06) !important;
    border:1.5px solid rgba(226,168,34,0.3) !important;
    border-radius:10px !important; color:#F5E6D0 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color:#E2A822 !important;
    box-shadow:0 0 0 3px rgba(226,168,34,0.18) !important;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#C4122F 0%,#E2A822 100%) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-size:15px !important; padding:12px !important;
    transition:all 0.25s ease !important;
    box-shadow:0 6px 20px rgba(196,18,47,0.45) !important;
}
.stButton > button[kind="primary"]:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 10px 30px rgba(196,18,47,0.6) !important;
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
}
[data-testid="column"] { animation: fadeUp 0.5s ease; }
</style>
""", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown(
            f'<div style="text-align:center;padding:28px 0 0 0;">{logo_tag}</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="login-title">KSS BODY EVOLUTION</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Wellness Evaluation System</div>', unsafe_allow_html=True)

        username = st.text_input("\U0001f464  Username", key="login_username",
                                 placeholder="Enter username")
        password = st.text_input("\U0001f511  Password", type="password",
                                 key="login_password", placeholder="Enter password")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Optional Gemini API Keys ────────────────────────────────────────
        with st.expander("⚙️  Gemini API Keys  (optional — uses built-in key if left blank)"):
            st.markdown(
                "<div style='font-size:12px;color:rgba(245,230,208,0.55);margin-bottom:12px;line-height:1.7;'>"
                "Provide your own Gemini API keys for higher rate limits.<br/>"
                "Leave blank to use the system's built-in key as fallback."
                "</div>",
                unsafe_allow_html=True,
            )
            gen_key = st.text_input(
                "🤖  Generation API Key",
                type="password",
                key="login_gen_key",
                placeholder="AIzaSy… (leave blank to use default)",
                help="Used to generate AI health reports, wellness analysis, and assessment text."
                     " → Powers: patient analysis, risk reports, health summaries.",
            )
            trans_key = st.text_input(
                "🌐  Translation API Key",
                type="password",
                key="login_trans_key",
                placeholder="AIzaSy… (leave blank to use default)",
                help="Used to translate generated reports between languages "
                     "(English ↔ Gujarati, Hindi, etc.)"
                     " → Powers: PDF language selection (Gujarati / Hindi).",
            )
            st.markdown(
                "<div style='font-size:11px;color:rgba(245,230,208,0.35);margin-top:8px;line-height:1.6;'>"
                "💡 <b>Generation API</b> — Generates AI text: reports, analysis, chat replies.<br/>"
                "💡 <b>Translation API</b> — Translates text between languages (English ↔ Gujarati / Hindi).<br/>"
                "Both keys can be the same Gemini key if you prefer."
                "</div>",
                unsafe_allow_html=True,
            )
        # ───────────────────────────────────────────────────────────────────

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Sign In  \u2192", width='stretch', type="primary"):
            if username and password:
                success, message = AuthManager.login(username, password)
                if success:
                    AuthManager.set_authenticated(True)
                    # Store user-supplied API keys in session state
                    # (empty string → helper functions fall back to env key)
                    st.session_state["user_generation_api_key"]  = gen_key.strip()   if gen_key   else ""
                    st.session_state["user_translation_api_key"] = trans_key.strip() if trans_key else ""
                    if cookie_manager is not None:
                        cookie_manager.set(
                            "wellness_auth", "authenticated",
                            expires_at=datetime.now() + timedelta(hours=8)
                        )
                    st.success(message)
                    st.rerun()
                else:
                    st.error("\u274c " + message)
            else:
                st.warning("\u26a0\ufe0f Please enter username and password")

        st.markdown("""
<div style="margin-top:22px;padding:14px 16px;border-radius:10px;
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(226,168,34,0.15);
            font-size:12px;color:rgba(245,230,208,0.5);line-height:1.9;">
    <b style="color:rgba(226,168,34,0.7);">Default credentials</b><br/>
    Username: <code style="color:#E2A822;">admin</code>&nbsp;&nbsp;
    Password: <code style="color:#E2A822;">admin123</code><br/>
    <span style="color:rgba(196,18,47,0.65);">\u26a0\ufe0f Change these in production!</span>
</div>
""", unsafe_allow_html=True)


def require_authentication():
    """Decorator to require authentication for pages"""
    if not AuthManager.is_authenticated():
        show_login_page()
        st.stop()
