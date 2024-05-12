import numpy

from skimage.metrics import structural_similarity

import utils


def similarity_match(frame, patterns, threshold, mirror=False):
    best_pattern = None
    best_image = None
    best_score = 0

    for pattern in patterns:
        rect = pattern.rect if not mirror else utils.mirror_rect(pattern.rect)
        haystack = frame.crop(rect)

        for image in pattern.images:
            score = structural_similarity(numpy.array(haystack), image.data)

            if score > best_score:
                best_pattern = pattern
                best_score = score
                best_image = image

    if best_score >= threshold:
        return best_pattern, best_image, best_score

    return None, None, None
