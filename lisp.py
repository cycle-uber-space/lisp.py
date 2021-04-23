#!/usr/bin/env python3
import sys, doctest

py_print = print
py_eval = eval
py_list = list
py_type = type
py_repr = repr

def join(s, l):
    return s.join(l)

def strip(s):
    return s.strip()

def split(s, *args):
    return s.split(*args)

def format(s, *args):
    return s.format(*args)

def escape(text, sep):
    """
>>> escape("foo", "\\"")
'"foo"'
>>> escape("foo", "'")
"'foo'"
"""
    ret = ""
    ret += sep
    for ch in text:
        if ch == sep or ch == "\\":
            ret += "\\"
            ret += ch
        elif ch == "\n":
            ret += "\\n"
        elif ch == "\t":
            ret += "\\t"
        elif ch == chr(0x1b):
            ret += format("\\x{:02x}", ord(ch))
        else:
            ret += ch
    ret += sep
    return ret

class Nil:
    def __iter__(self):
        return ListIter(self)
    def __repr__(self):
        return "nil"
    def __len__(self):
        return 0

nil = Nil()

def is_nil(exp):
    """
>>> is_nil(nil)
True
"""
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
    """
>>> eq(nil, nil)
True
>>> eq(nil, intern("nil"))
True
>>> eq(nil, intern("foo"))
False
"""
    if py_type(a) == py_type(b):
        if is_symbol(a):
            return symbol_name(a) == symbol_name(b)
        else:
            return a == b
    else:
        return a == b

def equal(a, b):
    """
>>> equal(nil, nil)
True
"""
    return eq(a, b)

def make_error(text):
    raise Exception(text)

def main(argc, argv):
    if argc < 2:
        make_error("missing command")
    cmd = argv[1]
    if cmd == "unit":
        doctest.testmod()

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
