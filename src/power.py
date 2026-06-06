import ctypes
from PyQt6.QtCore import QThread, pyqtSignal

POWER_CHECK_INTERVAL = 2000  # milliseconds

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus",        ctypes.c_byte),
        ("BatteryFlag",         ctypes.c_byte),
        ("BatteryLifePercent",  ctypes.c_byte),
        ("SystemStatusFlag",    ctypes.c_byte),
        ("BatteryLifeTime",     ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]

# define return type and args once at module level
_get_power_status = ctypes.windll.kernel32.GetSystemPowerStatus
if _get_power_status:
    _get_power_status.restype  = ctypes.c_bool
    _get_power_status.argtypes = [ctypes.POINTER(SYSTEM_POWER_STATUS)]


class PowerMonitor(QThread):
    plugged   = pyqtSignal()
    unplugged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running    = False
        self._last_state = None

    def _is_charging(self) -> bool | None:
        try:
            status  = SYSTEM_POWER_STATUS()
            success = _get_power_status(ctypes.byref(status)) 
            if not success:
                print("[power] warning: GetSystemPowerStatus returned False")
                return None
            if status.ACLineStatus == 255: 
                print("[power] warning: ACLineStatus is unknown (255)")
                return None
            return status.ACLineStatus == 1
        except Exception as e:
            print(f"[power] error: {e}")
            return None

    def run(self):
        self._running    = True
        self._last_state = self._is_charging()

        while self._running:
            current = self._is_charging()

            if current is None:
                pass
            elif self._last_state is None:
                self._last_state = current
            elif current != self._last_state:
                if not current:
                    self.unplugged.emit()
                else:
                    self.plugged.emit()
                self._last_state = current

            # sleep after check, not before
            for _ in range(4):
                if not self._running:
                    break
                self.msleep(500)

    def stop(self):
        self._running = False

    def is_charging(self) -> bool | None:
        return self._is_charging()