hotkey_shape = [
    [1, 59, 60, 61],
    [70, 62, 63, 64],
    [69, 65, 66, 67],
    [42, 68, 87, 88]
]


def get_hotkey_location(code):
    row = 0

    while row < len(hotkey_shape):
        if code in hotkey_shape[row]:
            col = hotkey_shape[row].index(code)
            return [row, col]
        row += 1

    return -1
