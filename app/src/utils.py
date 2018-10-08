import os


def avail_subclasses(clz):
    return [x.__name__ for x in clz.__subclasses__()]


def allowed_files(fname, allowed_list):
    return os.path.splitext(fname)[-1] in allowed_list