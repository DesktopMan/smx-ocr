import os
import PIL.ImageOps as ImageOps
import statistics

from cdifflib import CSequenceMatcher
from tesserocr import PyTessBaseAPI, PSM

import utils

api = None


# Find text matches in given area, based on valid values
def ocr_match(frame, rect, values=None, mirror=False, invert=True, threshold=None, min_length=0):
    global api

    if api is None:
        api = PyTessBaseAPI(psm=PSM.SINGLE_BLOCK, path=os.path.expanduser('~/.tessdata'))

    rect = utils.mirror_rect(rect) if mirror else rect

    best_ratio = 0
    best_text = None

    image = frame.crop(rect)
    image = ImageOps.invert(image) if invert else image
    image = image.point(lambda p: 255 if p > threshold else 0) if threshold else image

    api.SetImage(image)
    text = api.GetUTF8Text().strip()
    confidences = api.AllWordConfidences()

    if len(text) < min_length or not confidences or statistics.mean(confidences) < 50:
        return None

    if not values:
        return text if text else None

    for value in values:
        ratio = CSequenceMatcher(None, text.lower(), value.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_text = value

        if best_ratio == 1:
            break

    if best_ratio > 0.7 and best_text:
        return best_text

    return None
