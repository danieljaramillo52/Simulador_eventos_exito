@echo off
echo ===============================
echo Iniciando el proyecto Python...
echo ===============================

:: Activar el entorno virtual
: :call venv\Scripts\activate

:: Instalar requerimientos (Comentar si ya están instalados)
::echo Instalando requerimientos...
::pip install -r requirements.txt
echo ===============================

:: Ejecutar el script principal
echo Ejecutando el programa...
Streamlit run main.py

:: Esperar para que no se cierre de inmediato
echo.
pause
