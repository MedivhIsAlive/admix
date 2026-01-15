def flatten(args):
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            yield from flatten(arg)
        else:
            yield arg

