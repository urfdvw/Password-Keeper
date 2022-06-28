"""
This script is the entry point of all scripts.
Please check the .url files for more help

Github: https://github.com/urfdvw/Password-Keeper/

Platform: Password Keeper 52840
CircuitPython: 7

Author: River Wang
Contact: urfdvw@gmail.com
License: GPL3
Date updated: 2022/06/28 (YYYY/MM/DD)
"""
import board

#%% buzzer
from driver import Buzzer
from digitalio import DigitalInOut, Direction
buzzer = Buzzer(board.TX)
fake_gnd = DigitalInOut(board.D2)
fake_gnd.direction = Direction.OUTPUT
fake_gnd = False

#%% clickwheel
from driver import Ring, Button
center = Button(board.D9)
ring = Ring(
    [
        board.RX, # left
        board.D5, # up
        board.D13, # down
        board.D10, # right
    ],
    center,
)

#%% find the range of raw_value for ring pad.
# run this code if you are testing a new PCB design
if False:
    from time import monotonic, sleep
    tic = monotonic()
    ring_max = [0] * 4
    ring_min = [100000] * 4
    while monotonic() - tic < 5:
        # run the test for 5s
        # in the mean time, slide on the ring for multiple cycles.
        for i in range(4):
            value = ring.ring[i].raw_value
            ring_max[i] = max(ring_max[i], value)
            ring_min[i] = min(ring_min[i], value)
            # print(ring_max, ring_min)
            sleep(0.1)
    print(ring_max, ',', ring_min)
    # cancel running the original script
    import sys
    sys.exit()

#%% use pre measured max and min
ring.max, ring.min = [599, 495, 526, 676] , [189, 189, 220, 200]

#%% define screen
import busio
import displayio
import adafruit_displayio_ssd1306

displayio.release_displays()
oled_reset = None
i2c = busio.I2C(board.SCL, board.SDA, frequency=int(1e6))
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)
WIDTH = 128
HEIGHT = 64
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=0)

#%% USB HID
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse

while True:
    try:
        # Keep trying connect to USB untill success
        # This useful for computer log in after boot.
        mouse = Mouse(usb_hid.devices)
        keyboard = Keyboard(usb_hid.devices)
        break
    except:
        print('\n' * 10 + 'USB not ready\nPlease Wait')

#%% Background apps
from background import FpsControl, FpsMonitor, NumLocker, MouseJitter

frame_app = FpsControl(fps=30)
fpsMonitor_app = FpsMonitor(period=10, fps_app=frame_app)
num_app = NumLocker(keyboard=keyboard)
mouse_app = MouseJitter(mouse=mouse, period=60)

#%% apps
from application import BounceBall, MainMenu, Password, AccountList, Item, ClickWheelTest
app_ball = BounceBall()
app_menu = MainMenu([
    'password keeper',
    'bounce ball',
])
app_pass = Password()
app_accounts = AccountList()
app_item = Item(keyboard)
app_test = ClickWheelTest()

app = app_pass # app to start from

#%% Main logic
print('init done')
memo = {}
while True:
    # Background procedures
    fpsMonitor_app()
    mouse_app()
    num_app()  # For Windows Only

    # FPS control
    if not frame_app():
        continue

    # logic
    shift, message, broadcast = app.update(ring.get())
    memo.update(broadcast)
    if shift:
        if id(app) == id(app_menu):
            if shift == 1:
                app = app_pass
            elif shift == 2:
                app = app_ball
        elif id(app) == id(app_pass):
            if shift == -1:
                app = app_menu
            if shift == 1:
                app = app_accounts
        elif id(app) == id(app_accounts):
            if shift == -1:
                app = app_pass
            if shift == 1:
                app = app_item
        elif id(app) == id(app_item):
            if shift == -1:
                app = app_accounts
        elif id(app) == id(app_ball):
            if shift == -1:
                app = app_menu
        app.receive(message, memo)

    # display changes
    app.display(display, buzzer)
