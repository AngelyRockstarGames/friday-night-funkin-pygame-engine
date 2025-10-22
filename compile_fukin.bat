@echo off
chcp 65001
title funkin 

echo ========================================
echo    COMPILE DEBUG MODE
echo ========================================
echo.

if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo Compilando en modo debug...
pyinstaller --noconfirm --onefile --console ^
  --name "FridayNightFukin_Debug" ^
  --icon "fukin.ico" ^
  --add-data "assets;assets" ^
  --add-data "audio;audio" ^
  --add-data "config;config" ^
  --add-data "data;data" ^
  --add-data "scripts;scripts" ^
  --add-data "scripts_week;scripts_week" ^
  --hidden-import "pygame" ^
  --hidden-import "json" ^
  --hidden-import "os" ^
  --hidden-import "sys" ^
  --hidden-import "psutil" ^
  --hidden-import "email" ^
  --hidden-import "email.mime" ^
  --hidden-import "email.mime.text" ^
  --hidden-import "email.mime.multipart" ^
  --hidden-import "pkg_resources" ^
  main.py

echo.
echo ========================================
echo    COMPILACION DEBUG COMPLETADA
echo ========================================
echo.
echo Ejecutable creado en: dist\FridayNightFukin_Debug.exe
echo Este abrirá una consola para ver errores.
echo.
pause