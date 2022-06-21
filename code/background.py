from timetrigger import Repeat
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

class Background_app:
    def __init__(self, freq=None, period=None):
        assert (freq is not None) != (period is not None)  # != use as xor
        if freq is not None:
            self.freq = freq
        if period is not None:
            self.freq = 1 / period
        self.repeat_timer = Repeat(self.freq)
    def procedure(self):
        return 0
    def __call__(self):
        if self.repeat_timer.check():
            return self.procedure()
        else:
            return 0
        
class FpsControl(Background_app):
    def __init__(self, fps=None):
        super().__init__(freq=fps)
        self.fps_now = 10
    def procedure(self):
        self.fps_now = self.repeat_timer.freq_measure
        return 1
        
class FpsMonitor(Background_app):
    def __init__(self, period, fps_app):
        self.fps_app = fps_app
        super().__init__(period=period)
    def procedure(self):
        print('FPS:', self.fps_app.fps_now)
        return 0

class NumLocker(Background_app):
    def __init__(self):
        super().__init__(period=0.01)
        self.keyboard = Keyboard(usb_hid.devices)
        self.key = 'key'

    def procedure(self):
        ## keep number lock
        if not int.from_bytes(self.keyboard.led_status, "big") & 1:
            self.keyboard.send(Keycode.KEYPAD_NUMLOCK)
        return 0

class MouseJitter(Background_app):
    def __init__(self, period):
        super().__init__(period=period)
        self.mouse = Mouse(usb_hid.devices)

    def procedure(self):
        # Move mouse in a loop
        self.mouse.move(10, 0, 0)
        self.mouse.move(0, 10, 0)
        self.mouse.move(0, -10, 0)
        self.mouse.move(-10, 0, 0)
        return 0
