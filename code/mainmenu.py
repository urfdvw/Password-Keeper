import displayio
from terminalio import FONT
from adafruit_display_text import label, wrap_text_to_lines
from timetrigger import Timer
from buzzer import BuzzerApp
from menu import Menu
    
class MainMenu(Menu):
    def __init__(self, items):
        
        # call super
        super().__init__(items)
    
    def update(self, ring):
        super().update(ring, back=True)
            
        # if enter
        if self.ring_get['buttons']['center'] == -1:
            return 1, self.mod(self.ind)
            
        return 0, None