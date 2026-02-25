"""
Main Streamlit Application
Body Evolution Wellness Evaluation System
"""

import streamlit as st
import sys
import os
import re
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import extra_streamlit_components as stx

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import all modules
from auth import AuthManager, require_authentication, show_login_page
from database import DatabaseManager, init_database
from patient import PatientManager
from evaluation import EvaluationManager
from pdf_generator import PDFReportGenerator
from rule_engine import RuleEngine
from ai_engine import AIHealthAnalyzer
from utils import initialize_session_state, show_footer

# Configure page
def _load_logo_image():
    try:
        from PIL import Image
        return Image.open(Path(__file__).parent / "assets" / "volunteers kss insta profil pic.png")
    except Exception:
        return "💎"

st.set_page_config(
    page_title="KSS Body Evolution – Wellness Evaluation",
    page_icon=_load_logo_image(),
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Logo helper ────────────────────────────────────────────────────────────
import base64 as _b64

def _logo_b64() -> str:
    logo_path = Path(__file__).parent / "assets" / "volunteers kss insta profil pic.png"
    try:
        return _b64.b64encode(logo_path.read_bytes()).decode()
    except Exception:
        return ""

LOGO_B64 = _logo_b64()

# ─── Premium CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&display=swap');

/* ── Global ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #F8F5F0 !important; }
[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0508 0%, #1A0A0F 35%, #2D0D18 65%, #1A0A0F 100%) !important;
    border-right: 1px solid rgba(196,18,47,0.22) !important;
}
[data-testid="stSidebar"] * { color: #F5E6D0 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(226,168,34,0.15) !important; }

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(196,18,47,0.18) !important;
    color: rgba(245,230,208,0.75) !important;
    border-radius: 8px !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    font-weight: 500 !important;
    letter-spacing: 1.2px !important;
    font-size: 11px !important;
    padding: 10px 16px !important;
    text-transform: uppercase !important;
    margin-bottom: 3px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, rgba(196,18,47,0.85) 0%, rgba(226,168,34,0.85) 100%) !important;
    border-color: transparent !important;
    transform: translateX(6px) !important;
    box-shadow: 0 4px 20px rgba(196,18,47,0.35) !important;
    color: white !important;
    letter-spacing: 1.5px !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #C4122F 0%, #E2A822 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 4px 20px rgba(196,18,47,0.4) !important;
    font-weight: 600 !important;
    color: white !important;
}

/* ── Main area buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #C4122F 0%, #E2A822 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 12.5px !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 16px rgba(196,18,47,0.28) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(196,18,47,0.42) !important;
}
.stButton > button[kind="secondary"] {
    border: 1px solid rgba(196,18,47,0.35) !important;
    color: #C4122F !important;
    background: transparent !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    letter-spacing: 0.6px !important;
    font-size: 12.5px !important;
    transition: all 0.3s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(196,18,47,0.05) !important;
    border-color: #C4122F !important;
    transform: translateY(-1px) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #C4122F 0%, #E2A822 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    font-size: 12.5px !important;
    box-shadow: 0 4px 16px rgba(196,18,47,0.28);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
}
[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(196,18,47,0.42) !important;
}

/* ── Stat / metric cards ── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 6px 20px rgba(0,0,0,0.06);
    border-top: 2px solid #E2A822;
    border-left: none;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 40px rgba(196,18,47,0.1), 0 2px 8px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] {
    color: #aaa !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.8px !important;
}
[data-testid="stMetricValue"] {
    color: #1A0A0F !important;
    font-size: 32px !important;
    font-weight: 300 !important;
    font-family: 'Cormorant Garamond', serif !important;
    letter-spacing: 1px !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-testid="stTab"] {
    border-radius: 6px 6px 0 0 !important;
    font-weight: 500 !important;
    font-size: 11.5px !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
    padding: 10px 28px !important;
    margin-right: 4px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #C4122F 0%, #E2A822 100%) !important;
    color: white !important;
    border: none !important;
    padding: 10px 28px !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border: 1px solid #E4DDD4 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #E2A822 !important;
    box-shadow: 0 0 0 3px rgba(226,168,34,0.12) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(0,0,0,0.05);
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(226,168,34,0.3), transparent) !important;
    margin: 24px 0 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.5s cubic-bezier(0.4,0,0.2,1) forwards; }

/* ── Welcome banner ── */
.welcome-banner {
    background: linear-gradient(140deg, #6B0818 0%, #C4122F 45%, #9A1528 75%, #C49010 100%);
    border-radius: 18px;
    padding: 38px 48px;
    color: white;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 48px rgba(196,18,47,0.4), 0 4px 12px rgba(0,0,0,0.14);
}
.welcome-banner::before {
    content: '';
    position: absolute; top: -70px; right: -70px;
    width: 240px; height: 240px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.welcome-banner::after {
    content: '';
    position: absolute; bottom: -90px; right: 80px;
    width: 300px; height: 300px;
    background: rgba(226,168,34,0.09);
    border-radius: 50%;
}
.welcome-banner h1 {
    font-size: 28px;
    font-weight: 400;
    letter-spacing: 5px;
    text-transform: uppercase;
    margin: 0 0 6px 0;
    font-family: 'Cormorant Garamond', serif !important;
}
.welcome-banner p { font-size: 12.5px; margin: 0; opacity: 0.78; letter-spacing: 0.6px; }

/* ── Section heading ── */
.section-title {
    font-size: 10px;
    font-weight: 700;
    color: #bbb;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 30px 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(226,168,34,0.25);
}

/* ── Risk badge ── */
.risk-low  { background:#EDF7EE; color:#2E7D32; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:0.6px; }
.risk-mod  { background:#FFFBF0; color:#9A7200; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:0.6px; }
.risk-high { background:#FFF0F0; color:#C62828; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:0.6px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #F8F5F0; }
::-webkit-scrollbar-thumb { background: rgba(196,18,47,0.3); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


def initialize_app():
    """Initialize application"""
    initialize_session_state()

    # Initialize database (only once per session)
    if "db" not in st.session_state:
        with st.spinner("Connecting to database…"):
            try:
                st.session_state.db = init_database()
            except Exception as e:
                st.session_state.db = None

    # Show a persistent banner when the DB is unreachable
    from database import DatabaseManager
    if st.session_state.get("db") is None and DatabaseManager._offline:
        st.warning(
            "⚠️ **Supabase is unreachable** — the free-tier project may be **paused**.\n\n"
            "1. Open [supabase.com/dashboard](https://supabase.com/dashboard)\n"
            "2. Select your project → click **Resume Project**\n"
            "3. Wait ~30 s, then **restart this app**\n\n"
            "_Patient data and evaluations require an active database connection._",
            icon="🔌",
        )


def show_dashboard(db: DatabaseManager):
    """Display main dashboard"""
    today = datetime.now().strftime("%A, %d %B %Y")
    logo_img = (
        f'<img src="data:image/png;base64,{LOGO_B64}" '
        f'style="width:90px;height:90px;border-radius:50%;'
        f'border:2px solid rgba(255,255,255,0.6);object-fit:cover;'
        f'vertical-align:middle;margin-right:16px;'
        f'box-shadow:0 4px 16px rgba(0,0,0,0.3);" />'
        if LOGO_B64 else ""
    )
    st.markdown(f"""
    <div class="welcome-banner fade-up">
        <div style="display:flex;align-items:center;">
            {logo_img}
            <div>
                <h1 style="margin:0 0 4px 0;">KSS Body Evolution</h1>
                <p style="margin:0;">AI-powered Wellness Evaluation System &nbsp;·&nbsp; {today}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if db is None:
        st.warning("Database not connected — showing demo mode")
        col1, col2, col3, col4 = st.columns(4)
        for col, label, val in zip(
            [col1, col2, col3, col4],
            ["Total Patients", "Evaluations", "High Risk", "Status"],
            ["0", "0", "0", "Demo"]
        ):
            with col:
                st.metric(label, val)
        st.info("Update `.env` with Supabase credentials to enable full functionality.")
        return

    stats = db.get_dashboard_stats()

    # ── Stat cards ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Patients",    stats.get("total_patients", 0))
    with col2:
        st.metric("Total Evaluations", stats.get("total_evaluations", 0))
    with col3:
        hr = stats.get("high_risk_patients", 0)
        st.metric("High Risk", hr,
                  delta=f"{hr} need attention" if hr else "All clear",
                  delta_color="inverse" if hr else "normal")
    with col4:
        st.metric("System Status", "Active", delta="All systems operational")

    st.markdown('<div class="section-title">Recent Evaluations</div>', unsafe_allow_html=True)

    recent_records = db.get_recent_activity(limit=5)
    if recent_records:
        recent_data = []
        for record in recent_records:
            patient = db.get_patient(record["patient_id"])
            score = record.get('wellness_score', 0)
            risk = "High" if score > 6 else "Moderate" if score > 3 else "Low"
            if patient:
                recent_data.append({
                    "Patient ID":   record["patient_id"],
                    "Name":         patient["name"],
                    "Date":         record["created_at"][:10] if record["created_at"] else "N/A",
                    "Wellness Score": f"{score}/10",
                    "Risk Level":   risk,
                })
        st.dataframe(recent_data, width='stretch', hide_index=True)
    else:
        st.info("No evaluations recorded yet — complete a health evaluation to see data here.")

    st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add New Patient",  width='stretch', type="primary"):
            st.session_state.current_page = "Patient Management"; st.rerun()
    with col2:
        if st.button("New Evaluation",   width='stretch', type="primary"):
            st.session_state.current_page = "Evaluation"; st.rerun()
    with col3:
        if st.button("View History",     width='stretch', type="primary"):
            st.session_state.current_page = "History"; st.rerun()


def show_patient_management(db: DatabaseManager):
    """Display patient management page"""
    st.markdown('<div class="section-title">Patient Management</div>', unsafe_allow_html=True)
    st.markdown("**Create, search, and manage patient records**")
    st.divider()
    
    if db is None:
        st.warning("Database not connected. Cannot manage patients in demo mode.")
        st.info("Update .env with Supabase credentials to enable patient management.")
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Add Patient",
        "Search Patient",
        "All Patients",
        "Update Patient",
        "Delete Patient"
    ])
    
    patient_manager = PatientManager(db)
    
    with tab1:
        patient_manager.show_add_patient_form()
    
    with tab2:
        patient_id = patient_manager.show_search_patient()
        if patient_id:
            st.divider()
            patient_manager.show_patient_details(patient_id)
    
    with tab3:
        patient_manager.show_all_patients_table()
    
    with tab4:
        st.subheader("Update Patient Information")
        all_patients = db.get_all_active_patients()
        
        if all_patients:
            selected = st.selectbox(
                "Select patient to update:",
                options=all_patients,
                format_func=lambda p: f"{p['patient_id']} - {p['name']}"
            )
            
            if selected:
                patient_manager.show_update_patient_form(selected["patient_id"])
        else:
            st.info("No patients found")
    
    with tab5:
        st.subheader("Delete Patient")
        all_patients = db.get_all_active_patients()
        
        if all_patients:
            selected = st.selectbox(
                "Select patient to delete:",
                options=all_patients,
                format_func=lambda p: f"{p['patient_id']} - {p['name']}",
                key="delete_select"
            )
            
            if selected:
                patient_manager.show_delete_confirmation(selected["patient_id"])
        else:
            st.info("No patients found")


def show_evaluation_page(db: DatabaseManager):
    """Display health evaluation page"""
    st.markdown('<div class="section-title">Health Evaluation</div>', unsafe_allow_html=True)
    st.markdown("**Complete health assessment and generate wellness reports**")
    st.divider()
    
    evaluation_manager = EvaluationManager(db)
    
    # Step 1: Select Patient
    st.subheader("Step 1: Select Patient")
    
    all_patients = db.get_all_active_patients()
    
    if not all_patients:
        st.warning("No patients found. Please add a patient first.")
        if st.button("Add Patient"):
            st.session_state.current_page = "Patient Management"
            st.rerun()
        return
    
    selected_patient = st.selectbox(
        "Choose a patient:",
        options=all_patients,
        format_func=lambda p: f"{p['patient_id']} - {p['name']} (Age: {p['age']}, {p['gender']})"
    )
    
    if not selected_patient:
        return
    
    patient_id = selected_patient["patient_id"]
    
    st.divider()
    
    # Display patient info
    patient_manager = PatientManager(db)
    patient_manager.show_patient_details(patient_id)
    
    st.divider()
    
    # Step 2: Enter Health Metrics
    st.subheader("Step 2: Enter Health Metrics")
    
    health_data = evaluation_manager.show_evaluation_form(patient_id)
    
    if health_data:
        # Step 3: Process evaluation
        st.subheader("Step 3: Processing")
        
        # Process through rule engine and AI
        success, message, report_data = evaluation_manager.process_evaluation(
            selected_patient,
            health_data
        )
        
        if success:
            st.success(message)
            st.balloons()
            
            # Step 4: Display report
            st.divider()
            st.subheader("Step 4: Wellness Report")
            
            evaluation_manager.show_evaluation_report(report_data)
        else:
            st.error(f"Error: {message}")


def _build_pdf_for_record(
    patient: dict,
    record: dict,
    language: str = "English",
    trans_method: str = "google",
    mode: str = "translate",  # "direct" | "translate"
) -> bytes:
    """Re-compute categories from a stored health record and generate PDF bytes."""
    categories = RuleEngine.process_health_metrics(
        record, int(patient.get("age", 0)), patient.get("gender", "Male")
    )
    health_summary = categories.pop("health_summary", "")
    ai_text = record.get("ai_summary", "No AI analysis available for this record.")
    if language != "English":
        if mode == "direct":
            try:
                ok, resp = AIHealthAnalyzer.generate_in_language(health_summary, language)
                if ok:
                    ai_text = resp
            except Exception:
                pass  # fall back to stored English ai_summary
        else:
            try:
                ai_text = AIHealthAnalyzer.translate_for_pdf(ai_text, language, method=trans_method)
            except Exception:
                pass
    pdf_gen = PDFReportGenerator()
    return pdf_gen.generate_report(patient, record, categories, ai_text, language=language)


def show_health_history(db: DatabaseManager):
    """Display patient health history"""
    st.markdown('<div class="section-title">Health History</div>', unsafe_allow_html=True)
    st.markdown("**View, analyse, and download past wellness evaluations**")
    st.divider()

    all_patients = db.get_all_active_patients()

    if not all_patients:
        st.info("No patients found")
        return

    selected_patient = st.selectbox(
        "Select patient:",
        options=all_patients,
        format_func=lambda p: f"{p['patient_id']} - {p['name']}"
    )

    if not selected_patient:
        return

    patient_id = selected_patient["patient_id"]
    health_records = db.get_patient_health_records(patient_id)

    if not health_records:
        st.info(f"No health records found for {selected_patient['name']}")
        return

    st.write(f"Found **{len(health_records)}** evaluation(s) for **{selected_patient['name']}**")
    st.divider()

    # ── Summary table ─────────────────────────────────────────────────────────
    records_data = []
    for record in health_records:
        records_data.append({
            "Date": record["created_at"][:10] if record["created_at"] else "N/A",
            "Weight": f"{record['weight']} kg",
            "BMI": f"{record['bmi']}",
            "Wellness Score": f"{record.get('wellness_score', 0)}/10",
            "Body Fat": f"{record['body_fat']}%",
            "Muscle Mass": f"{record['muscle_mass']}%",
        })
    st.dataframe(records_data, width='stretch', hide_index=True)
    st.divider()

    # ── Per-record detail + PDF download ─────────────────────────────────────
    st.subheader("Evaluation Details & PDF Download")

    record_options = [
        f"#{i+1}  –  {r['created_at'][:10] if r['created_at'] else 'N/A'}  "
        f"(BMI {r['bmi']}, Score {r.get('wellness_score', 0)}/10)"
        for i, r in enumerate(health_records)
    ]
    selected_idx = st.selectbox(
        "Select evaluation to view / download:",
        options=range(len(health_records)),
        format_func=lambda i: record_options[i]
    )

    chosen_record = health_records[selected_idx]

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Physical Measurements:**")
        st.write(f"• Weight: {chosen_record['weight']} kg")
        st.write(f"• BMI: {chosen_record['bmi']}")
        st.write(f"• BMR: {chosen_record['bmr']} kcal/day")
        st.write(f"• TSF: {chosen_record['tsf']}")
    with col2:
        st.write("**Body Composition:**")
        st.write(f"• Body Fat: {chosen_record['body_fat']}%")
        st.write(f"• Visceral Fat: {chosen_record['visceral_fat']}")
        st.write(f"• Muscle Mass: {chosen_record['muscle_mass']}%")
        st.write(f"• Body Age: {chosen_record['body_age']} years")

    st.divider()

    # ── PDF download — language selector ────────────────────────────────────
    st.subheader("Download PDF Report")
    pdf_lang = st.radio(
        "Report Language:",
        ["English", "Hindi / हिंदी", "Gujarati / ગુજરાતી"],
        horizontal=True,
        key="history_pdf_lang",
    )
    lang_map = {"English": "English", "Hindi / हिंदी": "Hindi", "Gujarati / ગુજરાતી": "Gujarati"}
    lang_code_map = {"English": "EN", "Hindi": "HI", "Gujarati": "GU"}
    sel_lang = lang_map[pdf_lang]
    _pname = re.sub(r"[^A-Za-z0-9]+", "_", str(selected_patient.get("name", "Patient"))).strip("_")
    _pid   = selected_patient.get("patient_id", "report")
    filename = f"KSS_Wellness_Report_{_pname}_{_pid}.pdf"

    # Report mode + translation engine (only shown for non-English)
    hist_trans_method = "google"
    hist_report_mode = "translate"  # "direct" or "translate"
    if sel_lang != "English":
        hist_mode_opt = st.radio(
            "Report Mode:",
            [f"📝 Direct — AI writes in {sel_lang}", "🔄 Translated — Convert English analysis"],
            horizontal=True,
            key="hist_report_mode",
            help=(
                f"Direct: Gemini AI generates the full health report directly in {sel_lang} "
                "(highest quality, natural phrasing).\n"
                "Translated: The English AI analysis is translated to the chosen language."
            ),
        )
        hist_report_mode = "direct" if "Direct" in hist_mode_opt else "translate"

        if hist_report_mode == "translate":
            hist_trans_opt = st.radio(
                "Translation Engine:",
                ["🌐 Google Translate", "✨ Gemini AI"],
                horizontal=True,
                key="hist_trans_method",
                help="Google Translate is fast. Gemini AI gives richer medical phrasing.",
            )
            hist_trans_method = "gemini" if "Gemini" in hist_trans_opt else "google"

    # ── Generate / Cancel state ─────────────────────────────────────────────────────
    if "hist_pdf_bytes" not in st.session_state:
        st.session_state["hist_pdf_bytes"] = None
    if "hist_pdf_cancelled" not in st.session_state:
        st.session_state["hist_pdf_cancelled"] = False

    col_gen, col_can = st.columns(2)
    with col_gen:
        gen_clicked = st.button(
            f"Generate {sel_lang} Report",
            width='stretch',
            type="primary",
            key="hist_generate_btn",
        )
    with col_can:
        can_clicked = st.button(
            "Cancel",
            width='stretch',
            key="hist_cancel_btn",
        )

    if can_clicked:
        st.session_state["hist_pdf_bytes"] = None
        st.session_state["hist_pdf_cancelled"] = True
        st.rerun()

    if st.session_state.get("hist_pdf_cancelled"):
        st.warning("Report generation cancelled.")
        st.session_state["hist_pdf_cancelled"] = False

    if gen_clicked:
        st.session_state["hist_pdf_bytes"] = None
        try:
            with st.spinner(f"Generating {sel_lang} report... Please wait."):
                pdf_bytes = _build_pdf_for_record(
                    selected_patient,
                    chosen_record,
                    language=sel_lang,
                    trans_method=hist_trans_method,
                    mode=hist_report_mode,
                )
            st.session_state["hist_pdf_bytes"] = pdf_bytes
            st.success("Report generation successful!")
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

    if st.session_state.get("hist_pdf_bytes"):
        st.download_button(
            label=f"Download PDF ({sel_lang})",
            data=st.session_state["hist_pdf_bytes"],
            file_name=filename,
            mime="application/pdf",
            width='stretch',
            type="primary",
            key="hist_download_btn",
        )

    st.divider()

    # ── AI analysis for chosen record ─────────────────────────────────────────
    st.subheader("AI Analysis")
    if chosen_record.get("ai_summary"):
        st.markdown(chosen_record["ai_summary"])
    else:
        st.info("No AI analysis available for this record")


def _build_patient_records_pdf(patients: list) -> bytes:
    """
    Generate a clean A4 PDF listing patient info only
    (ID, Name, Age, Gender, Mobile, Area, Email, Registered date).
    Uses PIL — same renderer as wellness reports, no extra deps.
    """
    from PIL import Image, ImageDraw, ImageFont
    from pdf_generator import IndicPDFRenderer

    R   = IndicPDFRenderer
    fp, fi = R._resolve_font("English")
    try:
        if fp is None:
            raise OSError
        f_sm = ImageFont.truetype(fp, 17, index=fi)   # data cells
        f_md = ImageFont.truetype(fp, 26, index=fi)
        f_lg = ImageFont.truetype(fp, 34, index=fi)
        f_hd = ImageFont.truetype(fp, 19, index=fi)   # column headers
    except Exception:
        f_sm = f_md = f_lg = f_hd = ImageFont.load_default()

    RED   = R.RED;  DARK  = R.DARK;  WHITE  = R.WHITE
    LIGHT = R.LIGHT; LGREY = R.LGREY; GREY  = R.GREY
    GOLD  = R.GOLD
    # Portrait A4 @ 150 DPI  (1240 × 1754)
    PW, PH = 1240, 1754
    MG = 65   # usable width = 1240 - 2×65 = 1110 px

    # Column widths (total = 1110 px exactly)
    COLS = [
        ("#",       45),
        ("ID",      105),
        ("Name",    245),
        ("Age",      55),
        ("Gender",   90),
        ("Mobile",  160),
        ("Area",    155),
        ("Email",   255),
    ]  # 45+105+245+55+90+160+155+255 = 1110
    CX = [MG]
    for _, w in COLS[:-1]:
        CX.append(CX[-1] + w)
    RH  = 36   # row height
    HDR = 42   # header row height
    MAX_Y = PH - MG - 55

    pages: list = []

    def new_page(first=False):
        img = Image.new("RGB", (PW, PH), WHITE)
        d   = ImageDraw.Draw(img)
        y   = MG

        # Header bar (taller for bigger logo)
        d.rectangle([0, y, PW, y + 100], fill=RED)
        # Logo
        logo_path = Path(__file__).parent / "assets" / "volunteers kss insta profil pic.png"
        if logo_path.exists():
            try:
                logo = Image.open(str(logo_path)).convert("RGBA")
                lh = 90; lw = int(logo.width * lh / logo.height)
                logo = logo.resize((lw, lh), Image.LANCZOS)
                img.paste(logo, (MG, y + 5), logo)
            except Exception:
                pass
        bb = d.textbbox((0, 0), "KSS Body Evolution Wellness Center", font=f_lg)
        cx = (PW - (bb[2] - bb[0])) // 2
        d.text((cx, y + 28), "KSS Body Evolution Wellness Center", font=f_lg, fill=WHITE)
        y += 112

        # Title
        title = "Patient Records"
        bb = d.textbbox((0, 0), title, font=f_md)
        d.text(((PW - (bb[2] - bb[0])) // 2, y), title, font=f_md, fill=RED)
        y += 38
        d.text((MG, y), f"Generated: {datetime.now().strftime('%d %B %Y')}   |   Total patients: {len(patients)}", font=f_sm, fill=GREY)
        y += 30
        d.rectangle([MG, y, PW - MG, y + 2], fill=RED)
        y += 10
        return img, d, y

    def draw_table_header(d, y):
        d.rectangle([MG, y, PW - MG, y + HDR], fill=RED)
        for i, (label, _) in enumerate(COLS):
            d.text((CX[i] + 6, y + 11), label, font=f_hd, fill=WHITE)
        return y + HDR

    img, d, y = new_page(first=True)
    y = draw_table_header(d, y)

    for idx, p in enumerate(patients):
        if y + RH > MAX_Y:
            # Footer
            d.rectangle([MG, PH - MG - 28, PW - MG, PH - MG - 26], fill=RED)
            d.text((MG, PH - MG - 20), f"KSS Body Evolution  |  Page {len(pages)+1}", font=f_sm, fill=GREY)
            pages.append(img)
            img, d, y = new_page()
            y = draw_table_header(d, y)

        bg = WHITE if idx % 2 == 0 else LIGHT
        d.rectangle([MG, y, PW - MG, y + RH], fill=bg, outline=LGREY)

        cells = [
            str(idx + 1),
            str(p.get("patient_id", "")),
            str(p.get("name", "")),
            str(p.get("age", "")),
            str(p.get("gender", "")),
            str(p.get("mobile", "")),
            str(p.get("area", "")),
            str(p.get("email", "") or ""),
        ]
        for i, cell in enumerate(cells):
            d.text((CX[i] + 6, y + 9), cell, font=f_sm, fill=DARK)
        y += RH

    # Last page footer
    d.rectangle([MG, PH - MG - 28, PW - MG, PH - MG - 26], fill=RED)
    d.text((MG, PH - MG - 20), f"KSS Body Evolution  |  Page {len(pages)+1}", font=f_sm, fill=GREY)
    pages.append(img)

    buf = BytesIO()
    pages[0].save(buf, format="PDF", resolution=R.DPI, save_all=True, append_images=pages[1:])
    buf.seek(0)
    return buf.getvalue()


def show_bulk_download(db: DatabaseManager):
    """Export patient info (ID, Name, Age, Gender, Mobile, Area, Email) as a single PDF."""
    st.markdown('<div class="section-title">Patient Records Export</div>', unsafe_allow_html=True)
    st.markdown("**Download a PDF listing all patient details — ID, Name, Age, Gender, Mobile, Area, Email**")
    st.divider()

    if db is None:
        st.warning("Database not connected.")
        return

    all_patients = db.get_all_active_patients()
    if not all_patients:
        st.info("No patients found.")
        return

    # ── Patient selection table ───────────────────────────────────────────
    st.subheader(f"Patients  ({len(all_patients)} total)")

    col_all, col_none, _ = st.columns([1, 1, 6])
    if col_all.button("Select All",   key="bulk_sel_all",  width='stretch'):
        for p in all_patients:
            st.session_state[f"bulk_chk_{p['patient_id']}"] = True
    if col_none.button("Deselect All", key="bulk_sel_none", width='stretch'):
        for p in all_patients:
            st.session_state[f"bulk_chk_{p['patient_id']}"] = False

    header_cols = st.columns([0.5, 1.2, 2.5, 0.8, 0.9, 1.5, 1.5, 2.0])
    for col, label in zip(header_cols, ["", "ID", "Name", "Age", "Gender", "Mobile", "Area", "Email"]):
        col.markdown(f"**{label}**")

    selected_patients = []
    for p in all_patients:
        chk_key = f"bulk_chk_{p['patient_id']}"
        if chk_key not in st.session_state:
            st.session_state[chk_key] = True
        row = st.columns([0.5, 1.2, 2.5, 0.8, 0.9, 1.5, 1.5, 2.0])
        checked = row[0].checkbox("", key=chk_key, label_visibility="collapsed")
        row[1].write(p.get("patient_id", ""))
        row[2].write(p.get("name", ""))
        row[3].write(str(p.get("age", "")))
        row[4].write(p.get("gender", ""))
        row[5].write(p.get("mobile", ""))
        row[6].write(p.get("area", ""))
        row[7].write(str(p.get("email", "") or ""))
        if checked:
            selected_patients.append(p)

    st.divider()
    st.info(f"**{len(selected_patients)}** patient(s) selected")

    gen_col, _ = st.columns([2, 5])
    gen_clicked = gen_col.button(
        f"Generate PDF  ({len(selected_patients)} patients)",
        type="primary",
        width='stretch',
        key="bulk_generate_btn",
        disabled=len(selected_patients) == 0,
    )

    if gen_clicked:
        st.session_state["bulk_pdf_bytes"] = None
        with st.spinner("Building patient records PDF..."):
            try:
                pdf_bytes = _build_patient_records_pdf(selected_patients)
                st.session_state["bulk_pdf_bytes"] = pdf_bytes
                st.success(f"✅ PDF ready — **{len(selected_patients)}** patient(s) included.")
            except Exception as exc:
                st.error(f"Error generating PDF: {exc}")

    if st.session_state.get("bulk_pdf_bytes"):
        today = datetime.now().strftime("%Y%m%d")
        pdf_name = f"KSS_Patient_Records_{today}.pdf"
        st.download_button(
            label=f"⬇️  Download PDF  ({pdf_name})",
            data=st.session_state["bulk_pdf_bytes"],
            file_name=pdf_name,
            mime="application/pdf",
            width='stretch',
            type="primary",
            key="bulk_download_btn",
        )


def show_settings():
    """Display settings page"""
    st.markdown('<div class="section-title">Settings</div>', unsafe_allow_html=True)
    st.divider()
    
    st.subheader("Application Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current User:** Admin")
        st.write("**Session Status:** Active")
        st.write("**Last Login:** Today")
    
    with col2:
        st.write("**Database:** Connected")
        st.write("**Gemini API:** Configured")
        st.write("**PDF Generator:** Ready")
    
    st.divider()

    # ── GEMINI API KEYS MANAGEMENT ──────────────────────────────────────────
    st.subheader("🔑 Gemini API Keys Management")
    
    # Current API status
    st.markdown("**Current API Status:**")
    gen_key = st.session_state.get("user_generation_api_key", "").strip()
    trans_key = st.session_state.get("user_translation_api_key", "").strip()
    
    col_a, col_b = st.columns(2)
    with col_a:
        if gen_key:
            st.success(f"✅ **Generation Key:** Using user-provided key (ending in ...{gen_key[-4:]})")
        else:
            st.info("⚙️ **Generation Key:** Using system/environment key")
    with col_b:
        if trans_key:
            st.success(f"✅ **Translation Key:** Using user-provided key (ending in ...{trans_key[-4:]})")
        else:
            st.info("⚙️ **Translation Key:** Using system/environment key")
    
    st.divider()
    
    # API keys input form
    st.markdown("**Update Your API Keys:**")
    
    new_gen_key = st.text_input(
        "Generation API Key",
        value=gen_key,
        type="password",
        help="Your Google Gemini API key for health generation analysis. Leave blank to use system key."
    )
    
    new_trans_key = st.text_input(
        "Translation API Key",
        value=trans_key,
        type="password",
        help="Your Google Gemini API key for translation. Can be the same or different from generation key."
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("✅ Validate & Update Keys", type="primary", use_container_width=True):
            from ai_engine import validate_api_key
            validation_errors = []
            
            # Validate generation key if provided
            if new_gen_key and new_gen_key != gen_key:
                with st.spinner("🔑 Validating Generation API Key..."):
                    result = validate_api_key(new_gen_key)
                    if not result["valid"]:
                        error_msg = result.get("quota_message") if result.get("quota_warning") else result.get("message", "Invalid key")
                        validation_errors.append(f"❌ Generation Key: {error_msg}")
                    else:
                        st.session_state["user_generation_api_key"] = new_gen_key
                        st.success(f"✅ Generation Key: {result.get('message', 'Valid')}")
            
            # Validate translation key if provided
            if new_trans_key and new_trans_key != trans_key:
                with st.spinner("🔑 Validating Translation API Key..."):
                    result = validate_api_key(new_trans_key)
                    if not result["valid"]:
                        error_msg = result.get("quota_message") if result.get("quota_warning") else result.get("message", "Invalid key")
                        validation_errors.append(f"❌ Translation Key: {error_msg}")
                    else:
                        st.session_state["user_translation_api_key"] = new_trans_key
                        st.success(f"✅ Translation Key: {result.get('message', 'Valid')}")
            
            # Show validation errors
            if validation_errors:
                for err in validation_errors:
                    st.warning(err)
                if len(validation_errors) == 2:
                    st.error("⚠️ API key validation failed. Please check your keys and try again, or leave them blank to use the system keys.")
            elif new_gen_key != gen_key or new_trans_key != trans_key:
                st.success("🎉 All API keys updated and validated successfully!")
            else:
                st.info("No changes detected in API keys.")
    
    with col_btn2:
        if st.button("🔄 Reset to System Keys", use_container_width=True):
            st.session_state["user_generation_api_key"] = ""
            st.session_state["user_translation_api_key"] = ""
            st.success("✅ API keys reset to system/environment defaults")
            st.rerun()
    
    with col_btn3:
        if st.button("ℹ️ Check API Quota", use_container_width=True):
            gen_key_to_check = new_gen_key or gen_key
            if gen_key_to_check:
                with st.spinner("Checking API quota..."):
                    from ai_engine import validate_api_key
                    result = validate_api_key(gen_key_to_check)
                    if result.get("quota_warning"):
                        st.warning(f"⚠️ {result.get('quota_message')}")
                    elif result["valid"]:
                        st.success(f"✅ {result.get('message')}")
                    else:
                        st.error(f"❌ {result.get('message')}")
            else:
                st.info("ℹ️ Using system API key for quota check...")
    
    st.divider()
    
    st.subheader("Clinic Information")
    
    clinic_name = st.text_input("Clinic Name", value="KSS Body Evolution Wellness Center")
    clinic_phone = st.text_input("Clinic Phone", value="Your Phone Number")
    clinic_email = st.text_input("Clinic Email", value="your-email@clinic.com")
    
    if st.button("Save Clinic Settings", type="primary"):
        st.success("Clinic settings saved successfully!")
    
    st.divider()
    
    st.subheader("System Information")
    st.info("""
    **Version:** 1.0.0
    **Framework:** Streamlit
    **Database:** Supabase (PostgreSQL)
    **AI Engine:** Google Gemini
    **PDF Library:** ReportLab
    """)

    st.divider()

    # About KSS
    kss_logo = (
        f'<img src="data:image/png;base64,{LOGO_B64}" '
        f'style="width:104px;height:104px;border-radius:50%;'
        f'border:3px solid #E2A822;object-fit:cover;'
        f'box-shadow:0 4px 18px rgba(196,18,47,0.35);" />'
        if LOGO_B64 else ""
    )
    _kss_html = (
        '<div style="background:linear-gradient(135deg,#1A0A0F 0%,#2D0D18 100%);'
        'border-radius:16px;padding:32px 36px;'
        'border:1px solid rgba(226,168,34,0.25);'
        'box-shadow:0 8px 30px rgba(196,18,47,0.2);">'
        '<div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;">' +
        kss_logo +
        '<div>'
        '<div style="font-size:22px;font-weight:800;'
        'background:linear-gradient(135deg,#E2A822,#fff);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'letter-spacing:1px;">KSS</div>'
        '<div style="font-size:14px;color:rgba(245,230,208,0.7);'
        'letter-spacing:2px;text-transform:uppercase;margin-top:2px;">'
        'Krishna Sada Sahayate</div>'
        '</div></div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'
        '<div style="background:rgba(255,255,255,0.05);border-radius:12px;'
        'padding:18px 20px;border-left:3px solid #E2A822;">'
        '<div style="font-size:10px;color:rgba(226,168,34,0.7);'
        'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Founder</div>'
        '<div style="font-size:17px;font-weight:700;color:#F5E6D0;margin-bottom:4px;">'
        'Prithvirajsinh Parmar</div>'
        '<div style="font-size:12px;color:rgba(245,230,208,0.55);line-height:1.6;">'
        'Founder &amp; Visionary Leader<br/>KSS &ndash; Krishna Sada Sahayate'
        '</div></div>'
        '<div style="background:rgba(255,255,255,0.05);border-radius:12px;'
        'padding:18px 20px;border-left:3px solid #C4122F;">'
        '<div style="font-size:10px;color:rgba(196,18,47,0.8);'
        'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Developed By</div>'
        '<div style="font-size:17px;font-weight:700;color:#F5E6D0;margin-bottom:4px;">'
        'Vraj Kanubhai Sondagar</div>'
        '<div style="font-size:12px;color:rgba(245,230,208,0.55);line-height:1.6;">'
        '<span style="background:linear-gradient(135deg,#C4122F,#E2A822);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'font-weight:700;font-size:13px;">Member of KSS</span><br/>'
        'Krishna Sada Sahayate<br/>AI &amp; Software Developer'
        '</div></div>'
        '</div>'
        '<div style="margin-top:20px;padding:14px 16px;border-radius:10px;'
        'background:rgba(226,168,34,0.07);'
        'border:1px solid rgba(226,168,34,0.15);'
        'font-size:12px;color:rgba(245,230,208,0.6);line-height:1.8;text-align:center;">'
        '"<em>Krishna Sada Sahayate</em> &mdash; Krishna always helps."<br/>'
        '<span style="color:rgba(226,168,34,0.6);font-size:11px;">'
        'KSS Body Evolution Wellness System &copy; 2026</span>'
        '</div></div>'
    )
    st.markdown(_kss_html, unsafe_allow_html=True)


def main():
    """Main application"""
    # --- Cookie manager must be initialised BEFORE any auth check ---
    # It renders a hidden iframe that reads browser cookies and restores
    # the session even after a full page refresh (F5 / Ctrl+R).
    cookie_manager = stx.CookieManager(key="wellness_cookies")

    # Restore authentication AND last page from cookies (survive F5 / Ctrl+R)
    # SKIP restore if the user explicitly just logged out (_logged_out flag),
    # otherwise the stale cookie would re-authenticate them immediately.
    if not st.session_state.get("authenticated", False):
        if st.session_state.pop("_logged_out", False):
            # User just logged out — do NOT restore from cookie this cycle.
            # Also overwrite the cookie so future page loads don't re-auth.
            try:
                cookie_manager.set("wellness_auth", "logged_out",
                                   expires_at=datetime.now() + timedelta(seconds=5))
            except Exception:
                pass
        else:
            auth_cookie = cookie_manager.get("wellness_auth")
            if auth_cookie == "authenticated":
                st.session_state.authenticated = True
                # Set login time to track session duration for timeout validation
                if "login_time" not in st.session_state:
                    st.session_state.login_time = datetime.now()

    # Restore last visited page (only when session_state has been reset)
    if "current_page" not in st.session_state:
        saved_page = cookie_manager.get("wellness_page")
        if saved_page:
            st.session_state.current_page = saved_page

    # Check authentication (includes timeout validation)
    if not AuthManager.is_authenticated():
        show_login_page(cookie_manager=cookie_manager)
        st.stop()
    
    # Initialize app
    initialize_app()

    # ── Luxury Blessing Banner (authenticated users only) ─────────────
    st.markdown("""
    <style>
    @keyframes kss-shimmer {
        0%   { background-position: -300% center; }
        100% { background-position:  300% center; }
    }
    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(196, 18, 47, 0.20), inset 0 1px 0 rgba(226,168,34,0.20); }
        50% { box-shadow: 0 0 30px rgba(196, 18, 47, 0.35), inset 0 1px 0 rgba(226,168,34,0.25); }
    }
    </style>
    <div style="text-align:center; margin: 16px 0 28px 0;">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #FFF8EE 0%, #FEF3E0 50%, #FFF8EE 100%);
            border: 2px solid rgba(196,18,47,0.22);
            border-radius: 60px;
            padding: 10px 40px;
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

    # Sidebar
    with st.sidebar:
        # ── Logo ────────────────────────────────────────────────────────────
        if LOGO_B64:
            st.markdown(f"""
            <div style="text-align:center; padding: 18px 0 10px 0;">
                <img src="data:image/png;base64,{LOGO_B64}"
                     style="width:120px; height:120px; border-radius:50%;
                            border: 3px solid #E2A822;
                            box-shadow: 0 4px 20px rgba(196,18,47,0.4);
                            object-fit:cover;
                            animation: fadeUp 0.6s ease;" />
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; padding-bottom:4px;">
            <span style="font-size:17px; font-weight:700; color:#E2A822;
                         letter-spacing:0.5px;">KSS BODY EVOLUTION</span><br/>
            <span style="font-size:11px; color:#F5E6D0AA;
                         letter-spacing:1px;">WELLNESS SYSTEM</span>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        # ── Navigation ──────────────────────────────────────────────────────
        pages = {
            "Dashboard":          "Dashboard",
            "Patients":           "Patient Management",
            "Evaluation":         "Evaluation",
            "Health History":     "History",
            "Patient Records PDF": "Bulk Export",
            "Settings":           "Settings",
        }

        current_page = st.session_state.get("current_page", "Dashboard")

        for label, page_key in pages.items():
            if st.button(
                label,
                width='stretch',
                key=f"nav_{page_key}",
                type="primary" if current_page == page_key else "secondary"
            ):
                st.session_state.current_page = page_key
                cookie_manager.set("wellness_page", page_key,
                                   expires_at=datetime.now() + timedelta(hours=8))
                st.rerun()

        st.divider()

        # ── User / Logout ────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding: 6px 0;">
            <div style="width:42px; height:42px; border-radius:50%;
                        background:linear-gradient(135deg,#C4122F,#E2A822);
                        display:inline-flex; align-items:center;
                        justify-content:center; font-size:16px;font-weight:700;color:white;
                        box-shadow:0 4px 14px rgba(196,18,47,0.45);
                        margin-bottom:6px;font-family:'Cormorant Garamond',serif;">A</div>
            <div style="font-size:13px; font-weight:600;
                        color:#F5E6D0;">Admin</div>
            <div style="font-size:11px; color:#F5E6D077;">System Administrator</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display session timeout info
        if st.session_state.get("login_time"):
            login_time = st.session_state.get("login_time")
            elapsed_minutes = int((datetime.now() - login_time).total_seconds() / 60)
            remaining_hours = AuthManager.SESSION_TIMEOUT_HOURS - elapsed_minutes / 60
            
            if remaining_hours > 0:
                st.caption(f"🔐 Session active for {elapsed_minutes} min | {remaining_hours:.1f}h remaining")
            else:
                st.warning("Session expired. Please login again.")
                AuthManager.logout()
                st.rerun()

        if st.button("Logout", width='stretch', type="secondary"):
            try:
                cookie_manager.delete("wellness_auth")
            except Exception:
                pass
            try:
                cookie_manager.delete("wellness_page")
            except Exception:
                pass
            AuthManager.logout()
            st.rerun()

        st.markdown("""
        <div style="margin-top:20px; padding:12px; border-radius:10px;
                    background:rgba(255,255,255,0.05); font-size:11px;
                    color:#F5E6D077; line-height:1.7;">
            Add patients before evaluations<br/>
            Keep metrics within valid ranges<br/>
            AI follows preventive approach<br/>
            Data secured in Supabase
        </div>
        <div style="margin-top:14px; padding:10px 12px; border-radius:10px;
                    border:1px solid rgba(226,168,34,0.18);
                    background:rgba(226,168,34,0.05);
                    text-align:center; font-size:10px; line-height:1.8;
                    color:rgba(245,230,208,0.45);">
            <span style="color:rgba(226,168,34,0.65);font-weight:600;
                         letter-spacing:0.5px;">KSS</span>
            &nbsp;·&nbsp; Krishna Sada Sahayate<br/>
            Founder: <span style="color:rgba(245,230,208,0.6);">Prithvirajsinh Parmar</span><br/>
            Developed By: <span style="color:rgba(245,230,208,0.6);">Vraj K. Sondagar</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    db = st.session_state.db
    current_page = st.session_state.get("current_page", "Dashboard")
    
    if current_page == "Dashboard":
        show_dashboard(db)
    elif current_page == "Patient Management":
        show_patient_management(db)
    elif current_page == "Evaluation":
        show_evaluation_page(db)
    elif current_page == "History":
        show_health_history(db)
    elif current_page == "Bulk Export":
        show_bulk_download(db)
    elif current_page == "Settings":
        show_settings()
    
    # Footer
    show_footer()


if __name__ == "__main__":
    main()
