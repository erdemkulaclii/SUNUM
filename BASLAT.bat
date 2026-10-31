@echo off
REM Cift tiklayin: sunum tam ekran acilir ve kendiliginden oynar. Kapatmak icin bu pencerede Ctrl+C.
cd /d "%~dp0"
where py >nul 2>nul && (py -3 sunum.py %*) || (python sunum.py %*)
if errorlevel 1 pause
