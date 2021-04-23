#!/usr/bin/env python3
import sys, re, doctest

#
# util
#

py_print = print
py_eval = eval
py_list = list
py_type = type
py_repr = repr

def make_error(text):
    raise Exception(text)

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

#
# nil
#

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

#
# symbol
#

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

#
# cons
#

class Cons:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        return ListIter(self)
    def __repr__(self):
        return "(" + py_repr(self.a) + " . " + py_repr(self.b) + ")"
    def __len__(self):
        ret = 0
        tmp = self
        while not is_nil(tmp):
            ret += 1
            tmp = cdr(tmp)
        return ret

def is_cons(exp):
    return isinstance(exp, Cons)

def cons(a, b):
    return Cons(a, b)

def car(exp):
    """
>>> car(cons(intern("foo"), intern("bar")))
foo
"""
    if not is_cons(exp):
        return make_error(format("not a cons {}", repr_expr(exp)))
    return exp.a

def cdr(exp):
    """
>>> cdr(cons(intern("foo"), intern("bar")))
bar
"""
    if not is_cons(exp):
        return make_error(format("not a cons {}", repr_expr(exp)))
    return exp.b

def set_car(exp, val):
    exp.a = val

def set_cdr(exp, val):
    exp.b = val

#
# core
#

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

#
# stream
#

class StringInputStream:
    def __init__(self, src):
        self.src = src
        self.pos = 0

    def peek(self):
        if self.pos < len(self.src):
            return self.src[self.pos]
        else:
            return 0

    def advance(self):
        self.pos += 1

    def consume(self):
        ret = self.peek()
        self.advance()
        return ret

    def at_end(self):
        return self.peek() == 0

def make_string_input_stream(src):
    return StringInputStream(src)

def peek(stream):
    return stream.peek()

def advance(stream):
    stream.advance()

def consume(stream):
    return stream.consume()

def at_end(stream):
    return stream.at_end()

#
# comment
#

class Comment:
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return repr(self.text)

def make_comment(text):
    return Comment(text)

def is_comment(exp):
    return isinstance(exp, Comment)

def comment_text(exp):
    return exp.text

#
# reader
#

def read_one_from_string(src, comments = False):
    """
>>> read_one_from_string("nil")
nil
>>> read_one_from_string("foo")
foo
>>> read_one_from_string("(defun add (a b) (+ a b))") # TODO use printer
(defun . (add . ((a . (b . nil)) . ((+ . (a . (b . nil))) . nil))))
"""
    stream = make_string_input_stream(src)
    return parse_expr(stream, comments)

def parse_expr(stream, comments = False):
    lexeme = ""
    skip_junk(stream, not comments)
    if comments and peek(stream) == ";":
        while peek(stream) and peek(stream) != "\n":
            lexeme += consume(stream)
        if peek(stream):
            advance(stream)
        return Comment(lexeme)

    elif peek(stream) == "(":
        return parse_list(stream, comments)

    elif is_symbol_start(peek(stream)):
        while is_symbol_part(peek(stream)):
            lexeme += consume(stream)

        if re.match("^-?[0-9]+$", lexeme):
            return int(lexeme)

        return intern(lexeme)

    else:
        return make_error("unexpected '" + str(peek(stream)) + "'")

def parse_list(stream, comments = False):
    if peek(stream) != "(":
        return make_error()
    advance(stream)
    head = tail = nil
    while True:
        skip_junk(stream)
        if peek(stream) == 0:
            return make_error("unexpected end of stream while parsing list")
        if peek(stream) == ")":
            break
        exp = parse_expr(stream, comments)
        if eq(exp, intern(".")):
            exp = parse_expr(stream, comments)
            set_cdr(tail, exp)
            skip_junk(stream)
            break
        else:
            next = cons(exp, nil)
            if is_nil(tail):
                head = tail = next
            else:
                set_cdr(tail, next)
                tail = next
    if peek(stream) != ")":
        return make_error("missing closing ')'")
    advance(stream)
    return head

def skip_junk(stream, comments = True):
    while skip_ws(stream) or comments and skip_comment(stream):
        pass

def skip_ws(stream):
    if is_ws(peek(stream)):
        while is_ws(peek(stream)):
            advance(stream)
        return True

def skip_comment(stream):
    if is_comment_start(peek(stream)):
        advance(stream)
        while is_comment_part(peek(stream)):
            advance(stream)
        return True

def is_ws(ch):
    return ch and ch in " \n\t"

def is_comment_start(ch):
    return ch == ";"

def is_comment_part(ch):
    return ch and ch != "\n"

def is_symbol_start(ch):
    return ch and not is_ws(ch) and ch not in "\"();'"

def is_symbol_part(ch):
    return is_symbol_start(ch)

#
# main
#

def main(argc, argv):
    if argc < 2:
        make_error("missing command")
    cmd = argv[1]
    if cmd == "unit":
        doctest.testmod()

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
