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

# basic logic

Sound
- all sounds are just a brief beep (one frame) unless special usages
    - tictoc is used to avoid continuous sound
- sound is controlled by `self.freq`
    - it is going to control the buzzer for one frame
- press sound is only for indication (1000)
    - so in ui inpit
- release sound is when action taken (1200)
    - so in logic
- as sound is so different in every app
    - here we sacrifice the reusability
    - and let each app decide what soud they want