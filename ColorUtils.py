def transparent(col):
    return (col[0], col[1], col[2], 0)
def clamp(val, minimum=0, maximum=1):
    return min(max(val, minimum), maximum)