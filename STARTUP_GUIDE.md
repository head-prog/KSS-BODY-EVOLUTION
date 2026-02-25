# 🚀 QUICK START GUIDE - Body Evolution Wellness System

## ✅ Current Status
- ✓ Virtual Environment: Created
- ✓ Dependencies: Installed (Streamlit 1.54.0, Pandas 2.3.3, etc.)
- ✓ Project Files: All present
- ✓ AI Model: gemini-2.5-pro configured

## 📋 SETUP CHECKLIST (Complete Before Running)

### Step 1: Get Supabase Credentials ⚙️
1. Go to [supabase.com](https://supabase.com)
2. Create/sign into your account
3. Create a new project
4. Go to **Settings → API** and copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (starts with `eyJ...`)

### Step 2: Get Gemini API Key 🔑
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key**
3. Create a new API key
4. Copy the key (it starts with `AIza...`)

### Step 3: Update `.env` File 📝
Edit `.env` file in the project root:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-api-key-here
GEMINI_API_KEY=your-new-gemini-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
```

### Step 4: Create Database Schema in Supabase 🗄️
1. Open your Supabase project dashboard
2. Go to **SQL Editor**
3. Click **New Query**
4. Copy the ENTIRE contents of `database_schema.sql` 
5. Paste into SQL Editor
6. Click **Run**
7. Wait for tables to be created ✓

## 🎯 RUN THE APPLICATION

### Option A: Using Batch File (Windows)
```bash
Double-click: run_app.bat
```

### Option B: Using PowerShell
```powershell
cd "e:\KSS\BODY EVOLUTION PR"
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

### Option C: Using Command Prompt
```cmd
cd e:\KSS\BODY EVOLUTION PR
venv\Scripts\activate.bat
streamlit run app.py
```

## 📺 AFTER APP STARTS
- A new browser window will open automatically
- Default login: `admin` / `admin123`
- The app will be available at: `http://localhost:8501`

## 🔑 Admin Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

⚠️ Change these in production!

## 🛑 TROUBLESHOOTING

### Issue: "GEMINI_API_KEY not set"
**Solution:** Make sure you've updated `.env` with your actual API key

### Issue: "Cannot connect to Supabase"
**Solution:** 
1. Verify SUPABASE_URL and SUPABASE_KEY are correct
2. Check your Supabase project is active
3. Ensure database schema has been created

### Issue: "Module not found"
**Solution:** Make sure you're in the project directory when running the app

### Issue: Port 8501 already in use
**Solution:** Run with different port:
```bash
streamlit run app.py --server.port 8502
```

## 📞 SUPPORT
- Check the README.md for detailed documentation
- Review TESTING_DEPLOYMENT.md for deployment options
- API_DOCUMENTATION.md for module details

---
**Last Updated:** February 24, 2026
**Version:** 1.0.0
**Status:** Ready for Production
