:: filepath: C:\development\repo\stock_analytics\data\run_yahoo_data.bat
@echo off

REM Navigate to the interactive brokers client portal gateway directory
cd /d C:\development\repo\stock_analytics\clientportal.gw

REM authenticate the user
CALL bin\run.bat root\conf.yaml

REM change to project directory
@REM cd /d C:\development\repo\stock_analytics   

@REM REM Execute the Python script with parameters
@REM python ib\position_analytics.py
@REM REM (Optional) Deactivate virtual environment if activated
@REM REM CALL deactivate