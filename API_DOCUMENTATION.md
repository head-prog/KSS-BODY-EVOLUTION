# 📚 API Documentation & Module Reference

## Overview

This document provides detailed API documentation for all modules in the Body Evolution Wellness System.

---

## 1. Authentication Module (`auth.py`)

### Class: `AuthManager`

#### Methods

##### `hash_password(password: str) -> str`
Hash a password using SHA256.

**Parameters:**
- `password` (str): Password to hash

**Returns:**
- `str`: SHA256 hash of password

**Example:**
```python
from src.auth import AuthManager

hashed = AuthManager.hash_password("my_password")
print(hashed)  # Output: hash_string
```

---

##### `verify_password(password: str, password_hash: str) -> bool`
Verify a password against its hash.

**Parameters:**
- `password` (str): Plain password to verify
- `password_hash` (str): Hash to compare against

**Returns:**
- `bool`: True if password matches, False otherwise

**Example:**
```python
is_valid = AuthManager.verify_password("my_password", hashed)
```

---

##### `login(username: str, password: str) -> Tuple[bool, str]`
Authenticate user.

**Parameters:**
- `username` (str): Username
- `password` (str): Password

**Returns:**
- `Tuple[bool, str]`: (success, message)

**Example:**
```python
success, message = AuthManager.login("admin", "admin123")
if success:
    AuthManager.set_authenticated(True)
```

---

##### `is_authenticated() -> bool`
Check if user is logged in.

**Returns:**
- `bool`: True if authenticated

---

## 2. Database Module (`database.py`)

### Class: `DatabaseManager`

#### Patient Operations

##### `create_patient(patient_data: Dict) -> Tuple[bool, str, Optional[str]]`
Create a new patient record.

**Parameters:**
- `patient_data` (Dict): Patient details including name, age, gender, height, mobile, email, area, address, notes

**Returns:**
- `Tuple[bool, str, Optional[str]]`: (success, message, patient_id)

**Example:**
```python
from src.database import DatabaseManager

db = DatabaseManager()
success, message, patient_id = db.create_patient({
    "name": "John Doe",
    "age": 35,
    "gender": "Male",
    "height": 175.5,
    "mobile": "9876543210",
    "email": "john@example.com",
    "area": "New York",
    "address": "123 Main St",
    "notes": "No known allergies"
})
```

---

##### `get_patient(patient_id: str) -> Optional[Dict]`
Get patient by patient_id.

**Parameters:**
- `patient_id` (str): Patient ID (e.g., "P0001")

**Returns:**
- `Optional[Dict]`: Patient record or None

**Example:**
```python
patient = db.get_patient("P0001")
if patient:
    print(patient["name"])
```

---

##### `search_patients(query: str) -> List[Dict]`
Search patients by name or mobile.

**Parameters:**
- `query` (str): Search term

**Returns:**
- `List[Dict]`: List of matching patients

**Example:**
```python
results = db.search_patients("John")
```

---

##### `get_all_active_patients() -> List[Dict]`
Get all active patients.

**Returns:**
- `List[Dict]`: List of all active patients

---

##### `update_patient(patient_id: str, patient_data: Dict) -> Tuple[bool, str]`
Update patient information.

**Parameters:**
- `patient_id` (str): Patient ID
- `patient_data` (Dict): Fields to update

**Returns:**
- `Tuple[bool, str]`: (success, message)

---

##### `soft_delete_patient(patient_id: str) -> Tuple[bool, str]`
Soft delete patient (mark as inactive).

**Parameters:**
- `patient_id` (str): Patient ID

**Returns:**
- `Tuple[bool, str]`: (success, message)

---

#### Health Records Operations

##### `create_health_record(health_data: Dict) -> Tuple[bool, str, Optional[str]]`
Create a new health evaluation record.

**Parameters:**
- `health_data` (Dict): Health metrics and scores

**Returns:**
- `Tuple[bool, str, Optional[str]]`: (success, message, record_id)

**Example:**
```python
success, message, record_id = db.create_health_record({
    "patient_id": "P0001",
    "weight": 75.5,
    "bmi": 24.5,
    "bmr": 1800,
    "body_fat": 22.5,
    "visceral_fat": 8,
    "body_age": 35,
    "tsf": 12.5,
    "muscle_mass": 38,
    "wellness_score": 3.5,
    "ai_summary": "Health analysis..."
})
```

---

##### `get_patient_health_records(patient_id: str) -> List[Dict]`
Get all health records for a patient.

**Parameters:**
- `patient_id` (str): Patient ID

**Returns:**
- `List[Dict]`: List of health records

---

##### `get_latest_health_record(patient_id: str) -> Optional[Dict]`
Get the latest health record for a patient.

**Parameters:**
- `patient_id` (str): Patient ID

**Returns:**
- `Optional[Dict]`: Latest health record or None

---

#### Dashboard Operations

##### `get_dashboard_stats() -> Dict`
Get dashboard statistics.

**Returns:**
- `Dict`: Statistics including total_patients, total_evaluations, high_risk_patients

**Example:**
```python
stats = db.get_dashboard_stats()
print(f"Total patients: {stats['total_patients']}")
```

---

## 3. Patient Management Module (`patient.py`)

### Class: `PatientManager`

#### Methods

##### `show_add_patient_form()`
Display Streamlit form to add new patient.

**Example:**
```python
from src.patient import PatientManager

pm = PatientManager(db)
pm.show_add_patient_form()
```

---

##### `show_search_patient() -> Optional[str]`
Display patient search interface.

**Returns:**
- `Optional[str]`: Selected patient_id or None

---

##### `show_patient_details(patient_id: str)`
Display patient information.

**Parameters:**
- `patient_id` (str): Patient ID

---

##### `show_all_patients_table()`
Display all patients in a table.

---

##### `show_update_patient_form(patient_id: str)`
Display form to update patient.

**Parameters:**
- `patient_id` (str): Patient ID

---

##### `show_delete_confirmation(patient_id: str)`
Show delete confirmation dialog.

**Parameters:**
- `patient_id` (str): Patient ID

---

## 4. Rule Engine Module (`rule_engine.py`)

### Class: `RuleEngine`

#### Methods

##### `categorize_bmi(bmi: float) -> str`
Categorize BMI value.

**Parameters:**
- `bmi` (float): BMI value (10-50)

**Returns:**
- `str`: BMI category

**Categories:**
- < 18: "Underweight"
- 18-23: "Normal Weight"
- 23-25: "Overweight"
- 25-30: "Obesity Grade 1"
- > 30: "High Obesity Risk"

**Example:**
```python
from src.rule_engine import RuleEngine

category = RuleEngine.categorize_bmi(24.5)
print(category)  # Output: "Overweight"
```

---

##### `categorize_visceral_fat(vf: float) -> str`
Categorize Visceral Fat.

**Parameters:**
- `vf` (float): Visceral fat value (1-30)

**Returns:**
- `str`: Visceral fat category

**Categories:**
- 1-8: "Normal"
- 9-14: "High"
- 15+: "Very High Risk"

---

##### `categorize_body_fat(body_fat: float, gender: str) -> str`
Categorize Body Fat % based on gender.

**Parameters:**
- `body_fat` (float): Body fat percentage
- `gender` (str): "Male" or "Female"

**Returns:**
- `str`: Body fat category

---

##### `categorize_muscle_mass(muscle_mass: float, gender: str) -> str`
Categorize Muscle Mass % based on gender.

**Parameters:**
- `muscle_mass` (float): Muscle mass percentage
- `gender` (str): "Male" or "Female"

**Returns:**
- `str`: Muscle mass category

---

##### `calculate_wellness_score(categories: HealthCategories) -> float`
Calculate wellness score (0-10 scale).

**Parameters:**
- `categories` (HealthCategories): Categorized health data

**Returns:**
- `float`: Wellness score (0=perfect, 10=critical)

---

##### `process_health_metrics(health_data: Dict, patient_age: int, gender: str) -> Dict`
Process health metrics and generate categories.

**Parameters:**
- `health_data` (Dict): Raw health metrics
- `patient_age` (int): Patient's actual age
- `gender` (str): Patient's gender

**Returns:**
- `Dict`: Categorized metrics and wellness score

**Example:**
```python
result = RuleEngine.process_health_metrics({
    "weight": 75.5,
    "bmi": 24.5,
    "bmr": 1800,
    "body_fat": 22.5,
    "visceral_fat": 8,
    "body_age": 35,
    "tsf": 12.5,
    "muscle_mass": 38
}, patient_age=35, gender="Male")

print(result["wellness_score"])  # 0-10
print(result["overall_risk_level"])  # Risk assessment
```

---

## 5. AI Engine Module (`ai_engine.py`)

### Class: `AIHealthAnalyzer`

#### Methods

##### `analyze_health_data(health_summary: str) -> Tuple[bool, str]`
Send health summary to Gemini and get analysis.

**Parameters:**
- `health_summary` (str): Structured health summary

**Returns:**
- `Tuple[bool, str]`: (success, response_text)

**Example:**
```python
from src.ai_engine import AIHealthAnalyzer

analyzer = AIHealthAnalyzer()
success, response = analyzer.analyze_health_data(health_summary)

if success:
    print(response)  # AI analysis
```

---

##### `test_gemini_connection() -> bool`
Test Gemini API connection.

**Returns:**
- `bool`: True if connection successful

**Example:**
```python
if test_gemini_connection():
    print("API is working")
```

---

## 6. PDF Generator Module (`pdf_generator.py`)

### Class: `PDFReportGenerator`

#### Methods

##### `generate_report(patient: Dict, health_record: Dict, health_categories: Dict, ai_analysis: str) -> bytes`
Generate complete PDF report.

**Parameters:**
- `patient` (Dict): Patient data
- `health_record` (Dict): Health metrics
- `health_categories` (Dict): Categorized metrics
- `ai_analysis` (str): AI-generated analysis

**Returns:**
- `bytes`: PDF file as bytes

**Example:**
```python
from src.pdf_generator import PDFReportGenerator

generator = PDFReportGenerator()
pdf_bytes = generator.generate_report(patient, health_record, categories, ai_analysis)

with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

---

## 7. Evaluation Module (`evaluation.py`)

### Class: `EvaluationManager`

#### Methods

##### `show_evaluation_form(patient_id: str) -> Optional[Dict]`
Display health evaluation form.

**Parameters:**
- `patient_id` (str): Patient ID

**Returns:**
- `Optional[Dict]`: Health data if submitted, None otherwise

---

##### `validate_health_data(health_data: Dict) -> Dict`
Validate health metrics.

**Parameters:**
- `health_data` (Dict): Health metrics to validate

**Returns:**
- `Dict`: {"valid": bool, "message": str}

**Validation Ranges:**
- BMI: 10-50
- Body Fat: 5-60%
- Visceral Fat: 1-30
- Muscle Mass: 10-60%
- BMR: 800-3000

---

##### `process_evaluation(patient: Dict, health_data: Dict) -> Tuple[bool, str, Optional[Dict]]`
Process evaluation through rule engine and AI.

**Parameters:**
- `patient` (Dict): Patient data
- `health_data` (Dict): Health metrics

**Returns:**
- `Tuple[bool, str, Optional[Dict]]`: (success, message, report_data)

---

##### `show_evaluation_report(report_data: Dict)`
Display evaluation report and download options.

**Parameters:**
- `report_data` (Dict): Complete report data

---

## 8. Utilities Module (`utils.py`)

### Functions

##### `initialize_session_state()`
Initialize all session state variables.

---

##### `format_date(date_str: str) -> str`
Format ISO date string to readable format.

**Parameters:**
- `date_str` (str): ISO format date string

**Returns:**
- `str`: Formatted date

---

##### `get_risk_color(risk_level: str) -> str`
Get color code for risk level.

**Parameters:**
- `risk_level` (str): Risk level string

**Returns:**
- `str`: Emoji color indicator

---

##### `validate_email(email: str) -> bool`
Validate email format.

**Parameters:**
- `email` (str): Email address

**Returns:**
- `bool`: True if valid format

---

##### `validate_mobile(mobile: str) -> bool`
Validate mobile number format.

**Parameters:**
- `mobile` (str): Mobile number

**Returns:**
- `bool`: True if valid format (10+ digits)

---

## Error Handling

All modules use try-catch blocks and return error messages:

```python
success, message = db.create_patient(data)
if not success:
    print(f"Error: {message}")
```

---

## Data Flow Diagram

```
Patient Input
    ↓
[Validation]
    ↓
[Rule Engine] → Categories & Wellness Score
    ↓
[AI Engine] → Gemini Analysis
    ↓
[Database] → Save Health Record
    ↓
[PDF Generator] → A4 Report
    ↓
Download/Print
```

---

## Environment Variables

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key
GEMINI_API_KEY=your_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=sha256_hash
```

---

## Code Examples

### Complete Evaluation Workflow

```python
from src.database import DatabaseManager
from src.patient import PatientManager
from src.evaluation import EvaluationManager
from src.rule_engine import RuleEngine
from src.ai_engine import AIHealthAnalyzer
from src.pdf_generator import PDFReportGenerator

# Initialize
db = DatabaseManager()

# 1. Get patient
patient = db.get_patient("P0001")

# 2. Process health data
health_data = {
    "weight": 75.5,
    "bmi": 24.5,
    "bmr": 1800,
    "body_fat": 22.5,
    "visceral_fat": 8,
    "body_age": 35,
    "tsf": 12.5,
    "muscle_mass": 38
}

# 3. Validate
evaluation_mgr = EvaluationManager(db)
result = evaluation_mgr.validate_health_data(health_data)

if result["valid"]:
    # 4. Process evaluation
    success, msg, report_data = evaluation_mgr.process_evaluation(patient, health_data)
    
    if success:
        # 5. Generate PDF
        pdf_gen = PDFReportGenerator()
        pdf_bytes = pdf_gen.generate_report(
            report_data["patient"],
            report_data["health_record"],
            report_data["health_categories"],
            report_data["ai_analysis"]
        )
        
        # 6. Save PDF
        with open("wellness_report.pdf", "wb") as f:
            f.write(pdf_bytes)
```

---

**For more information, see README.md**
