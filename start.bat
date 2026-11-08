@echo off
echo === Fitness AI - Starting ===

REM Create folder of data if not exists
if not exist "data" mkdir data

REM Start MCP server
echo Starting MCP server on localhost:9700...
python -m src.main

echo === Fitness AI stopped ===
pause