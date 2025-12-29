@echo off
REM Meow Blog Development Server Startup Script
REM Handles: Environment check, database migration, server startup

echo Starting Meow Blog Development Server...
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
if not defined EXTERNAL_PORT set EXTERNAL_PORT=8000
if not defined PORT set PORT=8000

REM Check if port is available
echo Checking port %PORT% availability...
netstat -ano | findstr :%PORT% >nul
if %errorlevel% equ 0 (
    echo Port %PORT% is already in use. Attempting to free it...
    
    REM Find and kill processes using port
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
        echo Stopping process PID: %%a
        taskkill /f /pid %%a >nul 2>&1
    )
    
    REM Wait for processes to stop
    timeout /t 2 /nobreak >nul
    
    REM Check again
    netstat -ano | findstr :%PORT% >nul
    if %errorlevel% equ 0 (
        echo Failed to free port %PORT%. Please manually stop the process using this port.
        echo You can use: netstat -ano ^| findstr :%PORT%
        pause
        exit /b 1
    ) else (
        echo Port %PORT% is now available
    )
) else (
    echo Port %PORT% is available
)

REM Check database migrations
echo Checking database migrations...
python manage.py migrate --settings=meowsite.settings_dev --verbosity 0
if %errorlevel% neq 0 (
    echo Database migration failed, but continuing to start server
)

REM Start development server
echo.
echo ==========================================
echo Development Server Started
echo ==========================================
echo.
echo IMPORTANT: Use HTTP, not HTTPS!
echo Local access: http://127.0.0.1:%PORT%
echo External access: http://%EXTERNAL_HOST%:%EXTERNAL_PORT%
echo Admin Panel: http://127.0.0.1:%PORT%/admin
echo.
echo Test users:
echo   Admin: admin / admin123
echo   User: meow / meow123
echo.
echo Press Ctrl+C to stop server
echo.

python manage.py runserver 0.0.0.0:%PORT% --settings=meowsite.settings_dev
pause