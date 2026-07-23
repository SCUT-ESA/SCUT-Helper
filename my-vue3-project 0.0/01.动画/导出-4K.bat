@echo off
cd /d "%~dp0"

echo ========================================
echo  LiGong promo - 4K export
echo  2160p60  SLOW render, leave window open
echo  ligong2.py  -^>  LiGongAssistant
echo ========================================
echo.

python -m manim -pqk ligong2.py LiGongAssistant
if errorlevel 1 (
    echo.
    echo [FAILED]
    echo   1. Need python on PATH
    echo   2. Need: python -m pip install manim
    echo   3. Need enough disk space for 4K
    echo   4. Keep this bat next to ligong2.py and assets\
    echo.
    pause
    exit /b 1
)

echo.
echo [DONE] Output usually:
echo   media\videos\ligong2\2160p60\LiGongAssistant.mp4
echo.
pause
