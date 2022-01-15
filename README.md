# Password Keeper

## Why
This DIY project is a USB password management device for people who
- hate auto-saving passwords on browsers
- use public computers or changes devices all the time
- are forced to set a different "strong" password every month (me)
- have a lot of super-long passwords, such as Github keys and SSH keys.

This project focus on the user experiences. It is not for the highest security.

## Based on

Hardware and modules
- Pi Pico
- I2C SSD1306 OLED screen

Languages and libraries
- CircuitPython
    - displayio
    - usb_hid
    - touchio
- JavaScript
    - Chrome File API
    - Ace Editor

Techniques
- Finite state machines
- Vigenère cipher