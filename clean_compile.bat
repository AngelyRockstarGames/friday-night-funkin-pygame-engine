@echo off
title Limpiando archivos de compilación
echo ===============================
echo  Limpiando archivos temporales...
echo ===============================

:: Eliminar carpetas de compilación
if exist "build" (
    echo Eliminando carpeta build...
    rmdir /s /q "build"
)

if exist "dist" (
    echo Eliminando carpeta dist...
    rmdir /s /q "dist"
)

:: Eliminar archivos temporales
if exist "__pycache__" (
    echo Eliminando __pycache__...
    rmdir /s /q "__pycache__"
)

if exist "scripts\__pycache__" (
    echo Eliminando scripts\__pycache__...
    rmdir /s /q "scripts\__pycache__"
)

:: Eliminar archivos .spec y .log
if exist "FNF_Prototype.spec" (
    echo Eliminando FNF_Prototype.spec...
    del "FNF_Prototype.spec"
)

if exist "*.log" (
    echo Eliminando archivos .log...
    del "*.log"
)

echo.
echo ===============================
echo  ¡Limpieza completada!
echo ===============================

pause