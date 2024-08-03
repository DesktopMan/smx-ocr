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
    async with session.get(url) as res:
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


def mirror_rect(rect):
    rect = list(rect)

    x = rect[0]
    width = rect[2] - rect[0]

    rect[0] += 1920 - 2 * rect[0] - width
    rect[2] = rect[0] + width

    rect[0] -= 2
    rect[2] -= 2

    return tuple(rect)
