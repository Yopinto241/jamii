@echo off
REM Quick Start Script for Jamii Connect (Windows)
REM Run this to start services in separate windows

echo.
echo ==========================================
echo Jamii Connect - Quick Start (Windows)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm not found. Please install Node.js 16+
    pause
    exit /b 1
)

echo Checking database connections...
echo.

REM Check PostgreSQL
echo Checking PostgreSQL (localhost:5432)...
python -c "import psycopg2; psycopg2.connect(host='localhost', port=5432, database='huduma_connect', user='postgres', password='3698')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot connect to PostgreSQL
    echo Make sure PostgreSQL is running with correct credentials:
    echo   Host: localhost
    echo   Port: 5432
    echo   Database: huduma_connect
    echo   User: postgres
    echo   Password: 3698
    pause
    exit /b 1
)
echo [OK] PostgreSQL connected
echo.

REM Start Backend
echo Starting Backend...
start "Jamii Backend - FastAPI" cmd /k "cd app && python -m uvicorn main:app --reload"
timeout /t 2 /nobreak >nul

REM Start Frontend
echo Starting Frontend...
start "Jamii Dashboard - React" cmd /k "cd admin-dashboard && npm run dev"

REM Start tests monitor (optional)
echo.
echo ==========================================
echo Services Started!
echo ==========================================
echo.
echo Backend:  http://localhost:8000
echo Dashboard: http://localhost:5173
echo API Docs:  http://localhost:8000/docs
echo.
echo To run tests:
echo   1. Open new terminal
echo   2. Run: python test_validation.py
echo   3. Run: python test_admin_integration.py
echo.
echo Press any key to exit (this will close services)...
pause >nul

taskkill /FI "WINDOWTITLE eq Jamii Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Jamii Dashboard*" /T /F >nul 2>&1
echo Services stopped.
