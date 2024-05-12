# About

This script is for the arcade game StepManiaX. It uses OCR to identify:

* Which screen the game is on
* Currently selected song, difficulty and logged in users on the select song screen
* Current song being played in the gameplay screen

# OBS setup

This script requires a clean gameplay feed at 1080p. You can send this feed from OBS using the virtual camera. Set the
OBS virtual camera to output your capture source directly, that way it will work even if you change scenes in OBS.

# Installing dependencies

Currently only documented for Windows. TODO: Linux and macOS.

```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

# Running the script

The first example captures webcam 0, posts the data to the server as _my-unique-id_, and shows the capture preview
window. Once you have selected the right webcam you can run it again without debug.

The id you provide can be anything. Think of it like a password that identifies your data.

```
python main.py 0 my-unique-id debug
python main.py 0 my-unique-id
```

# Using the data

There are two ways to use the OCR data:

1. Use the score browser with the machine in the URL: https://smx.573.no/browser?machine=my-unique-id
   If you set the browser to auto refresh it will change songs as you navigate the song selection wheel.
   Maybe add some filters and use it as a browser source for your stream?
2. Use the data in your own application with the API: https://smx.573.no/api/machines/my-unique-id
