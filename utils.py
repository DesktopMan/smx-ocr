import aiohttp
import os
import shutil
import tempfile
import zipfile

from constants import URL_OCR_DATA

from datetime import date, datetime


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
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


async def download_file(session, url, file):
    async with session.get(url, ssl=False) as res:
        if res.status != 200:
            print('Failed to download OCR data. Try again?')
            return False

        chunk_num = 0

        while True:
            chunk = await res.content.readany()

            if not chunk:
                print()
                return True

            file.write(chunk)
            chunk_num += 1

            if chunk_num % 10 == 0:
                print('.', end='')

            if chunk_num % 1000 == 0:
                print()


async def check_ocr_data():
    if os.path.isdir('.tessdata'):
        shutil.move('.tessdata', os.path.expanduser('~/.tessdata'))

    if not os.path.isdir(os.path.expanduser('~/.tessdata')):
        print('OCR data not found, downloading approximately 1 GB:')

        session = aiohttp.ClientSession()

        with tempfile.TemporaryFile() as f:
            await download_file(session, URL_OCR_DATA, f)

            print('OCR data downloaded. Extracting...')

            with zipfile.ZipFile(f) as z:
                z.extractall()
                shutil.move('tessdata-4.1.0', os.path.expanduser('~/.tessdata'))

            print('Done.')

        await session.close()


def mirror_rect(rect):
    rect = list(rect)

    x = rect[0]
    width = rect[2] - rect[0]

    rect[0] += 1920 - 2 * rect[0] - width
    rect[2] = rect[0] + width

    rect[0] -= 2
    rect[2] -= 2

    return tuple(rect)
