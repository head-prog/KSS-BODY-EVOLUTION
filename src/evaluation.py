"""
Health Evaluation Module
Handles health metrics input and validation
"""

import streamlit as st
import re
from typing import Dict, Optional, Tuple
from database import DatabaseManager
from rule_engine import RuleEngine
from ai_engine import AIHealthAnalyzer
from pdf_generator import PDFReportGenerator


class EvaluationManager:
    """Manages health evaluation process"""
    
    # Validation ranges
    VALIDATION_RANGES = {
        "bmi": (10, 50),
        "body_fat": (5, 60),
        "visceral_fat": (1, 30),
        "muscle_mass": (10, 60),
        "bmr": (800, 3000)
    }
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.rule_engine = RuleEngine()
    
    def show_evaluation_form(self, patient_id: str) -> Optional[Dict]:
        """
        Display health evaluation form.
        Fields that couldn't be detected by the body-composition machine
        (common with elderly patients) can be individually marked as
        'Not detected' — they are then stored as None and skipped in
        validation, rule-engine categorisation, and the PDF report.
        Returns: health_data dict if submitted, None otherwise.
        """
        patient = self.db.get_patient(patient_id)
        if not patient:
            st.error("Patient not found")
            return None

        st.subheader(f"📊 Health Evaluation for {patient['name']}")

        # ── Not-detected toggles (outside the form so they re-render on click) ─
        # Each checkbox key: nd_<field>
        _ND = [
            ("nd_body_fat",     "Body Fat (%)"),
            ("nd_visceral_fat", "Visceral Fat"),
            ("nd_muscle_mass",  "Muscle Mass (%)"),
            ("nd_bmr",          "BMR (kcal/day)"),
            ("nd_body_age",     "Body Age"),
            ("nd_tsf",          "TSF"),
        ]
        for _k, _ in _ND:
            if _k not in st.session_state:
                st.session_state[_k] = False

        with st.expander("⚙️ Mark fields not detected by machine", expanded=False):
            st.caption(
                "Tick any measurement the machine could **not** read "
                "(e.g. elderly patients with implants, low conductivity, or impedance errors). "
                "Ticked fields will be skipped in validation and shown as *Not Measured* in the report."
            )
            _nd_cols = st.columns(3)
            for _i, (_k, _lbl) in enumerate(_ND):
                with _nd_cols[_i % 3]:
                    st.checkbox(f"❌  {_lbl}", key=_k)

        def _nd(k):
            return bool(st.session_state.get(k, False))

        nd_bf  = _nd("nd_body_fat")
        nd_vf  = _nd("nd_visceral_fat")
        nd_mm  = _nd("nd_muscle_mass")
        nd_bmr = _nd("nd_bmr")
        nd_ba  = _nd("nd_body_age")
        nd_tsf = _nd("nd_tsf")

        with st.form("health_evaluation_form"):
            col1, col2 = st.columns(2)

            with col1:
                weight = st.number_input(
                    "Weight (kg) *",
                    min_value=20.0, max_value=300.0, value=70.0, step=0.1,
                    help="Patient's current weight in kilograms",
                )
                bmi = st.number_input(
                    "BMI *",
                    min_value=10.0, max_value=50.0, value=22.0, step=0.1,
                    help="Body Mass Index (10-50)",
                )
                bmr = st.number_input(
                    "BMR (kcal/day)" + (" — ❌ Not detected" if nd_bmr else " *"),
                    min_value=800, max_value=3000, value=1500, step=10,
                    disabled=nd_bmr,
                    help="Basal Metabolic Rate in kcal per day (800-3000)",
                )
                body_fat = st.number_input(
                    "Body Fat (%)" + (" — ❌ Not detected" if nd_bf else " *"),
                    min_value=5.0, max_value=60.0, value=20.0, step=0.1,
                    disabled=nd_bf,
                    help="Body fat percentage (5-60%)",
                )

            with col2:
                visceral_fat = st.number_input(
                    "Visceral Fat" + (" — ❌ Not detected" if nd_vf else " *"),
                    min_value=1.0, max_value=30.0, value=5.0, step=0.1,
                    disabled=nd_vf,
                    help="Visceral fat level (1-30)",
                )
                body_age = st.number_input(
                    "Body Age (years)" + (" — ❌ Not detected" if nd_ba else " *"),
                    min_value=1, max_value=120, value=30, step=1,
                    disabled=nd_ba,
                    help="Metabolic age in years",
                )
                tsf = st.number_input(
                    "TSF (Triceps Skinfold)" + (" — ❌ Not detected" if nd_tsf else " *"),
                    min_value=0.0, max_value=50.0, value=10.0, step=0.1,
                    disabled=nd_tsf,
                    help="Triceps skinfold measurement in mm",
                )
                muscle_mass = st.number_input(
                    "Muscle Mass (%)" + (" — ❌ Not detected" if nd_mm else " *"),
                    min_value=10.0, max_value=60.0, value=30.0, step=0.1,
                    disabled=nd_mm,
                    help="Muscle mass percentage (10-60%)",
                )

            st.markdown("---")
            notes = st.text_area(
                "Evaluation Notes (Optional)",
                placeholder="Any additional observations during evaluation",
                height=100,
            )

            submitted = st.form_submit_button(
                "Generate Health Report", width='stretch', type="primary"
            )

            if submitted:
                health_data = {
                    "patient_id":    patient_id,
                    "weight":        weight,
                    "bmi":           bmi,
                    "bmr":           None if nd_bmr else bmr,
                    "body_fat":      None if nd_bf  else body_fat,
                    "visceral_fat":  None if nd_vf  else visceral_fat,
                    "body_age":      None if nd_ba  else body_age,
                    "tsf":           None if nd_tsf else tsf,
                    "muscle_mass":   None if nd_mm  else muscle_mass,
                    "notes":         notes,
                }
                validation_result = self.validate_health_data(health_data)
                if not validation_result["valid"]:
                    st.error(f"Validation Error: {validation_result['message']}")
                    return None
                return health_data

        return None
    
    def validate_health_data(self, health_data: Dict) -> Dict:
        """
        Validate health metrics.
        Fields that are None (marked as 'Not detected by machine') are skipped.
        Returns: {"valid": bool, "message": str}
        """
        try:
            lo, hi = self.VALIDATION_RANGES["bmi"]
            if not (lo <= health_data["bmi"] <= hi):
                return {"valid": False,
                        "message": f"BMI must be between {lo} and {hi}"}

            if health_data.get("body_fat") is not None:
                lo, hi = self.VALIDATION_RANGES["body_fat"]
                if not (lo <= health_data["body_fat"] <= hi):
                    return {"valid": False,
                            "message": f"Body Fat must be between {lo} and {hi}%"}

            if health_data.get("visceral_fat") is not None:
                lo, hi = self.VALIDATION_RANGES["visceral_fat"]
                if not (lo <= health_data["visceral_fat"] <= hi):
                    return {"valid": False,
                            "message": f"Visceral Fat must be between {lo} and {hi}"}

            if health_data.get("muscle_mass") is not None:
                lo, hi = self.VALIDATION_RANGES["muscle_mass"]
                if not (lo <= health_data["muscle_mass"] <= hi):
                    return {"valid": False,
                            "message": f"Muscle Mass must be between {lo} and {hi}%"}

            if health_data.get("bmr") is not None:
                lo, hi = self.VALIDATION_RANGES["bmr"]
                if not (lo <= health_data["bmr"] <= hi):
                    return {"valid": False,
                            "message": f"BMR must be between {lo} and {hi} kcal/day"}

            return {"valid": True, "message": "All validations passed"}

        except Exception as e:
            return {"valid": False, "message": f"Validation error: {str(e)}"}
    
    def process_evaluation(self, patient: Dict, health_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Process health evaluation through rule engine and AI
        Returns: (success, message, complete_report_data)
        """
        try:
            # Step 1: Apply rule engine
            st.info("⚙️ Processing health metrics...")
            
            categories = RuleEngine.process_health_metrics(
                health_data, 
                patient["age"], 
                patient["gender"]
            )
            
            if "error" in categories:
                return False, f"Rule engine error: {categories['error']}", None
            
            health_summary = categories.pop("health_summary")
            
            # Step 2: Send to Gemini AI
            st.info("🤖 Generating AI analysis...")
            
            ai_analyzer = AIHealthAnalyzer()
            ai_success, ai_response = ai_analyzer.analyze_health_data(health_summary)
            
            if not ai_success:
                return False, f"AI Analysis failed: {ai_response}", None
            
            # Step 3: Save health record
            st.info("💾 Saving health record...")
            
            record_data = {
                "patient_id":   patient["patient_id"],
                "weight":       health_data["weight"],
                "bmi":          health_data["bmi"],
                "bmr":          health_data.get("bmr"),          # may be None
                "body_fat":     health_data.get("body_fat"),     # may be None
                "visceral_fat": health_data.get("visceral_fat"), # may be None
                "body_age":     health_data.get("body_age"),     # may be None
                "tsf":          health_data.get("tsf"),          # may be None
                "muscle_mass":  health_data.get("muscle_mass"),  # may be None
                "wellness_score": categories["wellness_score"],
                "ai_summary":   ai_response,
            }
            
            db_success, db_message, record_id = self.db.create_health_record(record_data)
            
            if not db_success:
                return False, f"Database error: {db_message}", None
            
            # Prepare complete report
            report_data = {
                "patient": patient,
                "health_record": record_data,
                "health_record_id": record_id,
                "health_categories": categories,
                "ai_analysis": ai_response
            }
            
            return True, "Health evaluation completed successfully!", report_data
        
        except Exception as e:
            return False, f"Processing error: {str(e)}", None
    
    def show_evaluation_report(self, report_data: Dict):
        """Display evaluation report and provide download options"""
        if not report_data:
            st.error("No report data available")
            return
        
        patient = report_data["patient"]
        health_record = report_data["health_record"]
        health_categories = report_data["health_categories"]
        ai_analysis = report_data["ai_analysis"]
        
        # Display report sections
        st.success("✅ Health Evaluation Complete!")
        
        # Patient Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Risk", health_categories.get("overall_risk_level", "N/A"))
        with col2:
            st.metric("Wellness Score", f"{health_categories.get('wellness_score', 0)}/10")
        with col3:
            st.metric("BMI Status", health_categories.get("bmi_category", "N/A"))
        with col4:
            _ba = health_record.get("body_age")
            st.metric("Body Age", f"{_ba} yrs" if _ba is not None else "Not Measured")
        
        st.divider()
        
        # Metrics Display
        st.subheader("📊 Body Metrics & Categories")
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.write("**Physical Measurements:**")
            st.write(f"• Weight: {health_record['weight']} kg")
            st.write(f"• BMI: {health_record['bmi']} ({health_categories.get('bmi_category', 'N/A')})")
            _bf = health_record.get("body_fat")
            st.write(f"• Body Fat: {f'{_bf}%' if _bf is not None else '❌ Not measured'} ({health_categories.get('body_fat_category', 'N/A')})")
            _bmr = health_record.get("bmr")
            st.write(f"• BMR: {f'{_bmr} kcal/day' if _bmr is not None else '❌ Not measured'}")

        with metrics_col2:
            st.write("**Body Composition:**")
            _vf = health_record.get("visceral_fat")
            st.write(f"• Visceral Fat: {_vf if _vf is not None else '❌ Not measured'} ({health_categories.get('visceral_fat_category', 'N/A')})")
            _mm = health_record.get("muscle_mass")
            st.write(f"• Muscle Mass: {f'{_mm}%' if _mm is not None else '❌ Not measured'} ({health_categories.get('muscle_mass_category', 'N/A')})")
            _tsf = health_record.get("tsf")
            st.write(f"• TSF: {_tsf if _tsf is not None else '❌ Not measured'}")
            _ba2 = health_record.get("body_age")
            st.write(f"• Body Age: {f'{_ba2} years' if _ba2 is not None else '❌ Not measured'} ({health_categories.get('body_age_status', 'N/A')})")
        
        st.divider()
        
        # AI Analysis
        st.subheader("🤖 AI Health Analysis & Recommendations")
        st.markdown(ai_analysis)
        
        st.divider()
        
        # PDF Generation and Download
        st.subheader("📄 Generate Report")
        
        # PDF Download — language selector
        st.subheader("Download Report")

        pdf_lang = st.radio(
            "Report Language:",
            ["English", "Hindi / हिंदी", "Gujarati / ગુજરાતી"],
            horizontal=True,
            key="eval_pdf_lang",
        )
        lang_map  = {"English": "English", "Hindi / हिंदी": "Hindi", "Gujarati / ગુજરાતી": "Gujarati"}
        lang_code = {"English": "EN", "Hindi": "HI", "Gujarati": "GU"}
        sel_lang  = lang_map[pdf_lang]

        # Report mode + translation engine (only shown for non-English)
        trans_method = "google"
        report_mode = "translate"  # "direct" or "translate"
        if sel_lang != "English":
            mode_opt = st.radio(
                "Report Mode:",
                [f"📝 Direct — AI writes in {sel_lang}", "🔄 Translated — Convert English analysis"],
                horizontal=True,
                key="eval_report_mode",
                help=(
                    f"Direct: Gemini AI generates the full health report directly in {sel_lang} "
                    "(highest quality, natural phrasing).\n"
                    "Translated: The English AI analysis is translated to the chosen language."
                ),
            )
            report_mode = "direct" if "Direct" in mode_opt else "translate"

            if report_mode == "translate":
                trans_opt = st.radio(
                    "Translation Engine:",
                    ["🌐 Google Translate", "✨ Gemini AI"],
                    horizontal=True,
                    key="eval_trans_method",
                    help="Google Translate is fast. Gemini AI gives richer medical phrasing.",
                )
                trans_method = "gemini" if "Gemini" in trans_opt else "google"

        # ── Generate / Cancel state ─────────────────────────────────────────────────────
        if "eval_pdf_generating" not in st.session_state:
            st.session_state["eval_pdf_generating"] = False
        if "eval_pdf_bytes" not in st.session_state:
            st.session_state["eval_pdf_bytes"] = None
        if "eval_pdf_cancelled" not in st.session_state:
            st.session_state["eval_pdf_cancelled"] = False

        col1, col2 = st.columns(2)
        with col1:
            generate_clicked = st.button(
                f"Generate {sel_lang} Report",
                width='stretch',
                type="primary",
                key="eval_generate_btn",
            )
        with col2:
            cancel_clicked = st.button(
                "Cancel",
                width='stretch',
                key="eval_cancel_btn",
            )

        if cancel_clicked:
            st.session_state["eval_pdf_generating"] = False
            st.session_state["eval_pdf_bytes"] = None
            st.session_state["eval_pdf_cancelled"] = True
            st.rerun()

        if st.session_state.get("eval_pdf_cancelled"):
            st.warning("Report generation cancelled.")
            st.session_state["eval_pdf_cancelled"] = False

        if generate_clicked:
            st.session_state["eval_pdf_generating"] = True
            st.session_state["eval_pdf_bytes"] = None
            try:
                with st.spinner(f"Generating {sel_lang} report... Please wait."):
                    ai_for_pdf = ai_analysis
                    if sel_lang != "English":
                        if report_mode == "direct":
                            # Re-generate the analysis directly in the target language
                            try:
                                _cats = RuleEngine.process_health_metrics(
                                    health_record,
                                    int(patient.get("age", 0)),
                                    patient.get("gender", "Male"),
                                )
                                _health_summary = _cats.get("health_summary", "")
                                _ok, _resp = AIHealthAnalyzer.generate_in_language(
                                    _health_summary, sel_lang
                                )
                                if _ok:
                                    ai_for_pdf = _resp
                                else:
                                    st.warning(f"⚠️ {sel_lang} AI generation failed — using English analysis. Error: {_resp}")
                            except Exception as _exc:
                                st.warning(f"⚠️ {sel_lang} report generation error: {_exc}. Using English fallback.")
                        else:
                            try:
                                ai_for_pdf = AIHealthAnalyzer.translate_for_pdf(
                                    ai_analysis, sel_lang, method=trans_method
                                )
                            except Exception as _exc:
                                st.warning(f"⚠️ Translation failed: {_exc}. Using English fallback.")
                    pdf_generator = PDFReportGenerator()
                    pdf_bytes = pdf_generator.generate_report(
                        patient,
                        health_record,
                        health_categories,
                        ai_for_pdf,
                        language=sel_lang,
                    )
                st.session_state["eval_pdf_bytes"] = pdf_bytes
                st.session_state["eval_pdf_generating"] = False
                st.success("Report generation successful!")
            except Exception as e:
                st.session_state["eval_pdf_generating"] = False
                st.error(f"Error generating PDF: {str(e)}")

        if st.session_state.get("eval_pdf_bytes"):
            pid   = patient.get("patient_id", "report")
            pname = re.sub(r"[^A-Za-z0-9]+", "_", str(patient.get("name", "Patient"))).strip("_")
            fname = f"KSS_Wellness_Report_{pname}_{pid}.pdf"
            st.download_button(
                label=f"Download PDF ({sel_lang})",
                data=st.session_state["eval_pdf_bytes"],
                file_name=fname,
                mime="application/pdf",
                width='stretch',
                type="primary",
                key="eval_download_btn",
            )

        if st.button("Print Report", width='stretch', key="eval_print_btn"):
            st.info("Use your browser's print function (Ctrl+P / Cmd+P) to print this report")
