"""
Database module for Supabase integration
Handles all database operations for patients and health records
"""

import os
import socket
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# Load environment variables
load_dotenv()

# ── Connection timeout (seconds) ────────────────────────────────────────────
_CONNECT_TIMEOUT = 6   # abort if Supabase doesn't reply within 6 s


def _is_supabase_reachable(url: str, timeout: int = _CONNECT_TIMEOUT) -> bool:
    """Quick TCP probe — returns False if the host can't be reached."""
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname
        port = 443
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except OSError:
        return False


class DatabaseManager:
    """Manages Supabase database connections and operations"""

    # Set when the first timeout is detected so we stop retrying every render
    _offline: bool = False

    def __init__(self):
        """Initialize Supabase client with a short connection timeout."""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        # ── Quick reachability probe ─────────────────────────────────────
        if not _is_supabase_reachable(self.url, timeout=_CONNECT_TIMEOUT):
            DatabaseManager._offline = True
            raise ConnectionError(
                "Cannot reach Supabase server — the project may be **paused**.\n\n"
                "➡  Visit https://supabase.com/dashboard → select your project → click **Resume**.\n"
                "After resuming, restart the app."
            )

        # ── Create client with per-request timeout ───────────────────────
        try:
            from supabase import ClientOptions
            options = ClientOptions(
                postgrest_client_timeout=_CONNECT_TIMEOUT,
                storage_client_timeout=_CONNECT_TIMEOUT,
            )
            self.client: Client = create_client(self.url, self.key, options=options)
        except (ImportError, TypeError):
            # Older supabase-py that doesn't accept ClientOptions
            self.client: Client = create_client(self.url, self.key)

        DatabaseManager._offline = False
    
    # ==================== PATIENT OPERATIONS ====================
    
    def get_next_patient_id(self) -> str:
        """Generate next patient ID (P0001, P0002, etc.)"""
        try:
            response = self.client.table("patients").select("patient_id").order("patient_id", desc=True).limit(1).execute()
            if response.data:
                last_id = response.data[0]["patient_id"]
                number = int(last_id[1:]) + 1
                return f"P{str(number).zfill(4)}"
            return "P0001"
        except Exception as e:
            st.error(f"Error generating patient ID: {str(e)}")
            return "P0001"
    
    def create_patient(self, patient_data: Dict) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new patient record
        Returns: (success, message, patient_id)
        """
        try:
            # Check if mobile already exists
            existing = self.client.table("patients").select("id").eq("mobile", patient_data["mobile"]).execute()
            if existing.data:
                return False, "Patient with this mobile number already exists", None
            
            # Generate patient ID
            patient_id = self.get_next_patient_id()
            
            patient_data["patient_id"] = patient_id
            patient_data["is_active"] = True
            patient_data["created_at"] = datetime.now().isoformat()
            patient_data["updated_at"] = datetime.now().isoformat()
            
            response = self.client.table("patients").insert(patient_data).execute()
            return True, f"Patient created successfully with ID: {patient_id}", patient_id
        except Exception as e:
            return False, f"Error creating patient: {str(e)}", None
    
    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get patient by patient_id"""
        try:
            response = self.client.table("patients").select("*").eq("patient_id", patient_id).eq("is_active", True).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching patient: {str(e)}")
            return None
    
    def search_patients(self, query: str) -> List[Dict]:
        """Search patients by name or mobile"""
        try:
            # Search by name
            name_results = self.client.table("patients").select("*").ilike("name", f"%{query}%").eq("is_active", True).execute()
            
            # Search by mobile
            mobile_results = self.client.table("patients").select("*").ilike("mobile", f"%{query}%").eq("is_active", True).execute()
            
            # Combine and remove duplicates
            combined = {r["id"]: r for r in name_results.data + mobile_results.data}
            return list(combined.values())
        except Exception as e:
            st.error(f"Error searching patients: {str(e)}")
            return []
    
    def get_all_active_patients(self) -> List[Dict]:
        """Get all active patients"""
        try:
            response = self.client.table("patients").select("*").eq("is_active", True).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching patients: {str(e)}")
            return []
    
    def update_patient(self, patient_id: str, patient_data: Dict) -> Tuple[bool, str]:
        """Update patient information"""
        try:
            patient_data["updated_at"] = datetime.now().isoformat()
            
            response = self.client.table("patients").update(patient_data).eq("patient_id", patient_id).execute()
            return True, "Patient updated successfully"
        except Exception as e:
            return False, f"Error updating patient: {str(e)}"
    
    def soft_delete_patient(self, patient_id: str) -> Tuple[bool, str]:
        """Soft delete patient (mark as inactive)"""
        try:
            response = self.client.table("patients").update(
                {"is_active": False, "updated_at": datetime.now().isoformat()}
            ).eq("patient_id", patient_id).execute()
            return True, "Patient deleted successfully"
        except Exception as e:
            return False, f"Error deleting patient: {str(e)}"
    
    # ==================== HEALTH RECORDS OPERATIONS ====================
    
    def create_health_record(self, health_data: Dict) -> Tuple[bool, str, Optional[str]]:
        """Create a new health evaluation record"""
        try:
            health_data["created_at"] = datetime.now().isoformat()
            
            response = self.client.table("health_records").insert(health_data).execute()
            record_id = response.data[0]["id"] if response.data else None
            return True, "Health record created successfully", record_id
        except Exception as e:
            return False, f"Error creating health record: {str(e)}", None
    
    def get_patient_health_records(self, patient_id: str) -> List[Dict]:
        """Get all health records for a patient"""
        try:
            response = self.client.table("health_records").select("*").eq("patient_id", patient_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching health records: {str(e)}")
            return []
    
    def get_latest_health_record(self, patient_id: str) -> Optional[Dict]:
        """Get the latest health record for a patient"""
        try:
            response = self.client.table("health_records").select("*").eq("patient_id", patient_id).order("created_at", desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching latest health record: {str(e)}")
            return None
    
    def update_health_record(self, record_id: str, health_data: Dict) -> Tuple[bool, str]:
        """Update a health record"""
        try:
            response = self.client.table("health_records").update(health_data).eq("id", record_id).execute()
            return True, "Health record updated successfully"
        except Exception as e:
            return False, f"Error updating health record: {str(e)}"
    
    # ==================== DASHBOARD OPERATIONS ====================
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        try:
            total_patients = len(self.client.table("patients").select("id").eq("is_active", True).execute().data)
            total_evaluations = len(self.client.table("health_records").select("id").execute().data)
            high_risk = len(self.client.table("health_records").select("id").gt("wellness_score", 7).execute().data)
            
            return {
                "total_patients": total_patients,
                "total_evaluations": total_evaluations,
                "high_risk_patients": high_risk
            }
        except OSError:
            DatabaseManager._offline = True
            return {"total_patients": 0, "total_evaluations": 0, "high_risk_patients": 0}
        except Exception as e:
            st.error(f"Error fetching dashboard stats: {str(e)}")
            return {"total_patients": 0, "total_evaluations": 0, "high_risk_patients": 0}
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent health records"""
        try:
            response = self.client.table("health_records").select("*").order("created_at", desc=True).limit(limit).execute()
            return response.data
        except OSError:
            # WinError 10060 / connection timeout — don't spam the UI
            DatabaseManager._offline = True
            return []
        except Exception as e:
            st.error(f"Error fetching recent activity: {str(e)}")
            return []


def init_database():
    """Initialize database tables if they don't exist"""
    try:
        db = DatabaseManager()
        return db
    except ConnectionError as e:
        # Shown as a warning banner — project paused or unreachable
        st.warning(str(e))
        return None
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return None
