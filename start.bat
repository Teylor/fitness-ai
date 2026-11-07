@echo off
echo === Fitness AI - Starting ===

REM Crear carpeta de datos si no existe
if not exist "data" mkdir data

REM Iniciar MCP server
echo Starting MCP server on localhost:9700...
python -m src.main

echo === Fitness AI stopped ===
pause