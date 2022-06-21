# Python
import random
from math import pi
from buzzer import Buzzer
# CircuitPython
import displayio
from terminalio import FONT
import usb_hid
# Adafruit
from adafruit_display_text import label, wrap_text_to_lines
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# Keeper
from timetrigger import Timer

class Application:
    def update(self):
        """ update related to main logic, once every fixed period
        return:
            shift: int
                0, no shift
                -1, back
                1~, to other app
            message: dict
                other information that the app want to send
            broadcast: dict
                message broadcast to all app
        """
        raise NotImplementedError
    def display(self):
        """ OLED and buzzer output """
        raise NotImplementedError
    def receive(self):
        """ process received message and start """
        raise NotImplementedError

class BounceBall(Application):
    def __init__(self): 

        # ball variables
        self.ball_size = 5
        self.ball_x = 0
        self.ball_y = 32
        self.ball_dx = 0.95
        self.ball_dy = - 1
        self.ball_ay = 0.2
        self.ball_width = 126 - self.ball_size - 1
        self.ball_height = 64 - self.ball_size - 1

        # display
        self.splash = displayio.Group()
        
        # draw a square (ball)
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

        # pad variables
        self.pad_x = 0
        self.pad_size = 30

        # draw a square (pad)
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
        
        # game states
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
        
    def update(self, ring_get):
        self.freq = 0
        
        # if back
        if ring_get['buttons_hold']['up'] == 1:
            return -1, {
                'count': self.count,
            }, {}

        # if game over
        if self.game_over == 2 and ring_get['buttons']['ring'] == 1:
            # if finger released and pressed again
            self.game_over = 1
        if self.game_over == 1 and ring_get['dial']:
            # if finger moved
            self.game_over = 0
            self.init()
        if self.game_over:
            # ui buzzer
            if ring_get['buttons']['up'] == 1:
                self.freq = 1000
            return 0, {}, {}
        
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
                self.info = str(self.count) + '  game over\ntouch ring to restart\nhold back to back'
                self.count_up = True
        return 0, {}, {}
                
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
        
    def receive(self, message, memo):
        print('Entered the bounce ball app')
        self.freq = 1200
        if message:
            self.init()

class Password(Application):
    def __init__(self):
        # buzzer
        self.freq = 0

        # display setting
        self.scale = 2
        
        # display
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
        
        # draw a square (cursor)
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

    def update(self, ring_get):
        # buzzer
        if ring_get['buttons']['center'] == 1 \
            or ring_get['buttons']['ring'] == 1 \
            or ring_get['dial']:
            # if press or slide
            self.freq = 1000
        if ring_get['buttons']['ring'] == -1:
            self.freq = 1200

        # logic
        if ring_get['buttons_hold']['up'] == 1:
            # back
            self.key = '0' # remove the current key
            return -1, {}, {'key': self.key}
        if ring_get['buttons']['center'] == -1:
            # enter
            return 1, {}, {'key': self.key}
        if ring_get['buttons']['right'] == -1:
            # next
            self.key = self.key + '0'
        if ring_get['buttons']['left'] == -1:
            # backspace
            if len(self.key) > 1:
                self.key = self.key[:-1] # remove the last charactor
                self.key = self.key[:-1] + '0' # change the visible charactor to '0'
        if ring_get['buttons']['up'] == -1:
            self.key = self.key[:-1] + \
                chr(ascii_mod(ord(self.key[-1]) - 10))
        if ring_get['buttons']['down'] == -1:
            self.key = self.key[:-1] + \
                chr(ascii_mod(ord(self.key[-1]) + 10))

        # key input
        self.key = self.key[:-1] + \
            chr(ascii_mod(ord(self.key[-1]) + ring_get['dial']))
            
        
        return 0, {}, {'key': self.key}

    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        
        cursor = self.key[-1]
        if cursor != self.cursor_text.text:
            self.cursor_text.text = cursor
        if self.key != self.all_text.text:
            self.all_text.text = '*' * (len(self.key))
            
        self.cursor_disp.x = 6 * self.scale * (len(self.all_text.text) - 1)
        self.cursor_text.anchored_position = (self.cursor_disp.x, 32)
        # buzzer
        buzzer.beep(freq=self.freq)
        self.freq = 0
        return 

    def receive(self, message, memo):
        self.freq = 1200
        print('Entered the Master Key app')
        self.key = '0'
        return

class Menu(Application):
    def __init__(self, items):
        # data
        self.items = items

        # buzzer
        self.freq = 0
        self.tictoc = True
        
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
        
    def update(self, ring_get):
        # buzzer
        if ring_get['buttons']['center'] == 1 \
            or ring_get['buttons']['ring'] == 1 \
            or ring_get['dial']:
            # if press or slide
            self.freq = 1000
        # logic
        self.ind += ring_get['dial']
        if self.ind - self.ind_screen >= self.screen_N:
            self.ind_screen = self.ind - (self.screen_N - 1)
        if self.ind < self.ind_screen:
            self.ind_screen = self.ind
            
        return 0, {}, {}
        
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
        if self.tictoc:
            buzzer.beep(freq=self.freq)
            self.freq = 0
        else:
            buzzer.beep(freq=0)
        self.tictoc = not self.tictoc

        return 

    def receive(self, message, memo):
        print('Entered a Menu app')
        self.freq = 1200

class MainMenu(Menu):
    def __init__(self, items):
        # call super
        super().__init__(items)
    
    def update(self, ring_get):
        super().update(ring_get)
            
        # if enter
        if ring_get['buttons']['center'] == -1:
            return 1, self.mod(self.ind), {}
            
        return 0, {}, {}

    def receive(self, message, memo):
        super().receive(message, memo)
        print("Entered the Main Menu app")
        self.freq = 1200
    
class AccountList(Menu):
    def __init__(self):
        # data
        file = open('items.csv', 'r')
        self.title = [
            sec.strip() 
            for sec in file.readline().strip().split(',')
        ]
        self.data = []
        while True:
            line_raw = file.readline().strip()
            if not line_raw:
                break
            line_list = [sec.strip() for sec in line_raw.split(',')]
            if len(line_list) > 5:
                # in case ciphered text contains ','
                line_list[4] = ','.join(line_list[4:])
                line_list = line_list[:5]
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
    
    def update(self, ring_get):
        super().update(ring_get)
            
        # if enter
        if ring_get['buttons']['center'] == -1:
            return 1, {
                'data': self.data[self.mod(self.ind)]
            }, {}
            
        # if back
        if ring_get['buttons']['up'] == -1:
            return -1, {}, {}
            
        return 0, {}, {}
        
    def receive(self, message, memo):
        super().receive(message, memo)
        print("Entered the Account list")
        self.freq = 1200

# functions for items
def ascii_mod(n):
    period = 126 - 32 + 1
    while n > 126:
        n -= period
    while n < 32:
        n += period
    return n

def vigenere(plain, key, dir=1):
    out = ""
    i = 0
    for c in plain:
        ci = chr(ascii_mod(ord(c) + dir * ord(key[i])))
        out += ci
        i += 1
        if i == len(key):
            i = 0
    return out

class Item(Application):
    def __init__(self):
        # data
        self.data = {}
        
        # display
        self.splash = displayio.Group()
        
        # draw a square (cursor)
        self.cursor_bitmap = displayio.Bitmap(128, 16, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        self.cursor_disp = displayio.TileGrid(
            self.cursor_bitmap, 
            pixel_shader=color_palette,
            x=0, y=0,
        )
        self.splash.append(self.cursor_disp)
                
        # name text
        self.name_text = label.Label(
            FONT,
            anchor_point = (0.5, 0), # top left
            anchored_position = (64, 0), # position
            text='',
            color=0x000000,
        )
        self.splash.append(self.name_text)
        
        # note text
        self.note_text = label.Label(
            FONT,
            text='',
            anchor_point = (0, 0), # top left
            anchored_position = (0, 16), # position
            color=0xFFFFFF,
        )
        self.splash.append(self.note_text)
        
        # keyboard
        self.keyboard = Keyboard(usb_hid.devices)
        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)
        self.key = 'key'
        
    def update(self, ring_get):
        # buzzer
        if ring_get['buttons']['center'] == 1 \
            or ring_get['buttons']['ring'] == 1:
            # if press
            self.freq = 1000
        # logic
        if ring_get['buttons']['up'] == -1:
            return -1, {}, {}
        if ring_get['buttons']['left'] == -1:
            self.keyboard_layout.write(self.data['username'])
        if ring_get['buttons']['down'] == -1:
            # print(self.key)
            self.keyboard_layout.write(
                vigenere(self.data['password'],
                self.key))
        if ring_get['buttons']['right'] == -1:
            self.keyboard_layout.write(self.data['link'])
        return 0, {}, {}

    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        name = self.data['website']
        note = '\n'.join(wrap_text_to_lines(self.data['note'], 21))
        if name != self.name_text.text:
            self.name_text.text = name
        if note != self.note_text.text:
            self.note_text.text = note
        # buzzer
        buzzer.beep(freq=self.freq)
        self.freq = 0
        return 

    def receive(self, message, memo):
        print("Entered the Item app")
        self.freq = 1200
        self.data = message['data']
        self.key = memo['key']
        return

class ClickWheelTest(Application):
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
        self.info = ''
        
    def update(self, ring_get):
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
        elif ring_get['buttons_hold']['up'] == 1:
            self.info = 'up hold'
        elif ring_get['buttons_hold']['down'] == 1:
            self.info = 'down hold'
        elif ring_get['buttons_hold']['left'] == 1:
            self.info = 'left hold'
        elif ring_get['buttons_hold']['right'] == 1:
            self.info = 'right hold'
        elif ring_get['buttons_hold']['center'] == 1:
            self.info = 'center hold'
        else:
            button_released = False
            
        # delayed display content
        if button_released:
            self.timer.start(2)
        if self.timer.over():
            self.info = ''
            
        # Normal return
        return 0, {}, {}
            
    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        self.text_area.text = str(self.n)
        self.button_text_area.text = self.info
            
    def receive(self, message, memo):
        self.n = message['count']