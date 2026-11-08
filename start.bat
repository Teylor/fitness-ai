@echo off
echo === Fitness AI - Starting ===

REM Create folder of data if not exists
if not exist "data" mkdir data

REM Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Start MCP server
echo Starting MCP server on localhost:9700...
python -m src.main

echo === Fitness AI stopped ===
pause
