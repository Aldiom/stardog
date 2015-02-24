; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
#pragma include __INCLUDE__ + ";" + "c:\Program Files\Inno Download Plugin/idp.iss"
#define MyAppName "stardog"
#define MyAppVersion "3"
#define PyToDOwn "python-2.7.9.msi"
#define PyGameToDown  "pygame-1.9.2a0.win32-py2.7.msi"
#define MyTitleName "StarDog" 


[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{1606C853-76D6-4F34-8406-9D2879C2E1F3}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=stardog-installer
#include <idp.iss>
ChangesEnvironment=yes

[Icons]
Name: "{group}\StarDog"; Filename: "c:\Python27\python.exe"; WorkingDir: "{app}"; Parameters: """{app}\stardog.py"""
Name: "{group}\Updater"; Filename: "c:\Python27\python.exe"; WorkingDir: "{app}"; Parameters: """{app}\updater.py"""


[UninstallDelete]
Type: filesandordirs; Name: "{app}\*.*"

[CustomMessages]
AppAddPath=Add application directory to your environmental path (required)

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked;
Name: modifypath; Description:{cm:AppAddPath}; 

[CustomMessages]
AppAddPath="Add application directory to your environmental path (required)"

[Files]
Source: "{tmp}\{#PyToDOwn}"; DestDir: "{app}"; Flags: external deleteafterinstall;
Source: "{tmp}\{#PyGameToDown}"; DestDir: "{app}"; Flags: external deleteafterinstall;
Source: "{tmp}\updater.py"; DestDir: "{app}";  Flags: external;

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};c:\Python27"

[Run]
Filename: "msiexec.exe"; Parameters: "/i""{app}\{#PyToDOwn}"""
Filename: "msiexec.exe"; Parameters: "/i""{app}\{#PyGameToDown}"" /qb"
Filename: "c:\Python27\python.exe"; WorkingDir: "{app}"; Parameters: """{app}\updater.py"""

[Code]
procedure InitializeWizard();
begin
 idpAddFile('https://www.python.org/ftp/python/2.7.9/{#PyToDOwn}', ExpandConstant('{tmp}\{#PyToDOwn}'));
    idpAddFile('http://pygame.org/ftp/{#PyGameToDown}', ExpandConstant('{tmp}\{#PyGameToDown}'));
    idpAddFile('https://raw.githubusercontent.com/aaps/stardog/master/updater.py', ExpandConstant('{tmp}\updater.py'));
    idpDownloadAfter(wpReady);
end;

const
    ModPathName = 'modifypath';
    ModPathType = 'system';

function ModPathDir(): TArrayOfString;
begin
    setArrayLength(Result, 1)
    Result[0] := ExpandConstant('C:\Python27');
end;

#include "modpath.iss"