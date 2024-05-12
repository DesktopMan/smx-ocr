def mirror_rect(rect):
    rect = list(rect)

    x = rect[0]
    width = rect[2] - rect[0]

    rect[0] += 1920 - 2 * rect[0] - width
    rect[2] = rect[0] + width

    rect[0] -= 2
    rect[2] -= 2

    return tuple(rect)
