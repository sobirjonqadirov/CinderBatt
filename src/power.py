import ctypes
import threading
import time

POWER_CHECK_INTERVAL = 5  # seconds

class PowerMonitor:
    def __init__(self, on_unplug=None, on_plug=None):
        self.on_unplug = on_unplug
        self.on_plug   = on_plug
        self._last_state = self._is_charging()
        self._running = False
        self._thread  = None

    def _is_charging(self):
        class SYSTEM_POWER_STATUS(ctypes.Structure):
            _fields_ = [
                ("ACLineStatus",        ctypes.c_byte),
                ("BatteryFlag",         ctypes.c_byte),
                ("BatteryLifePercent",  ctypes.c_byte),
                ("SystemStatusFlag",    ctypes.c_byte),
                ("BatteryLifeTime",     ctypes.c_ulong),
                ("BatteryFullLifeTime", ctypes.c_ulong),
            ]

        status = SYSTEM_POWER_STATUS()
        ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
        return status.ACLineStatus == 1  # 1 = plugged in

    def _loop(self):
        while self._running:
            current = self._is_charging()
            if current != self._last_state:
                if not current and self.on_unplug:
                    self.on_unplug()
                elif current and self.on_plug:
                    self.on_plug()
                self._last_state = current
            time.sleep(POWER_CHECK_INTERVAL)

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def is_charging(self):
        return self._is_charging()