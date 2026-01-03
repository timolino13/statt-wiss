@echo off
echo checking for uv...
echo =================================

:: Prüfen, ob uv installiert ist
winget list uv 
if %ERRORLEVEL% neq 0 (
    echo =================================
    echo installing uv...
    winget install --id=astral-sh.uv -e
)

:: Skript mit uv ausführen
echo =================================
echo starting speedtest application...
uv run ./src/main.py