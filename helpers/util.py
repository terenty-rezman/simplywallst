import datetime

def timestamp_print(*args, **kwargs):
    timestamp = "[{}]".format(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    print(timestamp, *args, **kwargs)

def n_at_a_time(n, iterable):
    """returns list with max of `n` elements at a time."""
    exhausted = False
    while not exhausted:
        n_items = []
        for i in range(n):
            try:
                n_items.append(next(iterable))
            except StopIteration:
                exhausted = True
        if n_items:
            yield n_items
    return

    return zip_varlen(*stepped_slices)


# taken from https://gist.github.com/dhrrgn/7255361
def human_delta(tdelta):
    """
    Takes a timedelta object and formats it for humans.
    Usage:
        # 149 day(s) 8 hr(s) 36 min 19 sec
        print human_delta(datetime(2014, 3, 30) - datetime.now())
    Example Results:
        23 sec
        12 min 45 sec
        1 hr(s) 11 min 2 sec
        3 day(s) 13 hr(s) 56 min 34 sec
    :param tdelta: The timedelta object.
    :return: The human formatted timedelta
    """
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['days'] == 0:
        fmt = '{hrs:02d}:{min:02d}:{sec:02d}'
    else:
        fmt = '{days} day(s), {hrs:02d}:{min:02d}:{sec:02d}'

    return fmt.format(**d)
