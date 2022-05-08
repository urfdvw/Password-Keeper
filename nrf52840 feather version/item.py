#%% basic libs
import displayio
from terminalio import FONT
from adafruit_display_text import label, wrap_text_to_lines
from timetrigger import Timer
from buzzer import BuzzerApp
from time import sleep

#%% USB libs
import usb_hid

#%% keyboard libs
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

#%% BLE libs
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService

#%%
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
#%%
class Item(BuzzerApp):
    def __init__(self):
        #%% data
        self.data = {}
        
        #%% display
        self.splash = displayio.Group()
        
        #%% draw a square (cursor)
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
        try:
            # raise Exception('test')
            keyboard = Keyboard(usb_hid.devices)
            self.keyboard_layout = KeyboardLayoutUS(keyboard)
        except:
            hid = HIDService()
            device_info = DeviceInfoService(
                software_revision=adafruit_ble.__version__,
                manufacturer="Adafruit Industries"
                )
            advertisement = ProvideServicesAdvertisement(hid)
            advertisement.appearance = 961
            scan_response = Advertisement()
            scan_response.complete_name = "CircuitPython HID"
            
            ble = adafruit_ble.BLERadio()
            if not ble.connected:
                print("\n" * 4 + "advertising")
                ble.start_advertising(advertisement, scan_response)
                sleep(0.5)
            
            keyboard = Keyboard(hid.devices)
            self.keyboard_layout = KeyboardLayoutUS(keyboard)
            
            while not ble.connected:
                pass
        
        # decode
        self.key = 'key'

    def update(self, ring):
        ring_get = ring.get()
        # buzzer
        super().update(ring_get)
        # logic
        if ring_get['buttons']['up'] == -1:
            return -1, None
        
        if ring_get['buttons']['left'] == -1:
            self.keyboard_layout.write(self.data['username'])
        if ring_get['buttons']['down'] == -1:
            # print(self.key)
            self.keyboard_layout.write(
                vigenere(self.data['password'],
                self.key))
        if ring_get['buttons']['right'] == -1:
            self.keyboard_layout.write(self.data['link'])
        return 0, None

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
        super().display(buzzer)
        return 

    def receive(self, message):
        self.data = message['data']
        self.key = message['key']
        return