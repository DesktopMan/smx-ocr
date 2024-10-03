# About

This tool is for the arcade game StepManiaX. It uses OCR to identify:

* Which screen the game is on
* Currently selected song, difficulty and logged-in users on the select song screen
* Current song being played in the gameplay screen

# OBS setup

This tool requires a clean gameplay feed at >= 1080p. You can send this feed from OBS using the virtual camera. Set the
OBS virtual camera to output your capture source directly, that way it will work even if you change scenes in OBS.

1. Make sure _Settings -> Video ->_ _Base_ and _Output_ resolution is set to 1920x1080 or higher
2. Click the cogwheel next to "Start Virtual Camera"
3. Set _Output Type_ to _Source_
4. Select your capture device from the list
5. Click _Start Virtual Camera_

# Running the tool

First download latest tool [release](https://github.com/DesktopMan/smx-ocr/releases).

Both the two options below require you to come up with a data identifier. The identifier you provide can be anything.
Think of it like a password that identifies your OCR data for access in the browser or API.

## Option one - run the exe

Running the exe directly will open a window where the tool asks you which webcamera number to use and what your data
identifier should be. It will then open a preview window of the webcam. If it's not the right webcam just close the
window and try again with the next webcam number.

Example:

```
Enter webcam number: 4
Enter data identifier: my-unique-id
Enter Capture method. 1=ffmpeg (recommended), 2=OpenCV (older hw): 1
```

##  Option two - run from command line or script

The tool will run non-interactively if you give it the right parameters. This is useful if you want to start it without
typing in the answers every time.

`smx-ocr 0 my-unique-id`

If you put the command with parameters in a .bat file you can double-click it to run it, or have it run on startup.

# Using the data

There are three ways to use the OCR data:

1. Use the score browser with the machine in the URL:
    * https://smx.573.no/browser?machine=my-unique-id
    * The browser will auto refresh and change songs as you navigate the song selection wheel
    * Add additional filters in the browser, e.g. user and difficulty, as needed
    * You can use this URL as a browser source in OBS for overlays

2. Use the data in your own application with the API:
    * https://smx.573.no/api/machines/my-unique-id
    * Click the link to see example data
    * This endpoint supports websockets

3. Read the file data.json:
    * File is updated when the OCR data changes
    * Same format as the API output without user details, see above
