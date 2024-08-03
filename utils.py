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
