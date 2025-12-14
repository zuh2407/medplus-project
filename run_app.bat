@echo off
echo Starting Pharmacy App Services...

:: Start FastAPI in a new window
start "FastAPI Backend" cmd /k "python -m uvicorn chatbot_api.app.main:app --host 127.0.0.1 --port 8001 --reload"

:: Start Django in this window (or new one)
echo Waiting for backend...
timeout /t 3

echo Starting Django Server...
python manage.py runserver 0.0.0.0:8000
