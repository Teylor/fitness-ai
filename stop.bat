@echo off
echo === Fitness AI - Stopping ===

REM Matar proceso python que corre el MCP server
taskkill /F /FI "WINDOWTITLE eq Fitness AI*" 2>nul

REM Alternativa: buscar por puerto
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":9700" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a 2>nul
)

echo === Fitness AI stopped ===
pause