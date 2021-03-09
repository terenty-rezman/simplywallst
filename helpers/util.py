import datetime

def timestamp_print(*args, **kwargs):
    timestamp = "[{}]".format(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    print(timestamp, *args, **kwargs)

def n_at_a_time(n, iterable):
    """returns list with max of `n` elements at a time from iterable."""
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


# taken from https://gist.github.com/dhrrgn/7255361
def human_delta(tdelta):
    """
    Takes a timedelta object and formats it for humans.
    """
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['days'] == 0:
        fmt = '{hrs:02d}:{min:02d}:{sec:02d}'
    else:
        fmt = '{days} day(s), {hrs:02d}:{min:02d}:{sec:02d}'

    return fmt.format(**d)


def safe_parse_int(num:str):
    try:
        return int(num)
    except ValueError:
        return None