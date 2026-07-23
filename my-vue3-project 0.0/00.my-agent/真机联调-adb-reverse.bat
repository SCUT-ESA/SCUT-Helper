@echo off
chcp 65001 >nul
title 真机联调 - adb reverse 8000
cd /d "%~dp0"

where adb >nul 2>&1
if errorlevel 1 (
  echo [错误] 找不到 adb。请把 platform-tools 加到 PATH，或先打开 Android SDK / 手机助手。
  pause
  exit /b 1
)

echo ========================================
echo   真机联调：把手机 127.0.0.1:8000
echo   转到电脑后端 :8000
echo ========================================
echo.

echo [1] 当前设备：
adb devices
echo.

echo [2] 等待手机出现在 device 列表（请开 USB 调试并允许本电脑）...
adb wait-for-device
echo     已检测到设备。
echo.

echo [3] 设置端口转发...
adb reverse tcp:8000 tcp:8000
if errorlevel 1 (
  echo [失败] reverse 未成功。请检查 USB 调试是否授权。
  pause
  exit /b 1
)

echo.
echo [4] 当前 reverse 列表：
adb reverse --list
echo.
echo ========================================
echo   完成。现在可用 App 连 http://127.0.0.1:8000
echo   拔线/重插后若又连不上，再双击本脚本，
echo   或运行「真机联调-保持adb-reverse.bat」自动盯着。
echo ========================================
pause
