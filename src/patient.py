"""
Patient Management Module
CRUD operations for patient records
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from database import DatabaseManager


class PatientManager:
    """Manages patient operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def show_add_patient_form(self):
        """Display form to add new patient"""
        st.subheader("➕ Add New Patient")
        
        with st.form("add_patient_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="Enter patient name")
                age = st.number_input("Age *", min_value=1, max_value=120, step=1)
                gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                height = st.number_input("Height (cm) *", min_value=50.0, max_value=250.0, step=0.1)
            
            with col2:
                mobile = st.text_input("Mobile Number * (Unique)", placeholder="Enter 10-digit mobile")
                email = st.text_input("Email (Optional)", placeholder="Enter email")
                area = st.text_input("Area/City *", placeholder="Enter area")
                address = st.text_area("Address", placeholder="Enter full address", height=80)
            
            notes = st.text_area("Additional Notes", placeholder="Any medical history or notes")
            
            submit = st.form_submit_button("Create Patient", width='stretch', type="primary")
            
            if submit:
                # Validation
                if not name or not mobile or not area:
                    st.error("Please fill in all required fields (*)")
                    return
                
                if len(mobile) < 10:
                    st.error("Mobile number must be at least 10 digits")
                    return
                
                patient_data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "height": height,
                    "mobile": mobile,
                    "email": email if email else None,
                    "area": area,
                    "address": address,
                    "notes": notes
                }
                
                success, message, patient_id = self.db.create_patient(patient_data)
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
    
    def show_search_patient(self) -> Optional[str]:
        """Display patient search interface"""
        st.subheader("🔍 Search Patient")
        
        search_type = st.radio("Search by:", ["Name", "Mobile Number"], horizontal=True)
        
        if search_type == "Name":
            search_query = st.text_input("Enter patient name", placeholder="Type name...")
        else:
            search_query = st.text_input("Enter mobile number", placeholder="Type mobile...")
        
        if search_query:
            patients = self.db.search_patients(search_query)
            
            if patients:
                st.success(f"Found {len(patients)} patient(s)")
                
                selected_patient = st.selectbox(
                    "Select patient:",
                    options=patients,
                    format_func=lambda p: f"{p['patient_id']} - {p['name']} ({p['mobile']})"
                )
                
                if selected_patient:
                    return selected_patient['patient_id']
            else:
                st.info("No patients found")
        
        return None
    
    def show_patient_details(self, patient_id: str):
        """Display patient details"""
        patient = self.db.get_patient(patient_id)
        
        if not patient:
            st.error("Patient not found")
            return
        
        st.markdown("### 👤 Patient Information")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Patient ID", patient["patient_id"])
        with col2:
            st.metric("Age", f"{patient['age']} years")
        with col3:
            st.metric("Gender", patient["gender"])
        with col4:
            st.metric("Height", f"{patient['height']} cm")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Mobile:** {patient['mobile']}")
            st.write(f"**Email:** {patient['email'] or 'Not provided'}")
        
        with col2:
            st.write(f"**Area:** {patient['area']}")
            st.write(f"**Address:** {patient['address']}")
            st.write(f"**Notes:** {patient['notes'] or 'None'}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            created_date = patient['created_at'][:10] if patient['created_at'] else "N/A"
            st.write(f"**Created:** {created_date}")
        
        with col2:
            updated_date = patient['updated_at'][:10] if patient['updated_at'] else "N/A"
            st.write(f"**Last Updated:** {updated_date}")
    
    def show_all_patients_table(self):
        """Display all patients in a table"""
        st.subheader("📋 All Patients")
        
        patients = self.db.get_all_active_patients()
        
        if not patients:
            st.info("No patients found")
            return
        
        st.write(f"Total Active Patients: **{len(patients)}**")
        
        # Format data for display
        display_data = []
        for p in patients:
            display_data.append({
                "ID": p["patient_id"],
                "Name": p["name"],
                "Age": p["age"],
                "Gender": p["gender"],
                "Mobile": p["mobile"],
                "Area": p["area"],
                "Email": p["email"] or "-"
            })
        
        st.dataframe(
            display_data,
            width='stretch',
            hide_index=True,
            column_config={
                "ID": st.column_config.Column(width=100),
                "Name": st.column_config.Column(width=150),
                "Age": st.column_config.Column(width=80),
                "Gender": st.column_config.Column(width=100),
                "Mobile": st.column_config.Column(width=120),
                "Area": st.column_config.Column(width=120),
                "Email": st.column_config.Column(width=150),
            }
        )
    
    def show_update_patient_form(self, patient_id: str):
        """Display form to update patient"""
        patient = self.db.get_patient(patient_id)
        
        if not patient:
            st.error("Patient not found")
            return
        
        st.subheader("✏️ Update Patient Information")
        
        with st.form("update_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name", value=patient["name"])
                age = st.number_input("Age", value=int(patient["age"]), min_value=1, max_value=120)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient["gender"]))
                height = st.number_input("Height (cm)", value=float(patient["height"]), min_value=50.0, max_value=250.0)
            
            with col2:
                mobile = st.text_input("Mobile Number", value=patient["mobile"])
                email = st.text_input("Email", value=patient["email"] or "")
                area = st.text_input("Area/City", value=patient["area"])
                address = st.text_area("Address", value=patient["address"], height=80)
            
            notes = st.text_area("Additional Notes", value=patient["notes"] or "")
            
            submit = st.form_submit_button("Update Patient", width='stretch', type="primary")
            
            if submit:
                update_data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "height": height,
                    "mobile": mobile,
                    "email": email if email else None,
                    "area": area,
                    "address": address,
                    "notes": notes
                }
                
                success, message = self.db.update_patient(patient_id, update_data)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    def show_delete_confirmation(self, patient_id: str):
        """Show delete confirmation dialog"""
        patient = self.db.get_patient(patient_id)
        
        if not patient:
            st.error("Patient not found")
            return
        
        st.warning(f"⚠️ Are you sure you want to delete patient {patient['patient_id']} - {patient['name']}?")
        st.markdown("**This action will soft-delete the patient and hide all their records.**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Confirm Delete", width='stretch', type="secondary"):
                success, message = self.db.soft_delete_patient(patient_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("❌ Cancel", width='stretch'):
                st.info("Delete cancelled")
