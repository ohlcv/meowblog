@echo off
REM Meow Blog Production Server Startup Script
REM Handles: Environment check, database migration, static files, server startup

echo Starting Meow Blog Production Server...
echo ==========================================

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, please run deploy_clean.bat first
    pause
    exit /b 1
)

REM Check environment variable file
if not exist ".env" (
    echo Warning: .env file not found, using default configuration
    echo Tip: Create .env file for production environment parameters
)

REM Check if port 8000 is available
echo Checking port 8000 availability...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo Port 8000 is already in use. Attempting to free it...
    
    REM Find and kill processes using port 8000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo Stopping process PID: %%a
        taskkill /f /pid %%a >nul 2>&1
    )
    
    REM Wait for processes to stop
    timeout /t 3 /nobreak >nul
    
    REM Check again
    netstat -ano | findstr :8000 >nul
    if %errorlevel% equ 0 (
        echo Failed to free port 8000. Please manually stop the process using this port.
        echo You can use: netstat -ano ^| findstr :8000
        echo You can use: taskkill /PID [PID] /F
        pause
        exit /b 1
    ) else (
        echo Port 8000 is now available
    )
) else (
    echo Port 8000 is available
)

REM Check database migrations
echo Checking database migrations...
python manage.py migrate --settings=meowsite.settings_production --verbosity 0
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
    echo Static file collection failed, but continuing to start server
) else (
    echo Static file collection completed
)

REM Detect operating system and choose compatible server
echo Detecting system compatibility...
if "%OS%"=="Windows_NT" goto :windows_system
goto :unix_system

:windows_system
echo Windows system detected
echo Checking for Waitress (Windows-compatible WSGI server)...
python -c "import waitress" 2>nul
if %errorlevel% equ 0 (
    echo Waitress found - using Waitress server
    set SERVER_TYPE=waitress
    set SERVER_CMD=waitress-serve --host=0.0.0.0 --port=8000 meowsite.wsgi:application
    goto :server_selected
) else (
    echo Waitress not found - falling back to Django development server
    echo WARNING: This is not recommended for production!
    set SERVER_TYPE=django
    set SERVER_CMD=python manage.py runserver 0.0.0.0:8000 --settings=meowsite.settings_production
    goto :server_selected
)

:unix_system
echo Unix/Linux system detected
echo Checking for Gunicorn (Unix-compatible WSGI server)...
python -c "import gunicorn" 2>nul
if %errorlevel% equ 0 (
    echo Gunicorn found - using Gunicorn server
    set SERVER_TYPE=gunicorn
    set SERVER_CMD=gunicorn -c gunicorn.conf.py meowsite.wsgi:application
    goto :server_selected
) else (
    echo Gunicorn not found - falling back to Django development server
    echo WARNING: This is not recommended for production!
    set SERVER_TYPE=django
    set SERVER_CMD=python manage.py runserver 0.0.0.0:8000 --settings=meowsite.settings_production
    goto :server_selected
)

:server_selected

REM Load environment variables from .env file if it exists
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Set default values if environment variables are not set
if not defined EXTERNAL_HOST set EXTERNAL_HOST=101.32.161.229
if not defined EXTERNAL_PORT set EXTERNAL_PORT=80
if not defined PORT set PORT=8000

echo.
echo ==========================================
echo Production Server Started
echo ==========================================
echo.
echo Server type: %SERVER_TYPE%
echo Local access: http://127.0.0.1:%PORT%
echo External access: http://%EXTERNAL_HOST%:%EXTERNAL_PORT% (via nginx)
echo Admin Panel: http://%EXTERNAL_HOST%:%EXTERNAL_PORT%/admin (via nginx)
echo.
echo Important notes:
echo - Production environment uses HTTPS (via nginx)
echo - Static files are served by nginx
echo - Log files location: logs/
if "%SERVER_TYPE%"=="django" (
    echo - WARNING: Using development server - not recommended for production!
)
echo.
echo Press Ctrl+C to stop server
echo.

REM Start the selected server
%SERVER_CMD%
pause