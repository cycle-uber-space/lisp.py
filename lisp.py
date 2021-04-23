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

def main(argc, argv):
    pass

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
