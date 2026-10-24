@echo off
setlocal
chcp 65001 >nul
title So tay dat dai Ninh Binh

pushd "%~dp0"
if errorlevel 1 (
  echo Khong mo duoc thu muc du an.
  pause
  exit /b 1
)

where node.exe >nul 2>&1
if errorlevel 1 goto missing_node
where npm.cmd >nul 2>&1
if errorlevel 1 goto missing_node

if not exist "node_modules\@11ty\eleventy\cmd.cjs" (
  echo Dang cai cac goi can thiet cho lan chay dau...
  call npm.cmd ci --no-fund --no-audit
  if errorlevel 1 goto install_failed
)

node.exe "scripts\start-server.mjs" %*
set "siteRunExitCode=%errorlevel%"
popd
if not "%siteRunExitCode%"=="0" pause
exit /b %siteRunExitCode%

:missing_node
echo Can cai Node.js 20 tro len, kem npm, roi mo lai run.bat.
popd
pause
exit /b 1

:install_failed
echo Cai goi chua thanh cong. Hay kiem tra ket noi Internet va thu lai.
popd
pause
exit /b 1
