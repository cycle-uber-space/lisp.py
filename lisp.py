#!/usr/bin/env python3
import sys

py_print = print
py_eval = eval
py_list = list
py_type = type
py_repr = repr

class Nil:
    def __iter__(self):
        return ListIter(self)
    def __repr__(self):
        return "nil"
    def __len__(self):
        return 0

nil = Nil()

def is_nil(exp):
    return isinstance(exp, Nil)

def make_error(text):
    raise Exception(text)

def unit_test():
    assert is_nil(nil)

def main(argc, argv):
    if argc < 2:
        make_error("missing command")
    cmd = argv[1]
    if cmd == "unit":
        unit_test()

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
