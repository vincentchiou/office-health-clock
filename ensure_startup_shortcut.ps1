$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupVbs = Join-Path $scriptDir 'startup.vbs'

if (-not (Test-Path -LiteralPath $startupVbs)) {
    Write-Host '[setup] startup.vbs not found.'
    exit 1
}

$startupFolder = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupFolder 'Office Health Reminder.lnk'
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
$shortcut.Arguments = '"{0}"' -f $startupVbs
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description = 'Office Health Reminder startup launcher'
$shortcut.IconLocation = '{0},0' -f $startupVbs
$shortcut.Save()

Write-Host '[setup] Startup shortcut ensured.'
