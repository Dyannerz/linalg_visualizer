[Setup]
AppName=Linear Algebra Visualizer
AppVersion=1.0
DefaultDirName={localappdata}\LinearAlgebraVisualizer
DefaultGroupName=Linear Algebra Visualizer
UninstallDisplayIcon={app}\LinearAlgebraApp.exe
OutputDir=installer_output
OutputBaseFilename=LinearAlgebraInstaller
SetupIconFile=app.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\LinearAlgebraApp\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Linear Algebra Visualizer"; Filename: "{app}\LinearAlgebraApp.exe"; IconFilename: "{app}\app.ico"
Name: "{userdesktop}\Linear Algebra Visualizer"; Filename: "{app}\LinearAlgebraApp.exe"; Tasks: desktopicon; IconFilename: "{app}\app.ico"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
