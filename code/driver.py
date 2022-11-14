"""
This script contains driver classes for perferials, include
- buzzer
- the PCB touch clickwheel (sometimes called the `ring` in the code)
"""
#%% buzzer
import pwmio

# define buzzer
class Buzzer:
    """
    Driver class of the buzzer
    """
    def __init__(self, pin):
        self.buzzer = pwmio.PWMOut(pin, variable_frequency=True)
        self.buzzer.duty_cycle = 0
    def beep(self, freq):
        """
        Turn the buzzer on at a certain sound wave frequency
        freq=0 to turn off
        """
        if freq == 0:
            self.buzzer.duty_cycle = 0
            return
        else:
            self.buzzer.frequency = freq
            self.buzzer.duty_cycle = 32768
            return

#%% clickwheel
import touchio
from math import sqrt, atan2, pi, exp, sin
import time
from timetrigger import Timer

# Relay to filter out shakes
class ThetaFilter:
    def __init__(self):
        self.thr = pi / 30
        self.remain = 0
    # on theta
    def __call__(self, x):
        # return (1 / (exp(-x) +1) - 0.5) * 2 * abs(x) * 2.5 + 0.5 * x
        self.remain += x
        if self.remain > self.thr:
            y = self.remain - self.thr
        elif self.remain < -self.thr:
            y = self.remain + self.thr
        else:
            self.remain *= 0.95
            y = 0
        self.remain = self.remain - y
        return y
theta_filter = ThetaFilter()

# # uncomment and ctrl enter for plot and testing
# print('startplot:', 'y1', 'y2')
# y1 = 0
# y2 = 0
# for i in range(0, 70):
#     t = i / 100
#     x = sin(t * 10)
#     y1 += x
#     y2 += theta_filter(x)
#     print(y1, y2)

#%%
            

def theta_diff(a, b):
    c = a - b
    if c >= pi:
        c -= 2 * pi
    if c < - pi:
        c += 2 * pi
    return c

# define button
class Button:
    """
    Driver class of a single button
    """
    def __init__(self, pin):
        self.touch = touchio.TouchIn(pin)
        self.need_init = True
        self.current = False
        self.last = False
        self.en = True

    def get(self):
        # init on the first check
        if self.need_init:
            time.sleep(0.1)
            self.touch.threshold = self.touch.raw_value + 100
            self.need_init = False
        # compute output
        self.current = self.touch.value
        out = 0
        if self.current and (not self.last):
            out = 1 # press edge
        elif (not self.current) and self.last:
            if not self.en:
                self.en = True
            else:
                out = -1 # release edge
        elif self.current and self.last:
            out = 2 # hold

        self.last = self.current
        if self.en:
            return out
        else:
            return 0

# define ring
class Ring:
    """
    Driver class of the touch clickwheel
    """
    def __init__(self, pins, center, N=8):
        # center button
        self.center = center
        # ring pins
        self.ring = []
        for i in range(4):
            time.sleep(0.05)
            self.ring.append(touchio.TouchIn(pins[i]))
        # ring value range init
        self.min = []
        self.max = []
        for i in range(4):
            time.sleep(0.05)
            self.min.append(self.ring[-1].raw_value)
            self.max.append(self.min[-1] + 120)
        # constants
        self.alter_x = [-1, 0, 0, 1]
        self.alter_y = [0, 1, -1, 0]
        filtering_N = 2
        self.filtering_alpha = 1 / filtering_N
        self.dial_N = N
        # states
        self.pos_x = 0
        self.pos_y = 0
        self.r = 0
        self.theta = 0
        self.theta_last = 0
        self.theta_d = 0
        self.theta_residual = 0
        self.touch = False
        self.touch_last = False
        self.dial_changed = False
        # timer
        self.hold_timer = Timer()

    def get(self):
        # read sensor
        center_now = self.center.get()
        ring_now = [r.raw_value for r in self.ring]

        # conver sensor to weights
        w = [
            (ring_now[i] - self.min[i]) / (self.max[i] - self.min[i])
            for i in range(4)
        ]

        # computer vector sum
        pos_x = sum([w[i] * self.alter_x[i] for i in range(4)])
        pos_y = sum([w[i] * self.alter_y[i] for i in range(4)])

        # 1st-order low pass filter
        self.pos_x = pos_x * self.filtering_alpha \
            + self.pos_x * (1 - self.filtering_alpha)
        self.pos_y = pos_y * self.filtering_alpha \
            + self.pos_y * (1 - self.filtering_alpha)

        # covert xy to polar
        self.r = sqrt(self.pos_x ** 2 + self.pos_y ** 2)
        self.theta = atan2(self.pos_y, self.pos_x)

        # covert r to touch
        self.touch = self.r > 0.3

        # init outputs
        dial = 0

        buttons = {
            'left': 0,
            'right': 0,
            'up': 0,
            'down': 0,
            'center': 0,
            'ring': 0,
        }

        # touch conditions
        if self.touch and not self.touch_last: # ring touch edge
            buttons['ring'] = 1
            if self.pos_x > abs(self.pos_y): # right
                buttons['right'] = 1
            if self.pos_x < -abs(self.pos_y): # left
                buttons['left'] = 1
            if self.pos_y > abs(self.pos_x): # up
                buttons['up'] = 1
            if self.pos_y < -abs(self.pos_x): # down
                buttons['down'] = 1
            # init dial states
            self.theta_residual = 0
            self.theta_d = 0
            self.theta_last = self.theta
            self.dial_changed = False
        elif self.touch and self.touch_last: # ring hold
            buttons['ring'] = 2
            self.theta_d = theta_filter(theta_diff(self.theta, self.theta_last))
            self.theta_residual += self.theta_d
            while self.theta_residual > pi / self.dial_N:
                self.theta_residual -= 2 * pi / self.dial_N
                dial += 1
            while self.theta_residual < -pi / self.dial_N:
                self.theta_residual += 2 * pi / self.dial_N
                dial -= 1
            if dial:
                self.dial_changed = True
        elif not self.touch and self.touch_last: # ring release edge
            buttons['ring'] = -1
            if not self.dial_changed:
                if self.pos_x > abs(self.pos_y): # right
                    buttons['right'] = -1
                if self.pos_x < -abs(self.pos_y): # left
                    buttons['left'] = -1
                if self.pos_y > abs(self.pos_x): # up
                    buttons['up'] = -1
                if self.pos_y < -abs(self.pos_x): # down
                    buttons['down'] = -1
        else: # ring idle
            # center button only works when ring is not touched
            buttons['center'] = center_now

        # hold detect
        buttons_hold = {
            'left': 0,
            'right': 0,
            'up': 0,
            'down': 0,
            'center': 0,
        }

        # long press
        if buttons['ring'] == 1:
            self.hold_timer.start(1)
        if buttons['ring'] == 2 and self.hold_timer.over():
            if not self.dial_changed:
                self.dial_changed = True
                if self.pos_x > abs(self.pos_y): # right
                    buttons_hold['right'] = 1
                if self.pos_x < -abs(self.pos_y): # left
                    buttons_hold['left'] = 1
                if self.pos_y > abs(self.pos_x): # up
                    buttons_hold['up'] = 1
                if self.pos_y < -abs(self.pos_x): # down
                    buttons_hold['down'] = 1
        if center_now == 1:
            self.hold_timer.start(1)
        if center_now == 2 and self.hold_timer.over():
            buttons_hold['center'] = 1
            self.center.en = False

        # output
        out = {
            'dial': -dial,
            'buttons': buttons,
            'buttons_hold': buttons_hold,
            'theta': self.theta,
            'theta_d': -self.theta_d,
            'r': self.r,
        }

        # update
        self.touch_last = self.touch
        self.theta_last = self.theta
        return out
