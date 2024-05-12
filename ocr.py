import PIL.ImageOps as ImageOps
import statistics

from cdifflib import CSequenceMatcher
from tesserocr import PyTessBaseAPI, PSM

import utils


# Find text matches in given area, based on valid values
def ocr_match(frame, rect, values=None, mirror=False, threshold=175, invert=False):
    rect = utils.mirror_rect(rect) if mirror else rect

    best_ratio = 0
    best_text = None

    image = frame.crop(rect)
    image = ImageOps.invert(image) if invert else image
    image = image.point(lambda p: 255 if p > threshold else 0)

    with PyTessBaseAPI(psm=PSM.SINGLE_BLOCK) as api:
        api.SetImage(image)
        text = api.GetUTF8Text().strip()
        confidences = api.AllWordConfidences()

    if not confidences or statistics.mean(confidences) < 50:
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
