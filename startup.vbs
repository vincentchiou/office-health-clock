Dim project
project = "H:\我的雲端硬碟\ViberCoding-ClaudeCode\projects\辦公室檢康提醒"

Set WShell = CreateObject("WScript.Shell")
WShell.CurrentDirectory = project
WShell.Run """" & project & "\start.bat""", 0, False
