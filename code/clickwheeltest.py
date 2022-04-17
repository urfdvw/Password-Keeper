import displayio
from terminalio import FONT
from adafruit_display_text import label
from timetrigger import Timer
from buzzer import BuzzerApp

class ClickWheelTest(BuzzerApp):
    def __init__(self):
        self.splash = displayio.Group()
        
        # count text
        text = "0" # free ram
        self.text_area = label.Label(
            FONT, text=text, color=0xFFFFFF, x=0, y=3
        )
        self.splash.append(self.text_area)
        
        # button text
        button_text = "0" # free ram
        self.button_text_area = label.Label(
            FONT,
            text=button_text,
            background_color=0xFFFFFF,
            color=0x000000,
            x=0, y=58,
        )
        self.splash.append(self.button_text_area)
        
        # text display timer
        self.timer = Timer()
        
        # output contents
        self.n = 0
        self.info = '____'
        self.freq = 0
        
    def update(self, ring):
        ring_get = ring.get(long_back=True)
        # buzzer
        super().update(ring_get, long_back_sound=True)
        # if go back
        if ring_get['buttons_hold']['up'] == 1:
            print('back')
            print(self.freq)
            return 1, None
        # main logic
        self.n += ring_get['dial']
        button_released = True
        if ring_get['buttons']['up'] == -1:
            self.info = 'up'
        elif ring_get['buttons']['down'] == -1:
            self.info = 'down'
        elif ring_get['buttons']['left'] == -1:
            self.info = 'left'
        elif ring_get['buttons']['right'] == -1:
            self.info = 'right'
        elif ring_get['buttons']['center'] == -1:
            self.info = 'center'
        else:
            button_released = False
            
        # delayed display content
        if button_released:
            self.timer.start(2)
        if self.timer.over():
            self.info = '____'
            
            
        # Normal return
        return 0, None
            
    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        self.text_area.text = str(self.n)
        self.button_text_area.text = self.info
        # buzzer
        super().display(buzzer)
            
    def receive(self, message):
        self.n = message['count']