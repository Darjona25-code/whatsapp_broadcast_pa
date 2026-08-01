@echo off
REM Compila la aplicacion en un ejecutable de Windows con PyInstaller.
REM Requiere tener instalado Python 3.11+ y las dependencias del proyecto.

python -m pip install pyinstaller || goto :error
python -m PyInstaller --noconfirm --onefile --windowed --name WhatsAppBroadcastPA main.py || goto :error

echo.
echo Ejecutable generado en: dist\WhatsAppBroadcastPA.exe
pause
exit /b 0

:error
echo.
echo Fallo al compilar. Revisa que Python y las dependencias esten instaladas.
pause
exit /b 1
