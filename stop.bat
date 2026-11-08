@echo off
echo === Fitness AI - Stopping ===

REM Kill process python that runs the MCP server
taskkill /F /FI "WINDOWTITLE eq Fitness AI*" 2>nul

REM Alternative: search by port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":9700" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a 2>nul
)

echo === Fitness AI stopped ===
pause