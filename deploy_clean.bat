@echo off
REM Meow Blog Deployment Script
REM Only handles: Python environment, database migration, static files

echo Meow Blog Deployment Script
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found, please install Python 3.8+
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Detected existing virtual environment, skipping creation...
) else (
    echo Creating Python virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Virtual environment creation failed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Virtual environment activation failed
    pause
    exit /b 1
)

REM Update pip and install dependencies
echo Checking project dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Dependency installation failed
    pause
    exit /b 1
)

REM Check environment variable file
if not exist ".env" (
    echo Detected missing environment variable file, creating default configuration...
    if exist "env.production.example" (
        copy "env.production.example" ".env" >nul
        echo Created .env file, please edit security key configuration
        echo Important: Please modify SECRET_KEY in .env file!
    ) else (
        echo env.production.example template file not found
    )
)

REM Run database migrations
echo Running database migrations...
python manage.py migrate --settings=meowsite.settings_production --verbosity 1
if %errorlevel% neq 0 (
    echo Database migration failed
    pause
    exit /b 1
) else (
    echo Database migration completed
)

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput --settings=meowsite.settings_production --verbosity 0
if %errorlevel% neq 0 (
    echo Static file collection failed (may already be collected)
) else (
    echo Static file collection completed
)

REM Create superuser
echo Checking superuser...
python create_admin.py > temp_check.txt 2>nul
set /p USER_STATUS=<temp_check.txt
del temp_check.txt >nul 2>&1

if "%USER_STATUS%"=="CREATE" (
    echo Created default superuser: admin / admin123
    echo Please login to admin panel and change password immediately!
) else (
    echo Superuser already exists, skipping creation
)

echo.
echo =====================================
echo Deployment completed!
echo =====================================
echo.
echo Next steps:
echo   Development: start_dev_clean.bat
echo   Production:  start_production_clean.bat
echo.
pause