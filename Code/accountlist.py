import displayio
from terminalio import FONT
from adafruit_display_text import label, wrap_text_to_lines
from timetrigger import Timer
from buzzer import BuzzerApp
from menu import Menu
    
class AccountList(Menu):
    def __init__(self):
        # data
        file = open('items.csv', 'r')
        self.title = [
            sec.strip() 
            for sec in file.readline().strip().split(',')
        ]
        print(self.title)
        self.data = []
        while True:
            line_raw = file.readline().strip()
            if not line_raw:
                break
            line_list = [sec.strip() for sec in line_raw.split(',')]
            self.data.append({})
            for i in range(len(self.title)):
                self.data[-1][self.title[i]] = line_list[i]
        file.close()
        self.data = sorted(
            self.data,
            key=lambda x: x['website']
        )
        
        # call super
        super().__init__([self.data[i]['website'] for i in range(len(self.data))])
    
    def update(self, ring):
        super().update(ring, back=True)
            
        # if enter
        if self.ring_get['buttons']['center'] == -1:
            return 1, self.data[self.mod(self.ind)]
            
        # if back
        if self.ring_get['buttons_hold']['up'] == 1:
            print('back')
            return -1, None
            
        return 0, None