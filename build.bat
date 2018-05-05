@echo off
"C:\Python27\Scripts\pyinstaller.exe" simple-service.spec
if ERRORLEVEL 1 GOTO EndErr
"C:\Program Files (x86)\nsis\makensis.exe" simple-service.nsi
if ERRORLEVEL 1 GOTO EndErr
:End
Exit
:EndErr
Exit /b 1
