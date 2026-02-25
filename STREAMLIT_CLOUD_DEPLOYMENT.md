# Streamlit Cloud Deployment Guide

## How the App Works with Secrets

Your app is **already production-ready** because it uses `os.getenv()` to access APIs:

```python
# This works in BOTH Local & Cloud environments:
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
```

### Local Development
- `.env` file provides the environment variables
- No configuration needed ✅

### Streamlit Cloud
- Streamlit Cloud's **Secrets Manager** provides the environment variables
- No `.env` file needed (and shouldn't exist in repo)

---

## Step-by-Step Deployment

### 1. **Prepare Repository (Already Done ✓)**
```bash
git init
git add .
git commit -m "Ready for Streamlit Cloud"
git push -u origin main
```

### 2. **Deploy to Streamlit Cloud**

Go to **https://share.streamlit.io/**

1. Click **"Create app"**
2. Connect your GitHub repository
   - Repository: `head-prog/KSS-BODY-EVOLUTION`
   - Branch: `main`
   - Main file path: `app.py`

### 3. **Add Secrets in Streamlit Cloud Dashboard**

Once your app is deployed, it will fail initially (missing secrets). Fix it:

1. Go to your app's **Settings** (gear icon)
2. Click **"Secrets"** tab
3. Paste your secret keys in the format below:

```
SUPABASE_URL=https://bnwbsastgrzmubfkpart.supabase.co
SUPABASE_KEY=sb_publishable_1uwBIMRWXO4QwNtyTKtXtQ_vhnd3yVZ
GEMINI_API_KEY=AIzaSyAAAAtJNZjhkg7Fh0RYaydLkKvwYiS_sBs
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
```

4. Click **"Save"** → App automatically restarts with secrets loaded

### 4. **Keep .env for Local Development Only**

In your `.gitignore` (already configured):
```
.env
.env.*
```

Your `.env` file will NOT be pushed to GitHub ✅

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│      Your Local Machine                 │
│  ┌──────────────────────────────────┐  │
│  │ .env (keeps secrets locally)     │  │
│  │ - GEMINI_API_KEY                 │  │
│  │ - SUPABASE_KEY                   │  │
│  │ - ADMIN_PASSWORD_HASH            │  │
│  └──────────────────────────────────┘  │
│                │                        │
│         streamlit run app.py            │
│         (reads from .env)               │
│                │                        │
│        os.getenv("KEY_NAME")            │
│                │                        │
│         ✅ App works locally            │
└─────────────────────────────────────────┘
            ↓ git push ↓
┌─────────────────────────────────────────┐
│    GitHub Repository                    │
│  (NO .env file - it's in .gitignore)    │
│    head-prog/KSS-BODY-EVOLUTION         │
└─────────────────────────────────────────┘
            ↓ automatically ↓
┌─────────────────────────────────────────┐
│   Streamlit Cloud App                   │
│  ┌──────────────────────────────────┐  │
│  │ Secrets Manager (dashboard)      │  │
│  │ - GEMINI_API_KEY                 │  │
│  │ - SUPABASE_KEY                   │  │
│  │ - ADMIN_PASSWORD_HASH            │  │
│  └──────────────────────────────────┘  │
│                │                        │
│        os.getenv("KEY_NAME")            │
│        (reads from Secrets)             │
│                │                        │
│        ✅ App works in cloud            │
└─────────────────────────────────────────┘
```

---

## What's Already Configured ✅

Your codebase already supports cloud deployment:

✅ `app.py` uses `load_dotenv()` for local env  
✅ All modules use `os.getenv()` for API access  
✅ Imports are correct (fixed Google Gemini import)  
✅ `.gitignore` excludes `.env` files  
✅ `.gitignore` excludes `__pycache__` and venv  
✅ `requirements.txt` has all dependencies  

---

## Important: Rotate Your Exposed Keys ⚠️

Your keys were previously exposed. **Please update them immediately:**

1. **SUPABASE_KEY** → Regenerate in Supabase dashboard
2. **GEMINI_API_KEY** → Create new key in Google Cloud console
3. **ADMIN_PASSWORD_HASH** → Generate new hash

Then update the secrets in both:
- Your local `.env` file
- Streamlit Cloud secrets dashboard

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'google.generativeai'"
Likely issue: `requirements.txt` doesn't have library
Fix: Ensure `google-generativeai` is in `requirements.txt`

### "Environmental variable not found (GEMINI_API_KEY)"
Fix: Check Streamlit Cloud Secrets dashboard - secrets are case-sensitive!

### "ImportError: cannot import name 'genai' from 'google'"
✅ Already fixed! We updated the import to `import google.generativeai as genai`

---

## Commands Reference

```bash
# Local development
streamlit run app.py

# View secrets locally (encrypted)
cat ~/.streamlit/secrets.toml

# Check environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

---

## Security Best Practices ✅

| Practice | Your Setup |
|----------|-----------|
| .env not in git | ✅ Yes (in .gitignore) |
| API keys not hardcoded | ✅ Yes (using os.getenv) |
| Secrets in cloud dashboard | ✅ Configure before deploy |
| Rotating compromised keys | ⚠️ TODO - keys are exposed |

---

## Next Steps

1. **Rotate your API keys** (they were exposed)
2. **Go to Streamlit Cloud** and create app
3. **Add secrets** in dashboard
4. **App deploys** automatically
5. **Monitor logs** for any errors

Your app is ready! 🚀
