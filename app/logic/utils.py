import itertools


def dict_cross_product(atosetb):
    """Takes a dictionary mapping values of type a to sets of values of type b
    (think of it as having buckets of bs labeled with as) and return an iterable
    of dicts representing all possible combinations of choosing one element out
    of each bucket.
    """
    bucket_contents = (
            frozenset((a,b) for b in bs)
            for a,bs in atosetb.items())
    return map(dict, itertools.product(*bucket_contents))


def __dict_cross_product(possible_paths):
    dcp = dict_cross_product(possible_paths)
    return set(map(lambda d: frozenset().union(*d.values()), dcp))
