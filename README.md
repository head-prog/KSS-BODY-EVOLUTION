# 🏥 Body Evolution Wellness Evaluation System

A comprehensive AI-powered wellness evaluation system built with Streamlit, Supabase, and Google Gemini AI. The system provides health risk analysis, lifestyle recommendations, and generates professional PDF reports.

## ✨ Features

### 🔐 Authentication Module
- Secure admin login system
- Session-based authentication
- Password hashing with SHA256
- Protected dashboard access

### 👥 Patient Management (CRUD)
- Create new patient records with unique IDs (P0001, P0002, etc.)
- Search patients by name or mobile number
- Update patient information
- Soft delete functionality (maintains data integrity)
- View all active patients in a table
- Mobile and email validation

### 📊 Health Evaluation Module
Input comprehensive health metrics:
- Weight, BMI, BMR
- Body Fat %, Visceral Fat
- Body Age, TSF (Triceps Skinfold)
- Muscle Mass %

**Validation Ranges:**
- BMI: 10–50
- Body Fat %: 5–60
- Visceral Fat: 1–30
- Muscle Mass %: 10–60
- BMR: 800–3000 kcal

### ⚙️ Rule Engine (Pre-AI Processing)
Converts numeric values into meaningful categories:

**BMI Categories:**
- < 18: Underweight
- 18–23: Normal Weight
- 23–25: Overweight
- 25–30: Obesity Grade 1
- > 30: High Obesity Risk

**Visceral Fat Categories:**
- 1–8: Normal
- 9–14: High
- 15+: Very High Risk

**Body Fat Categories (Gender-specific):**
- Male: 14–17% Normal, >25% High Risk
- Female: 21–24% Normal, >35% High Risk

**Wellness Score:** 0–10 scale (higher = higher risk)

### 🤖 Gemini AI Integration
- Sends structured health summaries to Gemini API
- Preventive healthcare focus (no disease diagnosis)
- Uses "increased risk of" language instead of "has disease"
- 8-section structured response format

### 📄 PDF Report Generation
Generates professional A4-formatted reports including:
- Clinic header with date and report ID
- Patient information
- Comprehensive metrics table
- Risk assessment summary
- AI-generated wellness analysis
- Professional disclaimer

### 📊 Dashboard
- Total active patients count
- Total evaluations count
- High-risk patients tracking
- Recent evaluation activity
- Quick action buttons

## 🏗️ Project Structure

```
body-evolution-pr/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── database_schema.sql      # Supabase schema
├── README.md                # This file
│
└── src/
    ├── auth.py              # Authentication module
    ├── database.py          # Database manager (Supabase)
    ├── patient.py           # Patient CRUD operations
    ├── evaluation.py        # Health evaluation module
    ├── rule_engine.py       # Category conversion logic
    ├── ai_engine.py         # Gemini AI integration
    ├── pdf_generator.py     # PDF report generation
    └── utils.py             # Utility functions
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.10.x or higher
- Supabase account (free tier available at supabase.com)
- Google Gemini API key (get from ai.google.dev)

### 2. Clone & Setup

```bash
# Navigate to project directory
cd "e:\KSS\BODY EVOLUTION PR"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. In Supabase Dashboard:
   - Go to **SQL Editor**
   - Create a new query
   - Copy the entire contents of `database_schema.sql`
   - Paste and run in Supabase SQL Editor
3. Get your credentials:
   - Go to **Project Settings** → **API**
   - Copy `Project URL` and `anon public` key

### 5. Setup Gemini API

1. Go to [ai.google.dev](https://ai.google.dev)
2. Click "Get API Key"
3. Create a new API key and copy it

### 6. Configure Environment Variables

1. Copy `.env.example` to `.env`
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
```

**Note:** The password hash is SHA256 hash of "admin123". To change it:
```bash
python -c "import hashlib; print(hashlib.sha256(b'your_password').hexdigest())"
```

### 7. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📝 Default Credentials

```
Username: admin
Password: admin123
```

⚠️ **Change these in production!**

## 💻 Usage Guide

### Adding a Patient
1. Click **Patient Management** in sidebar
2. Go to **Add Patient** tab
3. Fill in patient details (required fields marked with *)
4. Click **Create Patient**

### Creating an Evaluation
1. Click **Health Evaluation** in sidebar
2. Select a patient
3. Enter all health metrics
4. System validates input ranges
5. Click **Generate Health Report**

### Workflow
1. **Rule Engine** categorizes metrics
2. **Gemini AI** generates analysis
3. **Database** stores results
4. **PDF Generator** creates report

### Viewing Reports
- Download PDF button on evaluation page
- Print using browser print function
- PDF includes full health summary and recommendations

## 🔒 Security Features

- ✅ Password hashing (SHA256)
- ✅ Session-based authentication
- ✅ Supabase RLS (Row Level Security)
- ✅ Input validation on all fields
- ✅ SQL constraints for data integrity
- ✅ Audit logging for all changes
- ✅ Soft delete (no permanent data loss)

## 📊 Database Schema

### Patients Table
- `id`: Primary key (UUID)
- `patient_id`: Human-readable ID (P0001, P0002, etc.)
- `name, age, gender, height`: Demographic data
- `mobile, email`: Contact info (mobile is unique)
- `area, address`: Location info
- `notes`: Additional notes
- `is_active`: Soft delete flag
- `created_at, updated_at`: Timestamps

### Health Records Table
- `id`: Primary key (UUID)
- `patient_id`: Foreign key to patients
- `weight, bmi, bmr`: Basic metrics
- `body_fat, visceral_fat, body_age, tsf, muscle_mass`: Composition
- `wellness_score`: AI-calculated risk score
- `ai_summary`: Gemini API response
- `created_at`: Evaluation timestamp

### Audit Logs Table
- Automatic tracking of all changes
- Maintains history for compliance
- Tracks INSERT, UPDATE, DELETE operations

## 🤖 AI System Instructions

The Gemini AI assistant follows strict guidelines:

```
✅ DOES:
- Provide risk analysis
- Use preventive language
- Recommend lifestyle changes
- Suggest dietary improvements
- Warn about future health risks

❌ DOES NOT:
- Diagnose diseases
- Say "patient has" disease
- Provide medical treatment
- Replace professional medical advice
```

## 📱 API Endpoints Used

### Supabase Integration
- REST API for all CRUD operations
- Real-time subscriptions ready
- Storage for PDF backups (optional)

### Gemini API Integration
- Text generation with system instructions
- Structured prompt engineering
- Response validation

## 🎨 UI/UX Features

- 📱 Responsive design (works on desktop, tablet, mobile)
- 🎨 Professional color scheme
- 📊 Interactive charts and tables
- 🔔 Real-time notifications
- ⚡ Quick action buttons
- 📋 Tabbed navigation

## 🧪 Testing

### Test Data
Sample patients included in `database_schema.sql` (commented out)
Uncomment to populate test data

### Validation Testing
- BMI range: 10–50 ✓
- Body Fat range: 5–60 ✓
- Visceral Fat range: 1–30 ✓
- All validation ranges enforced ✓

## 📦 Dependencies

```
streamlit>=1.40.0           # Web framework (latest stable)
supabase>=2.4.0             # Database client
python-dotenv>=1.0.1        # Environment variables
google-generativeai>=0.7.0  # Gemini API
reportlab>=4.1.0            # PDF generation
pandas>=2.2.0               # Data handling
requests>=2.32.0            # HTTP client
psycopg2-binary>=2.9.0      # PostgreSQL adapter
```

## 🐛 Troubleshooting

### "SUPABASE_URL and SUPABASE_KEY must be set"
- Check `.env` file exists in project root
- Verify credentials are correct
- Restart Streamlit app

### "Gemini API connection failed"
- Verify `GEMINI_API_KEY` in `.env`
- Check API key is valid and hasn't expired
- Ensure billing is enabled for Gemini API

### "Patient with this mobile number already exists"
- Mobile numbers must be unique
- Use different mobile number for new patient

### PDF not generating
- Ensure `reportlab` is installed correctly
- Check patient and health record data is complete
- Verify AI response was generated

## 📈 Performance Optimization

- ✅ Database indexes on frequently queried columns
- ✅ Pagination for large datasets
- ✅ Caching of session data
- ✅ Lazy loading of health records
- ✅ Optimized PDF generation

## 🔄 Backup & Recovery

Supabase provides:
- Daily automated backups
- Point-in-time recovery
- Data export functionality
- Replication for redundancy

## 📞 Support & Maintenance

### Regular Maintenance
1. Monitor database size
2. Archive old evaluations (>1 year)
3. Update dependencies monthly
4. Review audit logs for anomalies

### Deployment
```bash
# On production server
streamlit run app.py --logger.level=error --client.toolbarMode=minimal
```

## 📄 License

This project is provided as-is for healthcare wellness evaluation purposes.

## ⚠️ Medical Disclaimer

**This system is NOT a medical diagnosis tool.**

- Results are for wellness evaluation only
- Not a substitute for professional medical advice
- Always consult healthcare professionals
- Do not use for emergency situations
- Not intended to diagnose, treat, or cure diseases

## 🎯 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Email report delivery
- [ ] Integration with fitness trackers
- [ ] Comparison reports (patient progress over time)
- [ ] Prescription integration
- [ ] Mobile app version
- [ ] Dark mode theme

## 👨‍💻 Developer Notes

### Adding Custom Rules
Edit `rule_engine.py` to add new categorization logic:
```python
@staticmethod
def categorize_custom_metric(value: float) -> str:
    # Add logic here
    pass
```

### Customizing PDF
Edit `pdf_generator.py` to modify report format:
```python
CLINIC_NAME = "Your Clinic Name"
CLINIC_ADDRESS = "Your Address"
```

### Extending AI Capabilities
Modify system instructions in `ai_engine.py`:
```python
SYSTEM_INSTRUCTION = "Your custom instructions here"
```

---

**Built with ❤️ using Streamlit, Supabase, and Google Gemini AI**

Last Updated: 2026-02-24
# KSS-BODY-EVOLUTION
