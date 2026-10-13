@echo off
cd /d "%~dp0"
title Formulario de visita as Ovitrampas
set "PY="
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY if exist "..\.venv\Scripts\python.exe" set "PY=..\.venv\Scripts\python.exe"
if not defined PY set "PY=python"

echo Iniciando o formulario... Feche esta janela para encerrar o servidor.
"%PY%" iniciar.py
if errorlevel 1 (
  echo.
  echo Ocorreu um erro. Leia a mensagem acima.
  pause
)
