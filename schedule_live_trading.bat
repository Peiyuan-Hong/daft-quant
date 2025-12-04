@echo off
REM ============================================
REM Scheduled RSI Live Trading for 510050.SH
REM Run at 9:25 AM before market opens
REM ============================================

echo [%date% %time%] Starting RSI Live Trading Script...

REM Change to the project directory
cd /d "C:\Users\Rui Ma\Desktop\real quant"

REM Activate conda/virtual environment if needed
REM Uncomment and modify if you use a virtual environment:
REM call conda activate your_env_name
REM call "C:\path\to\venv\Scripts\activate.bat"

REM Run the Python script
python run_rsi_live_510050.py

echo [%date% %time%] Script finished.
pause
