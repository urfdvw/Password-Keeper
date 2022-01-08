import displayio
from terminalio import FONT
from adafruit_display_text import label, wrap_text_to_lines
from timetrigger import Timer
from buzzer import BuzzerApp

class Menu(BuzzerApp):
    def __init__(self, items):
        # data
        self.items = items
        
        # display
        self.screen_N = min(len(self.items), 4)
        self.splash = displayio.Group()
        
        
        # note text
        self.note_text = label.Label(
            FONT,
            text='',
            anchor_point = (0, 0), # top left
            anchored_position = (0, 16), # position
            color=0xFFFFFF,
        )
        self.splash.append(self.note_text)
        
        # draw a square (cursor)
        self.cursor_bitmap = displayio.Bitmap(126, 16, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        self.cursor_disp = displayio.TileGrid(
            self.cursor_bitmap, 
            pixel_shader=color_palette,
            x=0, y=0,
        )
        self.splash.append(self.cursor_disp)
        
        # draw a square (scroll)
        self.scroll_size = max(20, 64 // len(self.items))
        self.scroll_bitmap = displayio.Bitmap(1, self.scroll_size, 1)
        scroll_palette = displayio.Palette(1)
        scroll_palette[0] = 0xFFFFFF  # White
        self.scroll_disp = displayio.TileGrid(
            self.scroll_bitmap, 
            pixel_shader=color_palette,
            x=127, y=0,
        )
        self.splash.append(self.scroll_disp)
                
        # name text
        self.name_text = label.Label(
            FONT,
            anchor_point = (0, 0), # top left
            anchored_position = (0, 0), # position
            text='',
            color=0x000000,
        )
        self.splash.append(self.name_text)
        

        # states
        self.ind = 0
        self.ind_screen = 0
        
    def update(self, ring, back=False):
        self.ring_get = ring.get(back)
        # buzzer
        super().update(self.ring_get, back)
        # logic
        self.ind += self.ring_get['dial']
        if self.ind - self.ind_screen >= self.screen_N:
            self.ind_screen = self.ind - (self.screen_N - 1)
        if self.ind < self.ind_screen:
            self.ind_screen = self.ind
            
        return 0, None
        

    def mod(self, ind):
        while ind >= len(self.items):
            ind -= len(self.items)
        while ind < 0:
            ind += len(self.items)
        return ind
        
    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        # note
        note = '\n'.join([
            self.items[self.mod(i + self.ind_screen)]
            for i in range(self.screen_N)
        ])
        if note != self.note_text.text:
            self.note_text.text = note
        # name
        name = self.items[self.mod(self.ind)]
        if name != self.name_text.text:
            self.name_text.text = name
        # position
        y = 16 * (self.ind - self.ind_screen)
        self.note_text.anchored_position = (0, 0)
        self.cursor_disp.y = y
        self.name_text.anchored_position = (0, y)
        self.scroll_disp.y = int(round(
            (64 - self.scroll_size) * self.mod(self.ind) / (len(self.items) - 1)
        ))
        # buzzer
        super().display(buzzer)
        return 

    def receive(self, message):
        return