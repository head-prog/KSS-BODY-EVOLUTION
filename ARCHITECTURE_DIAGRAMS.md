# 🏗️ System Architecture & Data Flow Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB FRONTEND                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • Dashboard                                             │   │
│  │  • Patient Management (CRUD)                           │   │
│  │  • Health Evaluation Form                              │   │
│  │  • Report Display & Download                           │   │
│  │  • Health History View                                 │   │
│  │  • Settings & Configuration                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PYTHON BACKEND                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Authentication Module (auth.py)                         │   │
│  │  • Login/Logout                                         │   │
│  │  • Session Management                                  │   │
│  │  • Password Hashing                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Patient Management Module (patient.py)                 │   │
│  │  • Add Patient                                          │   │
│  │  • Search Patients                                      │   │
│  │  • Update Patient                                       │   │
│  │  • Delete Patient                                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Evaluation Module (evaluation.py)                       │   │
│  │  • Health Metrics Form                                  │   │
│  │  • Validation                                           │   │
│  │  • Workflow Orchestration                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Rule Engine (rule_engine.py)                            │   │
│  │  • BMI Categorization                                   │   │
│  │  • Body Composition Analysis                            │   │
│  │  • Wellness Score Calculation                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ AI Integration (ai_engine.py)                           │   │
│  │  • Gemini API Call                                      │   │
│  │  • Response Validation                                  │   │
│  │  • Preventive Healthcare Focus                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ PDF Generator (pdf_generator.py)                        │   │
│  │  • A4 Report Generation                                 │   │
│  │  • Professional Formatting                              │   │
│  │  • Report Download/Print                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Database Manager (database.py)                          │   │
│  │  • Patient CRUD Operations                              │   │
│  │  • Health Records Management                            │   │
│  │  • Dashboard Statistics                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
     ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
     │  Supabase   │   │   Gemini     │   │  ReportLab   │
     │  PostgreSQL │   │   API        │   │   PDF        │
     └─────────────┘   └──────────────┘   └──────────────┘
```

---

## Health Evaluation Data Flow

```
┌─────────────────────┐
│  Select Patient     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Enter Health Metrics               │
│  • Weight, BMI, BMR                 │
│  • Body Fat %, Visceral Fat         │
│  • Body Age, TSF, Muscle Mass       │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  VALIDATION LAYER                   │
│  • Range Checking                   │
│  • Data Type Validation             │
│  • Required Fields Check            │
└──────────┬──────────────────────────┘
           │
           ▼ (if valid)
┌─────────────────────────────────────┐
│  RULE ENGINE                        │
│  • Categorize BMI                   │
│  • Categorize Visceral Fat          │
│  • Categorize Body Fat              │
│  • Categorize Muscle Mass           │
│  • Evaluate Body Age                │
│  • Calculate Wellness Score         │
│  • Determine Risk Level             │
│  ↓                                  │
│  Generate Health Summary            │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  GEMINI AI ENGINE                   │
│  • Send Structured Prompt           │
│  • System Instructions Applied      │
│  • Generate Analysis                │
│  • Validate Response Format         │
│  ↓                                  │
│  Return 8-Section Response:         │
│  1. Current Health Summary          │
│  2. Risk Assessment                 │
│  3. Future Health Risks             │
│  4. What To Eat                     │
│  5. What To Avoid                   │
│  6. Lifestyle Recommendations       │
│  7. Future Risk Warning             │
│  8. Medical Disclaimer              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  DATABASE STORAGE                   │
│  • Save Health Record               │
│  • Store AI Analysis                │
│  • Update Patient Record            │
│  • Log Audit Trail                  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  PDF GENERATION                     │
│  • Create Report Header             │
│  • Add Patient Info                 │
│  • Insert Metrics Table             │
│  • Include AI Analysis              │
│  • Add Disclaimer                   │
│  ↓                                  │
│  Generate A4 PDF                    │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  REPORT DELIVERY                    │
│  • Display Report in UI             │
│  • Download PDF Button              │
│  • Print Report Option              │
│  • Store in Database                │
└─────────────────────────────────────┘
```

---

## Database Schema Diagram

```
┌─────────────────────────────────────┐
│         PATIENTS TABLE              │
├─────────────────────────────────────┤
│ id (UUID, PK)                       │
│ patient_id (VARCHAR, UNIQUE)        │
│ name (VARCHAR)                      │
│ age (INTEGER)                       │
│ gender (VARCHAR)                    │
│ height (DECIMAL)                    │
│ mobile (VARCHAR, UNIQUE)            │
│ email (VARCHAR)                     │
│ area (VARCHAR)                      │
│ address (TEXT)                      │
│ notes (TEXT)                        │
│ is_active (BOOLEAN)                 │
│ created_at (TIMESTAMP)              │
│ updated_at (TIMESTAMP)              │
└────────────────┬────────────────────┘
                 │ (1:N)
                 │
┌────────────────▼────────────────────┐
│      HEALTH_RECORDS TABLE           │
├─────────────────────────────────────┤
│ id (UUID, PK)                       │
│ patient_id (VARCHAR, FK)            │
│ weight (DECIMAL)                    │
│ bmi (DECIMAL)                       │
│ bmr (INTEGER)                       │
│ body_fat (DECIMAL)                  │
│ visceral_fat (DECIMAL)              │
│ body_age (INTEGER)                  │
│ tsf (DECIMAL)                       │
│ muscle_mass (DECIMAL)               │
│ wellness_score (DECIMAL)            │
│ ai_summary (TEXT)                   │
│ created_at (TIMESTAMP)              │
└─────────────────────────────────────┘
```

---

## Class Diagram

```
┌──────────────────────────────────┐
│      AuthManager                 │
├──────────────────────────────────┤
│ - ADMIN_USERNAME: str            │
│ - ADMIN_PASSWORD_HASH: str       │
├──────────────────────────────────┤
│ + hash_password(pwd)             │
│ + verify_password(pwd, hash)     │
│ + login(user, pwd)               │
│ + is_authenticated()             │
│ + set_authenticated(val)         │
│ + logout()                       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      DatabaseManager             │
├──────────────────────────────────┤
│ - client: Client                 │
├──────────────────────────────────┤
│ + create_patient(data)           │
│ + get_patient(id)                │
│ + search_patients(query)         │
│ + update_patient(id, data)       │
│ + soft_delete_patient(id)        │
│ + create_health_record(data)     │
│ + get_patient_health_records(id) │
│ + get_dashboard_stats()          │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      PatientManager              │
├──────────────────────────────────┤
│ - db: DatabaseManager            │
├──────────────────────────────────┤
│ + show_add_patient_form()        │
│ + show_search_patient()          │
│ + show_patient_details(id)       │
│ + show_update_patient_form(id)   │
│ + show_delete_confirmation(id)   │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      RuleEngine                  │
├──────────────────────────────────┤
│ + categorize_bmi(bmi)            │
│ + categorize_visceral_fat(vf)    │
│ + categorize_body_fat(bf, gen)   │
│ + categorize_muscle_mass(mm)     │
│ + calculate_wellness_score()     │
│ + process_health_metrics()       │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      AIHealthAnalyzer            │
├──────────────────────────────────┤
│ - model: GenerativeModel         │
│ - SYSTEM_INSTRUCTION: str        │
├──────────────────────────────────┤
│ + analyze_health_data(summary)   │
│ - _validate_and_format_response()│
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      PDFReportGenerator          │
├──────────────────────────────────┤
│ - styles: StyleSheet             │
│ - CLINIC_NAME: str               │
├──────────────────────────────────┤
│ + generate_report(...)           │
│ - _create_header()               │
│ - _create_patient_info_section() │
│ - _create_metrics_table()        │
│ - _create_footer()               │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      EvaluationManager           │
├──────────────────────────────────┤
│ - db: DatabaseManager            │
│ - rule_engine: RuleEngine        │
├──────────────────────────────────┤
│ + show_evaluation_form(id)       │
│ + validate_health_data(data)     │
│ + process_evaluation(...)        │
│ + show_evaluation_report(data)   │
└──────────────────────────────────┘
```

---

## Module Interaction Diagram

```
                    ┌─────────────┐
                    │  Streamlit  │
                    │   Frontend  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐        ┌────────────┐
    │  Auth  │        │Patient │        │Evaluation  │
    │ Module │        │Manager │        │Manager     │
    └────┬───┘        └───┬────┘        └──────┬─────┘
         │                │                    │
         └────────────────┼────────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Database     │
                   │ Manager      │
                   └──────┬───────┘
                          │
            ┌─────────────┼──────────────┐
            │             │              │
            ▼             ▼              ▼
    ┌─────────────┐  ┌──────────┐  ┌──────────┐
    │Rule Engine  │  │AI Engine │  │PDF       │
    │             │  │(Gemini)  │  │Generator │
    └─────────────┘  └──────────┘  └──────────┘
            │
            └──────────────┬──────────────┐
                           │              │
                    ┌──────▼──────┐  ┌───▼──────┐
                    │  Supabase   │  │ Storage  │
                    │  Database   │  │ (Future) │
                    └─────────────┘  └──────────┘
```

---

## Authentication Flow

```
┌──────────────────┐
│  Login Page      │
└────────┬─────────┘
         │
         ▼
┌─────────────────────┐
│ Enter Credentials   │
└────────┬────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ AuthManager.login(user, password)  │
└────────┬───────────────────────────┘
         │
         ├─→ Check username matches ✓
         │
         ├─→ Hash password
         │
         ├─→ Compare with stored hash ✓
         │
         ▼
┌──────────────────────┐
│ Set Session State    │
│ authenticated = true │
└────────┬─────────────┘
         │
         ▼
┌─────────────────┐
│ Redirect to     │
│ Dashboard       │
└─────────────────┘
```

---

## Validation Chain

```
Health Metrics Input
        │
        ▼
┌─────────────────────────────────┐
│ Input Type Check                │
│ (numbers, required fields, etc) │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Range Validation                │
│ BMI: 10-50 ✓                    │
│ Body Fat: 5-60 ✓                │
│ Visceral Fat: 1-30 ✓            │
│ Muscle Mass: 10-60 ✓            │
│ BMR: 800-3000 ✓                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Business Logic Validation       │
│ • Check correlations            │
│ • Verify consistency            │
└────────────┬────────────────────┘
             │
             ▼ (Valid)
┌─────────────────────────────────┐
│ Process Evaluation              │
└─────────────────────────────────┘
```

---

## Risk Assessment Scoring

```
Wellness Score Calculation:
Start: 5.0 (Neutral)

BMI Impact:
├─ Normal:        -0.5
├─ Overweight:    +1.0
├─ Grade 1:       +2.0
└─ High Obesity:  +3.0

Visceral Fat Impact:
├─ Normal:        -0.5
├─ High:          +1.5
└─ Very High:     +2.5

Body Fat Impact:
├─ Normal:        -0.5
├─ Moderate:      +1.0
└─ High Risk:     +2.0

Muscle Mass Impact:
├─ Low:           +1.5
└─ High:          -1.0

Final Score: 0-10 range
(Clamped to valid range)

Risk Levels:
├─ 0-3:   Low Risk
├─ 3-5:   Moderate Risk
├─ 5-7:   High Risk
└─ 7-10:  Very High Risk
```

---

## PDF Report Structure

```
┌─────────────────────────────────────┐
│         REPORT HEADER               │
│  • Clinic Name                      │
│  • Report Date                      │
│  • Report ID                        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    PATIENT INFORMATION              │
│  • Name, ID, Age, Gender            │
│  • Contact Details                  │
│  • Area, Address                    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   BODY METRICS TABLE                │
│  ┌────────────────────────────────┐ │
│  │ Metric | Value | Category      │ │
│  ├────────────────────────────────┤ │
│  │ Weight │ 75kg  │ -             │ │
│  │ BMI    │ 24.5  │ Overweight    │ │
│  │ ...    │ ...   │ ...           │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    RISK ASSESSMENT SUMMARY          │
│  • Overall Risk Level               │
│  • Wellness Score                   │
│  • Key Findings                     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   WELLNESS ANALYSIS & RECOMMENDATIONS
│  (8 sections from AI)               │
│  1. Current Health Summary          │
│  2. Risk Assessment                 │
│  3. Future Health Risks             │
│  4. What To Eat                     │
│  5. What To Avoid                   │
│  6. Lifestyle Recommendations       │
│  7. Future Risk Warning             │
│  8. Medical Disclaimer              │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      REPORT FOOTER                  │
│  • Generated Date/Time              │
│  • Clinic Contact Info              │
│  • Medical Disclaimer               │
└─────────────────────────────────────┘
```

---

## Error Handling Strategy

```
User Action
    │
    ├─→ Input Validation
    │   └─→ Range Check
    │   └─→ Type Check
    │   └─→ Required Field Check
    │
    ├─→ Database Operation
    │   └─→ Connection Check
    │   └─→ Query Execution
    │   └─→ Error Handling
    │
    ├─→ API Call (Gemini)
    │   └─→ Connection Check
    │   └─→ Request Validation
    │   └─→ Response Parsing
    │
    └─→ File Generation (PDF)
        └─→ Template Check
        └─→ Data Validation
        └─→ File Creation

All errors:
├─→ Logged to console
├─→ Displayed to user
├─→ Gracefully handled
└─→ No data corruption
```

---

**All diagrams are ASCII-based for universal compatibility and can be copied into documentation.**
