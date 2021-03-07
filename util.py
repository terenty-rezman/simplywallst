import itertools

# taken from https://stackoverflow.com/questions/38054593/zip-longest-without-fillvalue
def _one_pass(iters):
    for it in iters:
        try:
            yield next(it)
        except StopIteration:
            pass # if some of them are already exhausted then ignore it.

def zip_varlen(*iterables):
    iters = [iter(it) for it in iterables]
    while True: #broken when an empty tuple is given by _one_pass
        val = tuple(_one_pass(iters))
        if val:
            yield val
        else:
            break

# taken from https://gist.github.com/pilcrow/8b6af7e35f5d19de7702d77446461b02
def natatime(n, iterable, fillvalue = None):
  """Returns an iterator yielding `n` elements at a time.
  :param n: the number of elements to return at each iteration
  :param iterable: the iterable over which to iterate
  :param fillvalue: the value to use for missing elements
  :Example:
  >>> for (a,b,c) in natatime(3, [1,2,3,4,5], fillvalue = "?"):
  ...   print a, b, c
  ...
  1 2 3
  4 5 ?
  """
  stepped_slices = ( itertools.islice(iterable, i, None, n) for i in range(n) )
  return itertools.zip_longest(*stepped_slices, fillvalue = fillvalue)

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

# for n_items in natatime(3, (x for x in range(10))):
#      print(*n_items)
# l = [0, 1, 2, 3]
# l = (x for x in range(0))