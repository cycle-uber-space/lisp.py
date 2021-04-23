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

class Symbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

def is_symbol(exp):
    return isinstance(exp, Symbol)

def make_symbol(name):
    return Symbol(name)

def symbol_name(exp):
    return exp.name

def intern(name):
    if name == "nil":
        return nil
    else:
        return make_symbol(name)

def eq(a, b):
    if py_type(a) == py_type(b):
        if is_symbol(a):
            return symbol_name(a) == symbol_name(b)
        else:
            return a == b
    else:
        return a == b

def equal(a, b):
    return eq(a, b)

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
