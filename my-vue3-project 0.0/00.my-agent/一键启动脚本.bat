@echo off
chcp 65001 >nul
title SCUT Assistant Launcher
echo ====================================
echo   Starting SCUT Campus Assistant...
echo ====================================

cd /d "%~dp0"

echo [1/4] Starting backend server...
start "Backend" cmd /k "cd /d "%~dp0" && venv\Scripts\activate && uvicorn app:app --reload --host 0.0.0.0 --port 8000"

timeout /t 2 /nobreak >nul

echo [2/4] Starting frontend server...
start "Frontend" cmd /k "cd /d "%~dp0" && python -m http.server 8080"

timeout /t 1 /nobreak >nul

echo [3/4] Opening browser...
start http://127.0.0.1:8080/frontend/index.html

echo [4/4] 尝试 adb reverse（真机 App 联调）...
where adb >nul 2>&1
if errorlevel 1 (
  echo     未找到 adb，跳过。需要时请双击「真机联调-adb-reverse.bat」
) else (
  adb reverse tcp:8000 tcp:8000 >nul 2>&1
  if errorlevel 1 (
    echo     当前无已授权手机，跳过。插上手机后请双击「真机联调-adb-reverse.bat」
    echo     或运行「真机联调-保持adb-reverse.bat」自动保持转发
  ) else (
    echo     已设置 adb reverse tcp:8000 tcp:8000
    adb reverse --list
  )
)

echo ====================================
echo   All services started!
echo   Backend:  http://0.0.0.0:8000  (本机/局域网均可访问)
echo   Frontend: http://127.0.0.1:8080/frontend/index.html
echo   真机 App: 先 USB 调试，再保证 reverse 8000（见上方脚本）
echo   Close the two cmd windows to stop.
echo ====================================
pause
