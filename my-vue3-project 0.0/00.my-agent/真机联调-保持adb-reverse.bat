@echo off
chcp 65001 >nul
title 真机联调 - 保持 adb reverse（可最小化）
cd /d "%~dp0"

where adb >nul 2>&1
if errorlevel 1 (
  echo [错误] 找不到 adb。请把 platform-tools 加到 PATH。
  pause
  exit /b 1
)

echo ========================================
echo   自动保持：手机 8000 ^<-> 电脑 8000
echo   拔线重插后会自动补上 reverse
echo   关闭本窗口即停止监控
echo ========================================
echo.

:loop
adb reverse --list 2>nul | findstr /C:"tcp:8000" >nul
if errorlevel 1 (
  echo [%time%] 未检测到 8000 转发，正在设置...
  adb wait-for-device >nul 2>&1
  adb reverse tcp:8000 tcp:8000 >nul 2>&1
  if errorlevel 1 (
    echo [%time%] 失败：请确认手机已连上且 USB 调试已授权
  ) else (
    echo [%time%] 已设置 adb reverse tcp:8000 tcp:8000
    adb reverse --list
  )
) else (
  rem 已存在则安静等待
)

timeout /t 5 /nobreak >nul
goto loop
