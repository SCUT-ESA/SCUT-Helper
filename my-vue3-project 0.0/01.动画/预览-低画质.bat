@echo off
cd /d "%~dp0"

echo ========================================
echo  LiGong promo - LOW quality preview
echo  ~480p15  fast preview
echo  ligong2.py  -^>  LiGongAssistant
echo ========================================
echo.

python -m manim -pql ligong2.py LiGongAssistant
if errorlevel 1 (
    echo.
    echo [FAILED]
    echo   1. Need python on PATH
    echo   2. Need: python -m pip install manim
    echo   3. Keep this bat next to ligong2.py and assets\
    echo.
    pause
    exit /b 1
)

echo.
echo [DONE] Output usually:
echo   media\videos\ligong2\480p15\LiGongAssistant.mp4
echo.
pause
