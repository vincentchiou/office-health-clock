# cpu_temp_helper.ps1 — 背景讀取 CPU 溫度並寫入暫存檔
# 需以管理員權限執行（由 start.bat 或排程觸發）

$tempFile = "$env:TEMP\health_clock_cpu_temp_v2.txt"
$writeFile = "$env:TEMP\health_clock_cpu_temp_v2.write"

$pidFile = "$env:TEMP\health_clock_cpu_helper_v2.pid"
Set-Content -Path $pidFile -Value $PID -Encoding ASCII -Force

try {
    while ($true) {
        try {
            $celsius = $null

            $lhmRoots = @(
                "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\LibreHardwareMonitor.LibreHardwareMonitor_Microsoft.Winget.Source_8wekyb3d8bbwe",
                "C:\Program Files\LibreHardwareMonitor",
                "C:\Program Files (x86)\LibreHardwareMonitor"
            )

            foreach ($root in $lhmRoots) {
                $dll = Join-Path $root "LibreHardwareMonitorLib.dll"
                if (Test-Path -LiteralPath $dll) {
                    Add-Type -Path $dll -ErrorAction SilentlyContinue
                    $computer = New-Object LibreHardwareMonitor.Hardware.Computer
                    $computer.IsCpuEnabled = $true
                    $computer.Open()
                    try {
                        $values = @()
                        foreach ($hw in $computer.Hardware) {
                            if ($hw.HardwareType -eq [LibreHardwareMonitor.Hardware.HardwareType]::Cpu) {
                                $hw.Update()
                                foreach ($sensor in $hw.Sensors) {
                                    if ($sensor.SensorType -eq [LibreHardwareMonitor.Hardware.SensorType]::Temperature -and $sensor.Value -ne $null) {
                                        if ($sensor.Name -notmatch "Distance") {
                                            $values += [double]$sensor.Value
                                        }
                                    }
                                }
                            }
                        }
                        if ($values.Count -gt 0) {
                            $celsius = [math]::Round(($values | Measure-Object -Maximum).Maximum, 1)
                        }
                    } finally {
                        $computer.Close()
                    }
                    if ($celsius -ne $null) { break }
                }
            }

            if ($celsius -eq $null) {
                $temps = Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace "root/WMI" -ErrorAction Stop
                $maxTemp = ($temps | Measure-Object -Property CurrentTemperature -Maximum).Maximum
                if ($maxTemp -ne $null) {
                    $celsius = [math]::Round(($maxTemp / 10.0) - 273.15, 1)
                }
            }

            if ($celsius -eq $null) { throw "No CPU temperature sensor value" }
            [System.IO.File]::WriteAllText($writeFile, $celsius.ToString())
            if (Test-Path -LiteralPath $tempFile) { Remove-Item -LiteralPath $tempFile -Force -ErrorAction SilentlyContinue }
            Move-Item -Path $writeFile -Destination $tempFile -Force -ErrorAction Stop
        } catch {
            $errMsg = "error"
            try { [System.IO.File]::WriteAllText($writeFile, $errMsg) } catch {}
            try {
                if (Test-Path -LiteralPath $tempFile) { Remove-Item -LiteralPath $tempFile -Force -ErrorAction SilentlyContinue }
                Move-Item -Path $writeFile -Destination $tempFile -Force -ErrorAction SilentlyContinue
            } catch {}
        }
        Start-Sleep -Seconds 3
    }
} finally {
    if (Test-Path -LiteralPath $pidFile) {
        Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    }
}
