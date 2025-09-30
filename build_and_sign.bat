@echo off
setlocal

echo Compilazione in corso...

REM Percorso completo di PyInstaller (modifica se diverso)
set PYINSTALLER="C:\Percorso\Assoluto\A\pyinstaller.exe"

REM Compila l'eseguibile con icona, info versione e supporto ttk
%PYINSTALLER% --onefile --noconsole --icon=icona.ico --version-file=version.txt --name "DataChecker" --hidden-import=tkinter.ttk data_checker.py

IF NOT EXIST dist\DataChecker.exe (
    echo Errore: EXE non generato.
    pause
    exit /b
)

echo EXE generato: dist\DataChecker.exe

REM Percorso di signtool (modifica se necessario)
set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"

REM Firma con certificato SHA1 (modifica se necessario)
echo Firma digitale in corso...
%SIGNTOOL% sign /sha1 E0A1BB9B9033D65644691DB03111C513DAECD583 /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\DataChecker.exe

IF %ERRORLEVEL% NEQ 0 (
    echo Errore durante la firma.
    pause
    exit /b
)

echo Firma completata con successo.
pause