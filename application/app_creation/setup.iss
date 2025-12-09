[Setup]
AppName=Whisper AI
AppVersion=1.0.9
AppPublisher=N.Charan Kumar Reddy
DefaultDirName={autopf}\Whisper AI
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=Whisper AI
SetupIconFile="logo.ico"
Compression=lzma2
SolidCompression=yes

[Files]
Source: "Whisper AI\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "vb-audio\*"; DestDir: "{tmp}\\VB-CABLE"; Flags: recursesubdirs createallsubdirs
Source: "Set-Audio-Devices.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\\Whisper AI"; Filename: "{app}\\Whisper AI.exe"; IconFilename: "{app}\\logo.ico"
Name: "{autodesktop}\\Whisper AI"; Filename: "{app}\\Whisper AI.exe"; IconFilename: "{app}\\logo.ico"

[UninstallDelete]
; Remove the entire application directory and any user-created files/folders inside it
Type: filesandordirs; Name: "{app}"
; Remove the temporary VB-CABLE folder copied to the system temp during install (if present)
Type: filesandordirs; Name: "{tmp}\\VB-CABLE"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  ErrorCode: Integer;
  DriverPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    DriverPath := ExpandConstant('{tmp}\\VB-CABLE');

    if not DirExists(DriverPath) then
    begin
      MsgBox('The VB-CABLE driver files were not copied correctly.', mbError, MB_OK);
      Abort();
    end;

    if MsgBox('The VB-CABLE driver will now install.'#13#10 +
              'Please click Install when prompted and accept any Windows security popups.',
              mbInformation, MB_OK) = IDOK then
    begin
      if not Exec(DriverPath + '\\VBCABLE_Setup_x64.exe', '', '', SW_SHOWNORMAL,
                  ewWaitUntilTerminated, ResultCode) then
      begin
        MsgBox('Failed to launch the VB-CABLE installer.', mbError, MB_OK);
        Abort();
      end;

      if ResultCode <> 0 then
      begin
        MsgBox('VB-CABLE installation did not complete successfully.', mbError, MB_OK);
        Abort();
      end;
    end;

    if not Exec(ExpandConstant('{win}\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'),
                '-ExecutionPolicy Bypass -File "' + ExpandConstant('{app}\\Set-Audio-Devices.ps1') + '"',
                '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode) then
    begin
      MsgBox('Failed to run the audio configuration script.', mbError, MB_OK);
      Abort();
    end;

    if ResultCode <> 0 then
    begin
      if MsgBox('Automatic audio setup failed. Open Windows Sound Settings now?',
                mbError, MB_YESNO) = IDYES then
      begin
        ShellExec('', 'ms-settings:sound', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
      end;
    end;

    Exec(ExpandConstant('{app}\\Whisper AI.exe'),
         '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
  end;
end;
