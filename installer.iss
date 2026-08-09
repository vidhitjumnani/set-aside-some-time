#define MyAppName "Set Aside Some Time"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Set Aside Some Time"
#define MyAppExeName "Set Aside Some Time.exe"

[Setup]
AppId={{7E0C7A8A-7C6D-4B5D-A3C5-8E4C2A8B9F11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\Set Aside Some Time

OutputDir=installer
OutputBaseFilename=SetAsideSomeTimeSetup

SetupIconFile=icon.ico

Compression=lzma
SolidCompression=yes

PrivilegesRequired=admin

WizardStyle=modern

UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\Set Aside Some Time.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.ini"; DestDir: "{userappdata}\Set Aside Some Time"; Flags: onlyifdoesntexist

[Icons]
Name: "{autodesktop}\Set Aside Some Time"; Filename: "{app}\{#MyAppExeName}"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Set Aside Some Time"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Set Aside Some Time"; Flags: nowait postinstall