# yeelight-control
A python application for Yeelight bulbs control via LAN

----

## How to run on Python
### 1. Install Python 3
https://www.python.org/downloads/
### 2. Install YeeLight library for python
https://yeelight.readthedocs.io/en/latest/

#### On Windows:
- open Command Prompt
- install the following packages:
-- `pip install yeelight`
-- `pip install opencv-python`
-- `pip install pillow`

### 3. Download and run the code
- Download and extract the code from the archive.
- Double click on `yeelight-control.py` file.

Program was tested using `yeelink.light.color2` and `yeelink.light.color4` bulbs.

----
## How to build into an .exe
`pyinstaller -F --add-data "yeelight-control.db;." --icon=logo.ico yeelight-control.py`

## Roadmap
### ✔️ v1.0
- Adding bulbs (setting bulb state, getting bulb status)
- Presets support (to be used to change bulb state)
- Creating and applying scenes

### ✔️ v1.1
- Multiple UX improvements
- Adding Scene management
- Ambient lighting feature

### v2.x
- ~~enable support for the button box device made on Raspberry Pi Pico platform~~ moved to [uyeelight-control](https://github.com/arrecifior/uyeelight-control "uyeelight-control") project
- GUI support
- Support for scene state sync
