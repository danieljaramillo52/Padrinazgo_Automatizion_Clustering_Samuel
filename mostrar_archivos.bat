@echo off
echo Mostrando archivos ocultos...

attrib -h -s ".vscode" /s /d
attrib -h -s "Scripts" /s /d
attrib -h -s "src" /s /d
attrib -h -s "Controllers" /s /d
attrib -h -s "python-3.12.6-emb.zip" /s /d
attrib -h -s "python-3.12.6-emb" /s /d
attrib -h -s "Utils" /s /d
attrib -h -s ".gitignore"
attrib -h -s "requirements.txt"
attrib -h -s "iniciar.bat"

echo Archivos visibles de nuevo.
pause