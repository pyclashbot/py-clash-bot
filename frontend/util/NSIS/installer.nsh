!addplugindir "plugins"

!macro InstallAHK
    ; download the AHK installer from the https://www.autohotkey.com/download/ahk-install.exe, saving to install dir
    inetc::get /CAPTION "Downloading AutoHotKey Installer" \
    "https://www.autohotkey.com/download/ahk-install.exe" \
    "$INSTDIR\ahk-install.exe" /END
    ; run the AHK installer
    ExecWait "$INSTDIR\ahk-install.exe" $0
    IfErrors +1 +3
        MessageBox MB_OK "AHK installation failed. Aborting!"
        Abort
    ; delete the AHK installer
    Delete "$INSTDIR\ahk-install.exe"
!macroend


!macro CheckForAHK
    ; read windows registry for AHK install dir at HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AutoHotKey\DisplayIcon
    ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AutoHotKey" "DisplayIcon"
    ; if AHK isnt installed, prompt user to install it
    IfErrors +1 +3
        MessageBox MB_OK "AutoHotKey is not installed. Press OK to install now..."
        !insertmacro InstallAHK
!macroend


!macro InstallMemu
    inetc::get /CAPTION "Downloading MEmu Installer" \
    "https://dl.memuplay.com/download/MEmu-setup-abroad-sdk.exe" \
    "$INSTDIR\MEmu-setup-abroad-sdk.exe" /END
    ExecWait "$INSTDIR\MEmu-setup-abroad-sdk.exe" $0
    IfErrors +1 +3
        MessageBox MB_OK "MEmu installation failed. Aborting!"
        Abort
    Delete "$INSTDIR\MEmu-setup-abroad-sdk.exe"
!macroend


!macro CheckForMemu
    ReadRegStr $R0 HKLM "SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MEmu" "InstallLocation"
    ; if MEmu isnt installed, prompt user to install it
    IfErrors +1 +3
        MessageBox MB_OK "MEmu is not installed. Press OK to install now..."
        !insertmacro InstallMemu
!macroend


!macro CheckForDependencies
    !insertmacro CheckForAHK
    !insertmacro CheckForMemu
!macroend


!macro customInstall
    !insertmacro CheckForDependencies
!macroend
