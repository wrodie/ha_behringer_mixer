def fader_to_db(retval):
    if retval >= 1:
        return 10
    elif retval >= 0.5:
        return round((40 * retval) - 30, 1)
    elif retval >= 0.25:
        return round((80 * retval) - 50, 1)
    elif retval >= 0.0625:
        return round((160 * retval) - 70, 1)
    elif retval >= 0:
        return round((480 * retval) - 90, 1)
    else:
        return -90


def db_to_fader(val):
    if val >= 10:
        return 1
    elif val >= -10:
        return (val + 30) / 40
    elif val >= -30:
        return (val + 50) / 80
    elif val >= -60:
        return (val + 70) / 160
    elif val >= -90:
        return (val + 90) / 480
    return 0
