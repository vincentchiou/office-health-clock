# core/system_monitor.py — 系統硬體監控（CPU/GPU 溫度、VRAM/RAM 用量、CUDA 使用率）

import os
import platform
import subprocess
import sys
import tempfile
import time


class SystemMonitor:
    """
    監控系統硬體狀態，提供快取讀取 API：
    - CPU 溫度（°C）— 透過背景 PowerShell helper
    - GPU 溫度（°C）
    - VRAM 用量（GB / GB / %）
    - RAM 用量（GB / GB / %）
    - GPU 使用率（%）
    """

    CPU_TEMP_FILE = os.path.join(tempfile.gettempdir(), "health_clock_cpu_temp_v2.txt")
    CPU_HELPER_PID_FILE = os.path.join(tempfile.gettempdir(), "health_clock_cpu_helper_v2.pid")
    CPU_TEMP_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cpu_temp_helper.ps1")

    def __init__(self):
        self._gpu = None
        self._has_nvml = False
        self._lhm_computer = None
        self._has_lhm = False
        self._cpu_helper_started = False

        # 快取值
        self.cpu_temp = None       # °C
        self.cpu_util = 0.0        # %
        self.gpu_temp = None       # °C
        self.vram_used = 0.0       # GB
        self.vram_total = 0.0      # GB
        self.vram_pct = 0.0        # %
        self.ram_used = 0.0        # GB
        self.ram_total = 0.0       # GB
        self.ram_pct = 0.0         # %
        self.gpu_util = 0.0        # %

        self._init_nvml()
        self._init_lhm()
        self._ensure_cpu_helper()

    # ── 初始化 ────────────────────────────────────────────

    def _init_nvml(self):
        try:
            import pynvml
            pynvml.nvmlInit()
            self._gpu = pynvml
            self._has_nvml = True
        except Exception:
            self._has_nvml = False

    def _init_lhm(self):
        """透過 pythonnet 載入 LibreHardwareMonitorLib.dll。"""
        if platform.system() != "Windows":
            return
        try:
            import clr
            # 找到 DLL 路徑
            lhm_dir = self._find_lhm_dll()
            if not lhm_dir:
                return
            clr.AddReference(os.path.join(lhm_dir, "LibreHardwareMonitorLib"))
            from LibreHardwareMonitor.Hardware import Computer

            computer = Computer()
            computer.IsCpuEnabled = True
            computer.IsGpuEnabled = True
            computer.Open()
            self._lhm_computer = computer
            self._has_lhm = True
        except Exception:
            self._has_lhm = False

    def _find_lhm_dll(self) -> str:
        """搜尋 LibreHardwareMonitorLib.dll 安裝路徑。"""
        candidates = [
            # WinGet 安裝路徑
            os.path.expandvars(
                r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"
                r"\LibreHardwareMonitor.LibreHardwareMonitor_*"
            ),
            # 常見安裝路徑
            r"C:\Program Files\LibreHardwareMonitor",
            r"C:\Program Files (x86)\LibreHardwareMonitor",
        ]
        import glob
        for pattern in candidates:
            for d in glob.glob(pattern):
                dll = os.path.join(d, "LibreHardwareMonitorLib.dll")
                if os.path.isfile(dll):
                    return d
        return None

    def _ensure_cpu_helper(self):
        """確保背景 CPU 溫度 helper 正在執行。"""
        if platform.system() != "Windows":
            return
        if not os.path.isfile(self.CPU_TEMP_SCRIPT):
            return
        # 檢查 helper 是否已在執行（先看 PID 檔，再確認有有效溫度檔）
        try:
            if os.path.isfile(self.CPU_HELPER_PID_FILE):
                with open(self.CPU_HELPER_PID_FILE, "r", encoding="utf-8-sig") as f:
                    pid = f.read().strip()
                if pid:
                    result = subprocess.run(
                        ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                        capture_output=True, text=True, timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    if pid in result.stdout and self._has_valid_cpu_temp_file():
                        self._cpu_helper_started = True
                        return
        except Exception:
            pass
        # 啟動 helper（以管理員權限）
        try:
            ps_cmd = f'Start-Process powershell -Verb RunAs -WindowStyle Hidden -ArgumentList "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \\"{self.CPU_TEMP_SCRIPT}\\""'
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self._cpu_helper_started = True
        except Exception:
            pass

    def _has_valid_cpu_temp_file(self) -> bool:
        try:
            if not os.path.isfile(self.CPU_TEMP_FILE):
                return False
            if time.time() - os.path.getmtime(self.CPU_TEMP_FILE) > 30:
                return False
            with open(self.CPU_TEMP_FILE, "r", encoding="utf-8-sig") as f:
                val = f.read().strip()
            if not val or val == "error":
                return False
            float(val)
            return True
        except Exception:
            return False

    # ── 公開 API ──────────────────────────────────────────

    def update(self):
        """重新讀取所有硬體數值並更新快取。"""
        self._update_gpu()
        self._update_cpu_temp()
        self._update_cpu_util()
        self._update_ram()

    def get_status_text(self) -> str:
        """回傳簡短狀態字串，供 UI 顯示。"""
        parts = []
        if self.cpu_temp is not None:
            parts.append(f"CPU {self.cpu_temp:.0f}°C")
        if self.gpu_temp is not None:
            parts.append(f"GPU {self.gpu_temp:.0f}°C")
        if self.vram_total > 0:
            parts.append(f"VRAM {self.vram_used:.1f}/{self.vram_total:.1f}G")
        if self.ram_total > 0:
            parts.append(f"RAM {self.ram_used:.1f}/{self.ram_total:.1f}G")
        if self._has_nvml:
            parts.append(f"CUDA {self.gpu_util:.0f}%")
        return "  ".join(parts) if parts else "無可用感測器"

    # ── GPU（pynvml）──────────────────────────────────────

    def _update_gpu(self):
        if not self._has_nvml:
            return
        try:
            pynvml = self._gpu
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            # GPU 溫度
            try:
                self.gpu_temp = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU)
            except Exception:
                self.gpu_temp = None

            # GPU 使用率
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                self.gpu_util = util.gpu
            except Exception:
                self.gpu_util = 0.0

            # VRAM
            try:
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                self.vram_used = mem.used / (1024 ** 3)
                self.vram_total = mem.total / (1024 ** 3)
                self.vram_pct = (mem.used / mem.total * 100) if mem.total else 0
            except Exception:
                pass

        except Exception:
            pass

    # ── CPU 溫度 ──────────────────────────────────────────

    def _update_cpu_temp(self):
        """直接透過 LibreHardwareMonitor DLL 讀取 CPU 溫度。"""
        # 優先嘗試 LHM（不需要管理員權限即可讀取大部分感測器）
        if self._has_lhm and self._lhm_computer:
            try:
                from LibreHardwareMonitor.Hardware import HardwareType, SensorType
                for hw in self._lhm_computer.Hardware:
                    if hw.HardwareType == HardwareType.Cpu:
                        hw.Update()
                        best = None
                        for sensor in hw.Sensors:
                            if sensor.SensorType == SensorType.Temperature and sensor.Value is not None:
                                name = sensor.Name.lower()
                                # 優先 Package / Core / CPU 溫度，排除 Distance / Hotspot
                                if "distance" in name or "hotspot" in name:
                                    continue
                                if "package" in name:
                                    self.cpu_temp = float(sensor.Value)
                                    return
                                if "core" in name or "cpu" in name:
                                    if best is None or float(sensor.Value) > best:
                                        best = float(sensor.Value)
                        if best is not None:
                            self.cpu_temp = best
                            return
            except Exception:
                pass

        # 後備：嘗試從暫存檔讀取（由背景 helper 寫入）
        try:
            if os.path.isfile(self.CPU_TEMP_FILE):
                with open(self.CPU_TEMP_FILE, "r", encoding="utf-8-sig") as f:
                    val = f.read().strip()
                if val and val != "error":
                    self.cpu_temp = float(val)
                    return
        except (ValueError, OSError):
            pass

        # 最後後備：嘗試 WMI（需要管理員權限）
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace 'root/WMI' -ErrorAction Stop | Select-Object -First 1 -ExpandProperty CurrentTemperature"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            raw = result.stdout.strip()
            if raw:
                celsius = float(raw) / 10.0 - 273.15
                if 0 < celsius < 150:
                    self.cpu_temp = round(celsius, 1)
                    return
        except Exception:
            pass

    # ── CPU 使用率 ──────────────────────────────────────

    def _update_cpu_util(self):
        try:
            import psutil
            self.cpu_util = psutil.cpu_percent(interval=0)
        except Exception:
            pass

    # ── RAM（psutil）──────────────────────────────────────

    def _update_ram(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            self.ram_used = mem.used / (1024 ** 3)
            self.ram_total = mem.total / (1024 ** 3)
            self.ram_pct = mem.percent
        except ImportError:
            # 後備：直接讀 Windows API
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                ctypes.windll.kernel32.SetProcessDPIAware()

                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                mem = MEMORYSTATUSEX()
                mem.dwLength = ctypes.sizeof(mem)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
                total = mem.ullTotalPhys
                avail = mem.ullAvailPhys
                used = total - avail
                self.ram_total = total / (1024 ** 3)
                self.ram_used = used / (1024 ** 3)
                self.ram_pct = mem.dwMemoryLoad
            except Exception:
                pass

    # ── 清理 ──────────────────────────────────────────────

    def shutdown(self):
        if self._has_nvml:
            try:
                self._gpu.nvmlShutdown()
            except Exception:
                pass
        if self._has_lhm and self._lhm_computer:
            try:
                self._lhm_computer.Close()
            except Exception:
                pass
