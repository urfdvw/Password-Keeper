import pwmio

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