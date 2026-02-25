"""
Utility functions for the application
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List
import pandas as pd


def initialize_session_state():
    """Initialize all session state variables with persistence across page refreshes"""
    # Authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    # Navigation & Patient Data
    if "current_patient_id" not in st.session_state:
        st.session_state.current_patient_id = None
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Form State Persistence — Patient Management
    if "pm_form_name" not in st.session_state:
        st.session_state.pm_form_name = ""
    if "pm_form_age" not in st.session_state:
        st.session_state.pm_form_age = 30
    if "pm_form_gender" not in st.session_state:
        st.session_state.pm_form_gender = "Male"
    if "pm_form_height" not in st.session_state:
        st.session_state.pm_form_height = 170.0
    if "pm_form_mobile" not in st.session_state:
        st.session_state.pm_form_mobile = ""
    if "pm_form_email" not in st.session_state:
        st.session_state.pm_form_email = ""
    if "pm_form_area" not in st.session_state:
        st.session_state.pm_form_area = ""
    if "pm_form_address" not in st.session_state:
        st.session_state.pm_form_address = ""
    if "pm_form_notes" not in st.session_state:
        st.session_state.pm_form_notes = ""
    
    # Form State Persistence — Evaluation
    if "eval_selected_patient" not in st.session_state:
        st.session_state.eval_selected_patient = None
    if "eval_form_weight" not in st.session_state:
        st.session_state.eval_form_weight = 0.0
    if "eval_form_bmi" not in st.session_state:
        st.session_state.eval_form_bmi = 0.0
    if "eval_form_body_fat" not in st.session_state:
        st.session_state.eval_form_body_fat = 0.0
    if "eval_form_visceral_fat" not in st.session_state:
        st.session_state.eval_form_visceral_fat = 0
    if "eval_form_muscle_mass" not in st.session_state:
        st.session_state.eval_form_muscle_mass = 0.0
    if "eval_form_bmr" not in st.session_state:
        st.session_state.eval_form_bmr = 0
    if "eval_form_body_age" not in st.session_state:
        st.session_state.eval_form_body_age = 0
    if "eval_form_tsf" not in st.session_state:
        st.session_state.eval_form_tsf = ""
    
    # PDF Generation State
    if "eval_pdf_generating" not in st.session_state:
        st.session_state.eval_pdf_generating = False
    if "eval_pdf_bytes" not in st.session_state:
        st.session_state.eval_pdf_bytes = None
    if "eval_pdf_cancelled" not in st.session_state:
        st.session_state.eval_pdf_cancelled = False
    
    # History State
    if "hist_pdf_bytes" not in st.session_state:
        st.session_state.hist_pdf_bytes = None
    if "hist_pdf_cancelled" not in st.session_state:
        st.session_state.hist_pdf_cancelled = False

    # User-supplied Gemini API keys (set at login; empty = use env fallback)
    if "user_generation_api_key" not in st.session_state:
        st.session_state.user_generation_api_key = ""
    if "user_translation_api_key" not in st.session_state:
        st.session_state.user_translation_api_key = ""


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    try:
        if not date_str:
            return "N/A"
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%d %b %Y, %H:%M")
    except:
        return date_str


def format_currency(amount: float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"


def get_risk_color(risk_level: str) -> str:
    """Get color code for risk level"""
    risk_level_lower = risk_level.lower()
    
    if "low" in risk_level_lower:
        return "🟢"
    elif "moderate" in risk_level_lower:
        return "🟡"
    elif "high" in risk_level_lower and "very" not in risk_level_lower:
        return "🔴"
    elif "very high" in risk_level_lower:
        return "🔴🔴"
    else:
        return "⚪"


def get_category_icon(category: str) -> str:
    """Get icon for category"""
    category_lower = category.lower()
    
    if "normal" in category_lower or "good" in category_lower or "excellent" in category_lower:
        return "✅"
    elif "high" in category_lower or "risk" in category_lower or "obesity" in category_lower:
        return "⚠️"
    elif "low" in category_lower:
        return "⚠️"
    
    return "•"


def create_patient_summary(patient: Dict) -> str:
    """Create a summary string of patient info"""
    return f"{patient['patient_id']} - {patient['name']} ({patient['age']}y, {patient['gender']})"


def format_health_metrics(health_record: Dict) -> Dict:
    """Format health metrics for display"""
    return {
        "Weight": f"{health_record.get('weight', 0)} kg",
        "BMI": f"{health_record.get('bmi', 0)}",
        "BMR": f"{health_record.get('bmr', 0)} kcal",
        "Body Fat": f"{health_record.get('body_fat', 0)}%",
        "Visceral Fat": f"{health_record.get('visceral_fat', 0)}",
        "Body Age": f"{health_record.get('body_age', 0)} years",
        "TSF": f"{health_record.get('tsf', 0)}",
        "Muscle Mass": f"{health_record.get('muscle_mass', 0)}%",
    }


def export_patients_to_csv(patients: List[Dict]) -> bytes:
    """Convert patients list to CSV"""
    if not patients:
        return b""
    
    df = pd.DataFrame(patients)
    return df.to_csv(index=False).encode('utf-8')


def export_health_records_to_csv(records: List[Dict]) -> bytes:
    """Convert health records list to CSV"""
    if not records:
        return b""
    
    df = pd.DataFrame(records)
    return df.to_csv(index=False).encode('utf-8')


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return True  # Email is optional
    
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_mobile(mobile: str) -> bool:
    """Validate mobile number format"""
    import re
    pattern = r'^\d{10,}$'
    return re.match(pattern, mobile) is not None


def get_age_group(age: int) -> str:
    """Get age group category"""
    if age < 18:
        return "Child"
    elif 18 <= age < 30:
        return "Young Adult"
    elif 30 <= age < 45:
        return "Adult"
    elif 45 <= age < 60:
        return "Middle-aged"
    else:
        return "Senior"


def get_bmi_category_color(bmi_category: str) -> str:
    """Get color for BMI category display"""
    category_lower = bmi_category.lower()
    
    if "normal" in category_lower:
        return "#00AA00"  # Green
    elif "underweight" in category_lower:
        return "#0066FF"  # Blue
    elif "overweight" in category_lower or "grade 1" in category_lower:
        return "#FF9900"  # Orange
    elif "obesity" in category_lower or "high" in category_lower:
        return "#FF0000"  # Red
    
    return "#CCCCCC"  # Gray


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_dashboard_metrics_summary(stats: Dict) -> str:
    """Create a summary text for dashboard metrics"""
    summary = f"""
    Total Patients: {stats.get('total_patients', 0)}
    Total Evaluations: {stats.get('total_evaluations', 0)}
    High Risk Patients: {stats.get('high_risk_patients', 0)}
    """
    return summary.strip()


def create_evaluation_summary(health_categories: Dict) -> str:
    """Create a brief evaluation summary"""
    summary_parts = [
        f"Risk Level: {health_categories.get('overall_risk_level', 'N/A')}",
        f"Wellness Score: {health_categories.get('wellness_score', 0)}/10",
        f"BMI: {health_categories.get('bmi_category', 'N/A')}",
        f"Body Fat: {health_categories.get('body_fat_category', 'N/A')}",
        f"Visceral Fat: {health_categories.get('visceral_fat_category', 'N/A')}",
        f"Muscle Mass: {health_categories.get('muscle_mass_category', 'N/A')}",
    ]
    return " | ".join(summary_parts)


def show_page_header(title: str, subtitle: str = ""):
    """Display consistent page header"""
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"**{subtitle}**")
    st.divider()


def show_info_box(title: str, content: str, box_type: str = "info"):
    """Show formatted info box"""
    if box_type == "success":
        st.success(f"✅ **{title}**\n{content}")
    elif box_type == "warning":
        st.warning(f"⚠️ **{title}**\n{content}")
    elif box_type == "error":
        st.error(f"❌ **{title}**\n{content}")
    else:
        st.info(f"ℹ️ **{title}**\n{content}")


def show_footer():
    """Display application footer"""
    st.divider()
    footer_html = """
    <div style="text-align: center; color: #666666; font-size: 12px; margin-top: 20px;">
        <p>
            <strong>Body Evolution Wellness System</strong> | 
            Version 1.0.0 | 
            <em>Powered by Streamlit & Gemini AI</em>
        </p>
        <p style="font-size: 11px;">
            ⚠️ <strong>Disclaimer:</strong> This system is for wellness evaluation purposes only. 
            It does not diagnose diseases. Always consult with a qualified healthcare professional.
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
