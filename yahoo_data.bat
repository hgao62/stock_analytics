:: filepath: C:\development\repo\stock_analytics\data\run_yahoo_data.bat
@echo off

REM Navigate to the script directory
cd /d C:\development\repo\stock_analytics

REM (Optional) Activate virtual environment if used
CALL C:\development\repo\stock_analytics\venv\Scripts\activate.bat

REM Execute the Python script with parameters
python data\yahoo_data.py --mode rerun --recipient hgao62@uwo.ca

REM (Optional) Deactivate virtual environment if activated
REM CALL deactivate