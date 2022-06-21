"""
This code test a bounce ball animation on the display.
It shows that the average frame rate is around 22.4. keep in mind.
as more pixels are refreshed, this is getting slower
"""
import board

#%% buzzer
from buzzer import Buzzer
buzzer = Buzzer(board.GP0)

#%% clickwheel
from clickwheel import Ring, Button
center = Button(board.GP9)
ring = Ring(
    [
        board.GP10, # left
        board.GP12, # up
        board.GP27, # down
        board.GP21, # right
    ],
    center,
)

#%% find the range of raw_value for ring pad.
if False:
    from time import monotonic, sleep
    tic = monotonic()
    ring_max = [0] * 4
    ring_min = [100000] * 4
    while monotonic() - tic < 5:
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
ring.max, ring.min = [2322, 2651, 2147, 2009], [794, 807, 941, 785]

#%% define screen
import busio
import displayio
import adafruit_displayio_ssd1306

displayio.release_displays()
oled_reset = None
i2c = busio.I2C(board.GP17, board.GP16, frequency=int(1e6))
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)
WIDTH = 128
HEIGHT = 64
ROTATION = 0 # or 180
FPS_SET = 30
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION)

#%% Background apps
from background import FpsControl, FpsMonitor, NumLocker, MouseJitter
        
frame_app = FpsControl(fps=30)
fpsMonitor_app = FpsMonitor(period=1, fps_app=frame_app)
num_app = NumLocker()
mouse_app = MouseJitter(period=60)
#%% apps
from application import BounceBall, MainMenu, Password, AccountList, Item, ClickWheelTest
app_ball = BounceBall()
app_menu = MainMenu([
    'password keeper',
    'bounce ball',
])
app_pass = Password()
app_accounts = AccountList()
app_item = Item()
app_test = ClickWheelTest()

app = app_pass

#%% Main logic
print('init done')
memo = {}
while True:
    # Background procedures
    fpsMonitor_app()  # monitor fps
    mouse_app()
    # num_app()  # For Windows Only


    # FPS control
    if not frame_app():
        continue
    
    # logic
    shift, message, broadcast = app.update(ring.get())
    memo.update(broadcast)
    if shift:
        if id(app) == id(app_menu):
            if shift == 1:
                if message == 0:
                    app = app_pass
                if message == 1:
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