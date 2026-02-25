# Streamlit Cloud Deployment Guide

## ⚠️ Security Requirements (COMPLETE BEFORE DEPLOYMENT)

### 1. Rotate ALL Exposed Credentials
Your API keys and credentials were exposed in the git history. **IMMEDIATELY:**
- [ ] Regenerate your SUPABASE_KEY at https://app.supabase.co/project/[your-project]/settings/api
- [ ] Regenerate your GEMINI_API_KEY at https://aistudio.google.com/apikey
- [ ] Update your ADMIN_PASSWORD_HASH with a new secure password

### 2. Verify .env File is Ignored
- [ ] Check `.gitignore` includes `.env` and `.env.*`
- [ ] Run `git rm --cached .env` to remove from git history (if needed)
- [ ] Verify no credentials appear in git log:
  ```bash
  git log --all -p | grep -i "API_KEY\|SUPABASE_KEY"
  ```

## 🚀 Deployment Steps

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Production-ready build"
git push origin main
```

### Step 2: Create Streamlit Cloud Account & App
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `head-prog/KSS-BODY-EVOLUTION`
5. Select branch: `main`
6. Set main file path: `app.py`
7. Click "Deploy"

### Step 3: Configure Secrets in Streamlit Cloud
1. Once app is deployed, click ⚙️ → "Settings"
2. Go to **Secrets** section
3. Paste your secrets in TOML format:
```toml
SUPABASE_URL = "https://bnwbsastgrzmubfkpart.supabase.co"
SUPABASE_KEY = "your_actual_key_here"
GEMINI_API_KEY = "your_actual_key_here"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "your_hash_here"
```
4. Click "Save"
5. App will automatically redeploy with secrets

## 🔧 Local Development Setup

### Option A: Using .streamlit/secrets.toml (Recommended)
1. Create `.streamlit/secrets.toml` in your workspace (don't commit):
```toml
SUPABASE_URL = "https://..."
SUPABASE_KEY = "..."
GEMINI_API_KEY = "..."
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "..."
```
2. Run locally:
```bash
cd "e:\KSS\BODY EVOLUTION PR"
venv/Scripts/python.exe -m streamlit run app.py
```

### Option B: Using .env (Local Testing Only)
1. Create `.env` file (ensure it's in `.gitignore`)
2. Set variables same as above
3. App will auto-load via `load_dotenv()` in development

⚠️ **IMPORTANT**: `.env` files are **NOT** supported on Streamlit Cloud. All secrets must go to the Streamlit Cloud web UI.

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] All imports fixed (checked ai_engine.py)
- [ ] No hardcoded API keys in source code
- [ ] No `print()` debug statements left in production code
- [ ] Error handling in place for missing secrets
- [ ] Requirements.txt has all dependencies

### Security
- [ ] All credentials rotated
- [ ] .gitignore blocks .env files
- [ ] No secrets in git history
- [ ] Streamlit Cloud secrets configured

### Functionality
- [ ] Local testing: `streamlit run app.py`
- [ ] Test login with admin credentials
- [ ] Test AI analysis (requires GEMINI_API_KEY)
- [ ] Test database connection (requires SUPABASE keys)
- [ ] Test PDF generation

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set" Error
- Verify secrets in Streamlit Cloud UI (Settings → Secrets)
- Check TOML formatting (no quotes needed for string values)
- Restart the app after saving secrets

### "SUPABASE_URL and SUPABASE_KEY must be set" Error
- Same as above, check Streamlit Cloud secrets configuration

### Import Errors on Deployment
- Delete `.git/objects/pack/` files if git was corrupted
- Ensure `requirements.txt` lists all dependencies
- Check Python version is 3.9+ (Streamlit Cloud uses 3.13)

### "Module not found" for pdf_generator, evaluation, etc.
- Ensure all files exist in `src/` directory
- Check imports use relative paths correctly
- Verify `sys.path.insert(0, str(Path(__file__).parent / "src"))` in app.py

## 📚 References

- [Streamlit Cloud Documentation](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/deploy/streamlit-cloud/manage-your-app/secrets-management)
- [Environment Variables Best Practices](https://docs.streamlit.io/library/advanced-features/configuration)

---

**Last Updated**: February 25, 2026
**Status**: Production Ready ✅
