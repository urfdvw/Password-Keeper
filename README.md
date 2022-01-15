# Password Keeper
A handy DIY off-line password management device.

## Why
This DIY project is a USB password management device for people who
- hate auto-saving passwords on browsers
- use public computers or changes devices all the time
- are forced to set a different "strong" password every month (me)
- have a lot of super-long passwords, such as Github keys and SSH keys.

This project focus on user experiences. It is not for the highest security.

## How to use

### New Password keeper User
- Open [Password Keeper Manager](https://urfdvw.github.io/Password-Keeper/) in browser
- Type in your master password
- Type your account information in the `Deciphered Text` area, following csv formate
- Click on [Save As] to download the ciphered data file `items.csv`
- Connect your password keeper to your computer and move downloaded `items.csv` to your `CIRCUITPY` drive

### Log in using the password keeper
- Connect the Password Keeper with the computer or phone with proper USB wire
- Type in Master password on your password keeper
    - rotate to change characters
    - right to add a new character
    - left to delete the last character
    - center to confirm
- Find out your account in the list
    - rotate to scroll
    - center to select
    - up to go back
- In the account
    - right to type in URL
    - left to type in user name
    - down to type in password
    - up to go back

### Update data
- Connect your password keeper to your computer
- Open [Password Keeper Manager](https://urfdvw.github.io/Password-Keeper/) in browser
- Type in your master password
- Click on [Open] and open the `items.csv` file on your `CIRCUITPY` drive
    - If your master password is wrong, the `Deciphered Text` is going to show wrong passwords
- Make changes to your account information in the `Deciphered Text` area, following csv formate
- If you need a new, you can click on [Random Password] button to generate a strong password.
- Click on [Save] to save changes
- ***It is suggested that you keep a backup of `items.csv` by [Save As], and store that ciphered data file in a safe place*** 

### Change Master Password
- With current Master Password, Open your ciphered data file `items.csv` in the [Password Keeper Manager](https://urfdvw.github.io/Password-Keeper/)
- Make sure you are seeing the correct passwords in the `Deciphered Text` area
- Change the Master Password in the manager
- Click on [Save] to save modifications

## Based on
Hardware and modules
- Pi Pico
- I2C SSD1306 OLED screen

Languages and libraries
- CircuitPython 7.0.0
    - displayio
    - usb_hid
    - touchio
- JavaScript
    - Chrome File API
    - Ace Editor

Techniques
- Finite state machines
- Vigenère cipher
