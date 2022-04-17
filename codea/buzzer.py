import pwmio
from time import sleep

# define buzzer
class Buzzer:
    def __init__(self, pin):
        self.buzzer = pwmio.PWMOut(pin, variable_frequency=True)
        self.buzzer.duty_cycle = 0
    def beep(self, freq):
        if freq == 0:
            self.buzzer.duty_cycle = 0
            return
        else:
            self.buzzer.frequency = freq
            self.buzzer.duty_cycle = 32768
            return
        
# Buzzer enabled app class
class BuzzerApp():
    def update(self, ring_get, long_sound=False, long_back_sound=False):
        self.freq = 0
        if long_sound:
            if 1 in ring_get['buttons_hold'].values():
                # if long press
                self.freq = 1200
        if long_back_sound:
            if ring_get['buttons_hold']['up'] == 1:
                # if long press on back
                self.freq = 1200
        if ring_get['buttons']['center'] == 1 \
            or ring_get['buttons']['ring'] == 1 \
            or ring_get['dial']:
            # if press or slide
            self.freq = 1000
        elif -1 in list(ring_get['buttons'].values())[:-1]:
            # if release
            self.freq = 1200
            
    def display(self, buzzer):
        if self.freq:
            buzzer.beep(freq=self.freq)
            sleep(0.01)
            buzzer.beep(freq=0)
        else:
            buzzer.beep(freq=0) 
            