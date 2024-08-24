import aiohttp
import asyncio
import cv2
import os
import imageio.v3 as iio
import json
import shutil
import signal
import sys
import tempfile
import threading
import time
import zipfile

from PIL import Image
from datetime import datetime, date
from dotmap import DotMap

import utils

from constants import *
from ocr import ocr_match

BROWSER_URL = 'https://smx.573.no/browser'
API_URL = 'https://smx.573.no/api'

running = True


class LatestFrame(threading.Thread):
    def __init__(self, index, method):
        self.index = int(index)
        self.method = method
        self.frame = None
        super().__init__()
        # Start thread
        self.start()

    def run(self):
        global running

        if self.method == 1:
            print('Reading frames using ffmpeg...')
            for index, self.frame in enumerate(iio.imiter(f'<video{self.index}>')):
                if not running:
                    return

                time.sleep(0.1)

        if self.method == 2:
            print('Opening OpenCV device...')
            cap = cv2.VideoCapture(self.index)

            print('Setting capture properties...')
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            print('Reading frames using OpenCV...')
            while running:
                _, self.frame = cap.read()


async def main():
    global running

    camera_index = 0
    debug = len(sys.argv) == 4 and sys.argv[3] == 'debug'
    method = 1

    if len(sys.argv) == 1:
        print('-------------------')
        print('StepManiaX OCR tool')
        print('-------------------', end='\n\n')

        camera_index = input('Enter webcam number: ')
        identifier = input('Enter data identifier: ')
        method = int(input('Enter Capture method. 1=ffmpeg (recommended), 2=OpenCV (older hw): '))
        debug = False
    elif len(sys.argv) in [3, 4]:
        camera_index = sys.argv[1]
        identifier = sys.argv[2]
    else:
        print('Usage  : python main.py <webcam> <identifier> [debug]')
        print('Example: python main.py 0 example-01')
        sys.exit(0)

    print(f'Your browser URL is: {BROWSER_URL}?machine={identifier}')
    print(f'Your data URL is: {API_URL}/machines/{identifier}')

    print('Starting frame capture...')
    latest_frame = LatestFrame(camera_index, method)
    time.sleep(3)

    if latest_frame.frame is None:
        print('Failed to capture first frame.')
        return

    print('Got first frame from capture device.')

    frame = cv2.cvtColor(latest_frame.frame, cv2.COLOR_BGR2RGB) if method == 2 else latest_frame.frame
    image = Image.fromarray(frame)

    print('Saving preview image to preview.png...')
    image.save('preview.png')
    image.show()

    if image.size[0] < 1920 or image.size[1] < 1080:
        print('Resolutions lower than 1920x1080 are not supported due to bad OCR performance.')
        print('Adjust your OBS output resolution and try again.')
        return

    if image.size[0] > 1920 or image.size[1] > 1080:
        print('Resolutions higher than 1920x1080 will be scaled down before performing OCR.')
        print('This might affect performance slightly.')

    session = aiohttp.ClientSession()

    if os.path.isdir('.tessdata'):
        shutil.move('.tessdata', os.path.expanduser('~/.tessdata'))

    if not os.path.isdir(os.path.expanduser('~/.tessdata')):
        print('OCR data not found, downloading approximately 1 GB:')

        with tempfile.TemporaryFile() as f:
            await utils.download_file(session, URL_OCR_DATA, f)

            print('OCR data downloaded. Extracting...')

            with zipfile.ZipFile(f) as z:
                z.extractall()
                shutil.move('tessdata-4.1.0', os.path.expanduser('~/.tessdata'))

            print('Done.')

    async with session.get(f'{API_URL}/songs') as res:
        songs = await res.json()
        short_titles = [utils.get_short_title(song) for song in songs]
        long_titles = [utils.get_long_title(song) for song in songs]

    data = DotMap({
        'screen': None,
        'song': None,
        'players': [
            {'difficulty': None, 'username': None},
            {'difficulty': None, 'username': None}
        ],
        'visible': False,
    })

    old_data = None

    while running:
        frame = cv2.cvtColor(latest_frame.frame, cv2.COLOR_BGR2RGB) if method == 2 else latest_frame.frame
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        if debug:
            cv2.imshow('Capture Preview', frame)
            cv2.waitKey(1)

        image = Image.fromarray(frame)

        if image.size[0] != 1920 or image.size[1] != 1080:
            image = image.resize((1920, 1080))

        song_title = None

        # Try to match screen by screen title
        screen = ocr_match(image, RECT_SCREEN_TITLE, TEXT_SCREEN_TITLES, threshold=175)

        # Try to match screen by song title
        if not screen:
            song_title = ocr_match(image, RECT_GAMEPLAY_SONG_TITLE, short_titles)
            if song_title:
                screen = 'GAMEPLAY'

        if screen == 'SELECT SONG':
            song_title = ocr_match(image, RECT_SELECT_SONG_SONG_TITLE, long_titles)

            for p, m in [(0, False), (1, True)]:
                difficulty = ocr_match(image, RECT_SELECT_SONG_DIFFICULTY, TEXT_DIFFICULTIES, mirror=m, invert=False)
                data.players[p].difficulty = difficulty.lower() if difficulty else None
                data.players[p].username = ocr_match(image, RECT_SELECT_SONG_PLAYER, mirror=m)

        data.screen = screen if screen else data.screen
        data.song = utils.get_song(song_title, songs) if song_title else data.song
        data.visible = True if screen else False

        data_dict = data.toDict()

        if data_dict != old_data:
            print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {data_dict}')

            old_data = data_dict

            try:
                with open('data.json', 'w') as f:
                    f.write(json.dumps(data_dict, indent=2))

                await session.post(f'{API_URL}/machines/{identifier}', json=data_dict)
            except Exception as e:
                print(f'Failed to post data to API. Network issues? Message: {e}')

    await session.close()


def signal_handler(sig, frame):
    global running
    print('Exiting.')
    running = False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
