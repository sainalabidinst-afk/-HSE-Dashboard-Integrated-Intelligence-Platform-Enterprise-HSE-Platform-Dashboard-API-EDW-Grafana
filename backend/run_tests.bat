@echo off
REM Test Runner Script for Windows
REM Runs the full test suite with coverage reporting

echo ============================================
echo HSE Enterprise Platform - Test Suite
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Running tests with coverage...
echo.

REM Run pytest with coverage
pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term --junitxml=test-results.xml

echo.
echo ============================================
echo Test Results
echo ============================================
echo.
echo Coverage report generated: htmlcov/index.html
echo Test results: test-results.xml
echo.

pause
