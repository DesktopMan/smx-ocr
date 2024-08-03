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

Note: The tool must be run from Command Prompt or similar.

1. Download latest tool [release](https://github.com/DesktopMan/smx-ocr/releases)
2. Open a _Command Prompt_ and navigate to the directory with the tool using _cd_
3. Run the tool with the preview window to find the right webcam id (0 or 1 or 2 ...):  
   `smx-ocr 0 my-unique-id debug`
4. Run the tool without the preview window:  
   `smx-ocr 0 my-unique-id`

These examples will post the OCR data to the server as _my-unique-id_. The id you provide can be anything. Think of it
like a password that identifies your data.

# Using the data

There are three ways to use the OCR data:

1. Use the score browser with the machine in the URL:
    * https://smx.573.no/browser?machine=my-unique-id
    * The browser will auto refresh and change songs as you navigate the song selection wheel.
    * You can use this URL as a browser source in OBS for overlays.

2. Use the data in your own application with the API:
    * https://smx.573.no/api/machines/my-unique-id
    * Click the link to see example data
    * TODO: Web socket support for this API endpoint

3. Read the file data.json:
    * File is updated when the OCR data changes
    * Same format as the API output, see above
