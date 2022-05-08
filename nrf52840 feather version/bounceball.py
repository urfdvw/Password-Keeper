from time import sleep
import displayio
from terminalio import FONT
from adafruit_display_text import label
from timetrigger import Timer
import random
from math import pi

class BounceBall:
    def __init__(self):
        #%% ball variables
        self.ball_size = 5
        self.ball_x = 0
        self.ball_y = 32
        self.ball_dx = 0.95
        self.ball_dy = - 1
        self.ball_ay = 0.2
        self.ball_width = 126 - self.ball_size - 1
        self.ball_height = 64 - self.ball_size - 1

        #%% display
        self.splash = displayio.Group()
        
        #%% draw a square (ball)
        self.ball_bitmap = displayio.Bitmap(self.ball_size, self.ball_size, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        self.ball_disp = displayio.TileGrid(
            self.ball_bitmap, 
            pixel_shader=color_palette, 
            x=int(self.ball_x), 
            y=int(self.ball_y)
        )
        self.splash.append(self.ball_disp)

        #%% pad variables
        self.pad_x = 0
        self.pad_size = 30

        #%% draw a square (pad)
        self.pad_bitmap = displayio.Bitmap(self.pad_size, 1, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        self.pad_disp = displayio.TileGrid(
            self.pad_bitmap, 
            pixel_shader=color_palette, 
            x=self.pad_x-self.pad_size//2, 
            y=63)
        self.splash.append(self.pad_disp)

        # Draw a label
        #     text = str(i) + ': ' + str(gc.mem_free()) # free ram
        text = "0" # free ram
        self.text_area = label.Label(
            FONT, text=text, color=0xFFFFFF, x=0, y=4
        )
        self.splash.append(self.text_area)
        
        # states
        self.freq = 0
        self.info = ''
        self.count = 0
        self.game_over = False
        self.count_up = False
        self.game_over_timer = Timer()
    
    def init(self):
        self.ball_x = 0
        self.ball_y = 32
        self.ball_dx = 0.95
        self.ball_dy = - 1
        self.count = 0
        self.count_up = True
        self.info = '0'
        
    def update(self, ring):
        ring_get = ring.get(long_back=True)
        self.freq = 0
        
        # if back
        if ring_get['buttons_hold']['up'] == 1:
            self.freq = 1200
            return -1, {
            'count': self.count,
        }
        
        # if game over
        if self.game_over == 2 and ring_get['buttons']['ring'] == 1:
            # if finger released and pressed again
            self.game_over = 1
        if self.game_over == 1 and ring_get['dial']:
            # if finger moved
            self.game_over = 0
            self.init()
        if self.game_over:
            return 0, None
        
        # physics
        self.ball_dy += self.ball_ay
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        if ring_get['buttons']['ring']:
            self.pad_x = (1 - abs(ring_get['theta']) / pi) * 127 - self.pad_size // 2
        # logic
        if self.ball_x < 0:
            self.ball_x = - self.ball_x
            self.ball_dx = - self.ball_dx
            self.freq = 880
        if self.ball_y < 0:
            self.ball_y = - self.ball_y
            self.ball_dy = - self.ball_dy
            self.freq = 880
        if self.ball_x > self.ball_width:
            self.ball_x = self.ball_width * 2 - self.ball_x
            self.ball_dx = - self.ball_dx
            self.freq = 880
        if self.ball_y > self.ball_height:
            # if ball touching bottom
            if ((self.ball_x + self.ball_size - 1) > self.pad_x) and (self.ball_x < (self.pad_x + self.pad_size + 1)):
                # if touch
                self.ball_y = self.ball_height * 2 - self.ball_y
                self.ball_dy = - self.ball_dy
                self.ball_dx -= random.uniform(
                    0.5,
                    ((self.pad_x + self.pad_size / 2) - (self.ball_x + self.ball_size / 2)) / 5
                )
                self.count += 1
                self.count_up = True
                self.freq = 880
                self.info = str(self.count)
            else:
                self.game_over = 2
                self.info = str(self.count) + ' game over'
                self.count_up = True
        return 0, None
                
    def display(self, display, buzzer):
        # display
        display.show(self.splash)
        self.ball_disp.x = int(self.ball_x)
        self.ball_disp.y = int(self.ball_y)
        self.pad_disp.x = int(self.pad_x)
        if self.count_up:
            self.count_up = False
            self.text_area.text = self.info
        # Buzzer
        buzzer.beep(freq=self.freq)
        
    def receive(self, message):
        pass