import aiohttp
import asyncio
import cv2
import signal
import sys
import threading
import time

from PIL import Image
from datetime import datetime, date
from dotmap import DotMap

from constants import *
from ocr import ocr_match

BROWSER_URL = 'https://smx.573.no/browser'
API_URL = 'https://smx.573.no/api'

running = True


class LatestFrame(threading.Thread):
    def __init__(self, index):
        self.index = int(index)
        self.frame = None
        super().__init__()
        # Start thread
        self.start()

    def run(self):
        global running

        cap = cv2.VideoCapture(self.index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        while running:
            ret, self.frame = cap.read()

            if not ret:
                raise Exception(f'OpenCV failed to read frame')


def get_short_title(song):
    return f"{song['title']} - {song['artist']}"


def get_long_title(song):
    return f"{song['title']}\n{song['subtitle']}\n{song['artist']}" if song['subtitle'] \
        else f"{song['title']}\n{song['artist']}"


def get_song(full_title, songs):
    for song in songs:
        if full_title == get_short_title(song) or full_title == get_long_title(song):
            return song


def json_serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


async def main():
    global running

    session = aiohttp.ClientSession()

    async with session.get(f'{API_URL}/songs') as res:
        songs = await res.json()
        short_titles = [get_short_title(song) for song in songs]
        long_titles = [get_long_title(song) for song in songs]

    latest_frame = LatestFrame(sys.argv[1])
    time.sleep(1)

    if latest_frame.frame is None:
        return

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
        frame = cv2.cvtColor(latest_frame.frame, cv2.COLOR_BGR2GRAY)

        if len(sys.argv) == 4 and sys.argv[3] == 'debug':
            cv2.imshow('Capture Preview', frame)
            cv2.waitKey(1)

        image = Image.fromarray(frame)

        song_title = None

        # Try to match screen by screen title
        screen = ocr_match(image, RECT_SCREEN_TITLE, TEXT_SCREEN_TITLES)

        # Try to match screen by song title
        if not screen:
            song_title = ocr_match(image, RECT_GAMEPLAY_SONG_TITLE, short_titles)
            if song_title:
                screen = 'GAMEPLAY'

        if screen == 'SELECT SONG':
            song_title = ocr_match(image, RECT_SELECT_SONG_SONG_TITLE, long_titles)

            for p, m in [(0, False), (1, True)]:
                data.players[p].difficulty = ocr_match(
                    image, RECT_SELECT_SONG_DIFFICULTY, TEXT_DIFFICULTIES, mirror=m, threshold=220, invert=True).lower()
                data.players[p].username = ocr_match(image, RECT_SELECT_SONG_PLAYER, mirror=m)

        data.screen = screen if screen else data.screen
        data.song = get_song(song_title, songs) if song_title else data.song
        data.visible = True if screen else False

        data_dict = data.toDict()

        if data_dict != old_data:
            print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {data_dict}')

            old_data = data_dict

            try:
                await session.post(f'{API_URL}/machines/{sys.argv[2]}', json=data_dict)
            except Exception as e:
                print(f'Failed to post data to API. Network issues? Message: {e}')

    await session.close()


def signal_handler(sig, frame):
    global running
    print('Exiting.')
    running = False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) not in [3, 4]:
        print('Usage  : python main.py <webcam> <identifier> [debug]')
        print('Example: python main.py 0 example-01')
        sys.exit(0)

    print(f'Your browser URL is: {BROWSER_URL}?machine={sys.argv[2]}')
    print(f'Your data URL is: {API_URL}/machines/{sys.argv[2]}')
    asyncio.run(main())
