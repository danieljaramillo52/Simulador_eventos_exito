@echo off
echo ===============================
echo Configurando el proyecto Python...

attrib -h -s "__pycache__" /s /d
attrib -h -s ".vscode" /s /d
attrib -h -s "static" /s /d
attrib -h -s "Controllers" /s /d
attrib -h -s "venv" /s /d
attrib -h -s "ui_components" /s /d
attrib -h -s ".gitignore"
attrib -h -s ".git"
attrib -h -s "README.md" 
attrib -h -s "services" /s /d
attrib -h -s "Img" /s /d
attrib -h -s "requirements.txt"
attrib -h -s "main.py"
attrib -h -s "iniciar.bat"
:: Acti-ar el entorno virtual
::call venv\Scripts\activate

:: Instalar requerimientos (Comentar si ya están instalados)
echo Instalando requerimientos...
pip install -r requirements.txt
echo ===============================


echo Instalacion terminada...
echo ===============================
:: Esperar para que no se cierre de inmediato
echo.
pause



