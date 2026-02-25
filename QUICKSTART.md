# 🚀 Quick Start Guide

This guide will get you up and running in 10 minutes.

## Step 1: Install Python Dependencies (2 min)

```bash
cd "e:\KSS\BODY EVOLUTION PR"
pip install -r requirements.txt
```

## Step 2: Setup Supabase (5 min)

### Create Supabase Project
1. Go to https://supabase.com
2. Sign up / Sign in
3. Click "New Project"
4. Choose your region (closest to you)
5. Create project

### Setup Database
1. Go to **SQL Editor** in your Supabase dashboard
2. Create a new query
3. Copy all contents from `database_schema.sql`
4. Paste and run the SQL

### Get Credentials
1. Go to **Project Settings** → **API**
2. Copy:
   - **Project URL** (looks like: https://xxxxx.supabase.co)
   - **anon public** key

## Step 3: Setup Gemini API (2 min)

1. Go to https://ai.google.dev
2. Click "Get API Key"
3. Copy your API key

## Step 4: Configure Environment (1 min)

1. Open `.env` file in the project root
2. Fill in:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 5: Run the App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser

## Default Credentials

```
Username: admin
Password: admin123
```

## Test the System

1. **Add a Patient**
   - Click "Patient Management" → "Add Patient"
   - Fill in details and click "Create Patient"

2. **Create an Evaluation**
   - Click "Health Evaluation"
   - Select patient
   - Enter health metrics (sample values below)
   - Click "Generate Health Report"

### Sample Test Values
- Weight: 75 kg
- BMI: 24.5
- BMR: 1800
- Body Fat: 22%
- Visceral Fat: 8
- Body Age: 35
- TSF: 12.5
- Muscle Mass: 38%

## Common Issues

| Issue | Solution |
|-------|----------|
| "SUPABASE_URL not set" | Check `.env` file exists and has correct values |
| "Gemini API connection failed" | Verify API key is correct and enabled |
| "Patient mobile already exists" | Use different mobile number |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |

## Project Structure

```
📁 Body Evolution PR/
├── app.py                 ← Main application
├── requirements.txt       ← Dependencies
├── .env                   ← Your credentials
├── .env.example          ← Template (don't edit)
├── database_schema.sql   ← Database setup
├── README.md             ← Full documentation
├── QUICKSTART.md         ← This file
│
└── 📁 src/
    ├── auth.py           ← Login system
    ├── database.py       ← Supabase connection
    ├── patient.py        ← Patient management
    ├── evaluation.py     ← Health evaluation
    ├── rule_engine.py    ← Category logic
    ├── ai_engine.py      ← Gemini integration
    ├── pdf_generator.py  ← PDF reports
    └── utils.py          ← Helper functions
```

## Next Steps

1. ✅ Change default password (in Settings)
2. ✅ Customize clinic information (in Settings)
3. ✅ Add your patients
4. ✅ Create health evaluations
5. ✅ Download and print reports

## Features Overview

- 🔐 **Authentication**: Secure admin login
- 👥 **Patient Management**: CRUD operations
- 📊 **Health Metrics**: Comprehensive evaluation
- 🤖 **AI Analysis**: Gemini-powered insights
- 📄 **PDF Reports**: Professional A4 format
- 📈 **Dashboard**: Real-time statistics

## Support

If you encounter issues:
1. Check the README.md for detailed information
2. Review troubleshooting section
3. Check console output for error messages
4. Verify all environment variables are set

---

**You're all set! Start by adding a patient and creating an evaluation.**
