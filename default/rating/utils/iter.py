import itertools


def chunks(seq, size):
    i = iter(seq)
    return iter(lambda: tuple(itertools.islice(i, size)), ())


def first(predicate, iterable):
    for x in iterable:
        if predicate(x):
            return x


def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result