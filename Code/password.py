import displayio
from terminalio import FONT
from adafruit_display_text import label, wrap_text_to_lines
from timetrigger import Timer
from buzzer import BuzzerApp
from item import ascii_mod

class Password(BuzzerApp):
    def __init__(self):
        # setting
        self.scale = 2
        
        #%% display
        self.splash = displayio.Group()
        
        # all text
        self.all_text = label.Label(
            FONT,
            text='',
            anchor_point = (0, 0.5), # top left
            anchored_position = (0, 32), # position
            color=0xFFFFFF,
            scale = self.scale
        )
        self.splash.append(self.all_text)
        
        #%% draw a square (cursor)
        self.cursor_bitmap = displayio.Bitmap(6 * self.scale, 32, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        self.cursor_disp = displayio.TileGrid(
            self.cursor_bitmap, 
            pixel_shader=color_palette,
            x=0, y=16,
        )
        self.splash.append(self.cursor_disp)
                
        # cursor text
        self.cursor_text = label.Label(
            FONT,
            anchor_point = (0, 0.5), # top left
            anchored_position = (0, 32), # position
            text='',
            color=0x000000,
            scale = self.scale,
        )
        self.splash.append(self.cursor_text)
        
        # keyboard
        self.key = '0'

    def update(self, ring):
        self.ring_get = ring.get(True)
        # buzzer
        super().update(self.ring_get, True)
        
        
        # if back
        if self.ring_get['buttons_hold']['up'] == 1:
            print('back')
            return -1, None
        
        # input
        self.key = self.key[:-1] + \
            chr(ascii_mod(ord(self.key[-1]) + self.ring_get['dial']))
            
        # logic
        if self.ring_get['buttons_hold']['up'] == 1:
            # back
            return -1, None
        if self.ring_get['buttons']['center'] == -1:
            # enter
            return 1, self.key
        if self.ring_get['buttons']['right'] == -1:
            # next
            self.key = self.key + '0'
        if self.ring_get['buttons']['left'] == -1:
            # backspace
            if len(self.key) > 1:
                self.key = self.key[:-1]
        if self.ring_get['buttons']['up'] == -1:
            self.key = self.key[:-1] + \
                chr(ascii_mod(ord(self.key[-1]) - 10))
        if self.ring_get['buttons']['down'] == -1:
            self.key = self.key[:-1] + \
                chr(ascii_mod(ord(self.key[-1]) + 10))
        
        return 0, None

    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        
        cursor = self.key[-1]
        if cursor != self.cursor_text.text:
            self.cursor_text.text = cursor
        if self.key != self.all_text.text:
            self.all_text.text = self.key
            
        self.cursor_disp.x = 6 * self.scale * (len(self.all_text.text) - 1)
        self.cursor_text.anchored_position = (self.cursor_disp.x, 32)
        # buzzer
        super().display(buzzer)
        return 

    def receive(self, message):
        return
