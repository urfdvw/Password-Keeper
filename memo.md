# Developer Memo
Here, I note logic that is not obvious by code.

This project is not only to build a working device for password management,
it also aims to provide a framework for
"Sort of complex" devices with
similar hardware that runs
multiple mini-apps,
and multiple background procedures.

# class dependency tree
- `App` (ABC): Apps with OLED UI
    - `BounceBall`: A game app
    - `Item`: App for typing password
    - `Menu` (ABC): Apps with list of text as menu
        - `Mainmenu`: App for main menu
        - `AccountList`: App for list accounts
- `Background_app` (ABC): Apps without UI
    - `FpsControl`
    - `FpsMonitor`

# File structure
All board specifications are in code.py.
Peripheral drivers are in driver.py.
Time-related tools are defined in timetrigger.py
Apps with UI are in Aplication.py
Background processes are in backgrounf.py

# code.py structure
- hardware and then software object instanciation and initialization should be here
    - class definitions should be in other modules
    - out put first and input after
        - this is for displaying debug info when not using USB
            - Should try BLE work flow later
- while true main loop at the end for managing the life cycle of the apps.

# Sound
- all sounds are just a brief beep (one frame) unless special usage
    - tic-toc is used to avoid continuous sound
- sound is controlled by `self.freq`
    - it is going to control the buzzer for one frame
- press sound is only for the indication (1000)
    - so, in UI input
- release sound is when the action is taken (1200)
    - so, in logic
- as sound is so different in every app
    - here, we sacrifice the reusability
    - and let each app decide what sound they want

# Life cycle of application
The life cycle only contains three parts: receive, update, and display.
This is designed for simple logic instead of complex procedures.
```
0 (device power on)
1 __init__
2 (wait)
3 reveive()
4 display()
5 (repeat frames)
6 | update()
7 | display()
8 update() (with exit signal)
9 (wait)
10 back to step 3 when called again
```
- receive is viewed as the entry point of the app, usually
    - contains an enter sound
    - contains state initialization
- display is considered following an update step or a receive step
    - Exception: update with exit operation does not have display step following

# Message transmission between apps
Messages are transferred in two ways:
- direct message
- broadcasting

A direct message is used between two consecutive apps.
This should be used as much as possible.
It is convenient for apps to help each other to finish a task in a relay.

Broadcasting should only be used for states or important global messages.
It can only be overwritten instead of removed.
Use it wisely.

shift signal should and should only be used for app shifting signal.
usually
- 0 means no action
- -1 means back
- 1 and above means other apps.

