@echo off
echo Starting Sea Ping Warfare server...
start cmd /k "npm start"

timeout /t 3 /nobreak > nul

echo.
echo Creating public tunnel with Serveo (no signup required)...
echo.
echo Your public URL will appear below:
echo.
ssh -R 80:localhost:3000 serveo.net