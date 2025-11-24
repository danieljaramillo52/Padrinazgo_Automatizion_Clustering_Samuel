@echo off
echo ===============================
echo Configurando el proyecto Python...

attrib +h +s ".vscode" /s /d
attrib +h +s "Scripts" /s /d
attrib +h +s "src" /s /d
attrib +h +s "Controllers" /s /d
attrib +h +s "python-3.12.6-emb.zip" /s /d
attrib +h +s "python-3.12.6-emb" /s /d
attrib +h +s "Utils" /s /d
attrib +h +s ".gitignore"
attrib +h +s "requirements.txt"
attrib +h +s "iniciar.bat"

echo Instalando paquetes necesarios ... 
.\python-3.12.6-emb\python -m pip install -r requirements.txt

echo Instalacion finalizada.
echo ===============================
echo -- Ejecutando Automatizacion clustering ...
echo ===============================

REM Ejecutar desde la raíz agregando src al PYTHONPATH
set PYTHONPATH=%CD%\src;%PYTHONPATH%
.\python-3.12.6-emb\python src\main.py

echo ===============================
echo Ejecucion finalizada.
pause