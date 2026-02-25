# Body Evolution Wellness System - Setup Script
# This script helps you get the system running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Body Evolution Wellness System Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".\.env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your credentials:"
    Write-Host ""
    Write-Host "Steps:" -ForegroundColor Yellow
    Write-Host "1. Go to https://supabase.com and create a project"
    Write-Host "2. Get your Project URL and API Key from Settings → API"
    Write-Host "3. Get a new Gemini API key from https://aistudio.google.com"
    Write-Host "4. Copy .env.example to .env and fill in your credentials"
    Write-Host ""
    exit 1
}

Write-Host "✓ .env file found" -ForegroundColor Green

# Check if venv exists
if (-not (Test-Path ".\venv")) {
    Write-Host "❌ Virtual environment not found! Creating..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "System Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the app:" -ForegroundColor Yellow
Write-Host "streamlit run app.py" -ForegroundColor Green
Write-Host ""
Write-Host "Database Schema Setup:" -ForegroundColor Yellow
Write-Host "1. Go to Supabase SQL Editor" -ForegroundColor Cyan
Write-Host "2. Copy contents of database_schema.sql" -ForegroundColor Cyan
Write-Host "3. Paste and run in SQL Editor" -ForegroundColor Cyan
Write-Host ""
