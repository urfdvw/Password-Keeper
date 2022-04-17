from time import monotonic

# Timer class
class Timer:
    def __init__(self, hold=False):
        self.duration = 0
        self.start_time = monotonic()
        self.enable = False
        self.hold = hold
        self.dt = 0
    def over(self):
        self.dt = monotonic() - self.start_time
        out = (self.dt > self.duration) and self.enable
        if out and not self.hold:
            self.enable = False
        return out
    def start(self, duration):
        self.duration = duration
        self.start_time = monotonic()
        self.enable = True
    def disable(self):
        self.enable = False
        
class Repeat:
    def __init__(self, FPS):
        self.timer = Timer()
        self.FPS = 0 # measurement
        self.duration = 1 / FPS # set
        self.timer.start(0)
    def check(self):
        if self.timer.over():
            self.FPS = 1 / self.timer.dt
            self.timer.start(self.duration)
            return True
        else:
            return False
        