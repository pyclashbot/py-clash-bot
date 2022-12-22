!addplugindir "plugins"

!macro customInstall
    ; AutoHotKey
    ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AutoHotKey" "DisplayIcon"
    IfErrors +1 +10
        MessageBox MB_YESNO "AutoHotKey is not installed. Install now?" /SD IDYES IDNO noinstall
        ClearErrors
        inetc::get /CAPTION "Downloading AutoHotKey Installer" \
        "https://www.autohotkey.com/download/ahk-install.exe" \
        "$INSTDIR\ahk-install.exe" /END
        ExecWait "$INSTDIR\ahk-install.exe" $0
        IfErrors +1 +4
            MessageBox MB_OK "AHK installation failed. Aborting!"
            Delete "$INSTDIR\ahk-install.exe"
            Abort
        Delete "$INSTDIR\ahk-install.exe"
    ClearErrors

    ; MEmu
    ReadRegStr $R0 HKLM "SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MEmu" "InstallLocation"
    IfErrors +1 +10
        MessageBox MB_YESNO "MEmu is not installed. Install now?" /SD IDYES IDNO noinstall
        ClearErrors
        inetc::get /CAPTION "Downloading MEmu Installer" \
        "https://dl.memuplay.com/download/MEmu-setup-abroad-sdk.exe" \
        "$INSTDIR\MEmu-setup-abroad-sdk.exe" /END
        ExecWait "$INSTDIR\MEmu-setup-abroad-sdk.exe" $0
        IfErrors +1 +4
            MessageBox MB_OK "MEmu installation failed. Aborting!"
            Delete "$INSTDIR\MEmu-setup-abroad-sdk.exe"
            Abort
        Delete "$INSTDIR\MEmu-setup-abroad-sdk.exe"
    ClearErrors
    goto done
    noinstall:
        MessageBox MB_OK "Installation skipped. Aborting!"
        Abort
    done:
!macroend
