@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem 固定使用项目独立环境，避免受其它项目的 Python 变动影响
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m app.main
) else (
    py -m app.main
    pause
)
