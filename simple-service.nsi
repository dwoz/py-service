; XXX: Use a similar command to pull the version from one of the python scripts
; or the debian changelog
!system 'echo|set /p="!define VERSION " > version.include'
!system 'python.exe ./simple-service.py --version >> version.include'
!include version.include
OutFile "simple-service-installer-${VERSION}.exe"
Name "Simple Service - Version ${VERSION}"
InstallDir $PROGRAMFILES\SimpleService
RequestExecutionLevel user

Section

    UserInfo::getAccountType
    Pop $0
    StrCmp $0 "Admin" +3
    MessageBox MB_OK "You must have administrative rights to install the service: $0"
    Return

SectionEnd

Section

    SetOutPath $INSTDIR
    File dist\simple-service.exe
    File ..\simple-service.ini
    SimpleSC::InstallService "SimpleService" "Simple Service" "16" "2" "$INSTDIR\simple-service.exe" "" "LocalSystem" ""
    SimpleSC::SetServiceDescription "Simple Service" "Simple Service Manager"
    SimpleSC::StartService "SimpleService" "" 30

    WriteUninstaller "$INSTDIR\uninstall.exe"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimpleService" \
                 "DisplayName" "Simple Service"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimpleService" \
                 "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimpleService" \
                 "Publisher" "dwoz"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimpleService" \
                 "DisplayVersion" "${VERSION}"

SectionEnd

Section "uninstall"

    SimpleSC::StopService "SimpleService" "" 30
    SimpleSC::RemoveService "SimpleService"
    Delete "$INSTDIR\simple-service.exe"
    Delete "$INSTDIR\simple-service.ini"
    Delete "$INSTDIR\uninstall.exe"
    RMDir "$INSTDIR"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimpleService"

SectionEnd

