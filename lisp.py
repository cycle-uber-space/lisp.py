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

def caar(exp):
    return car(car(exp))

def cadr(exp):
    return car(cdr(exp))

def cdar(exp):
    return cdr(car(exp))

def cddr(exp):
    return cdr(cdr(exp))

def caadr(exp):
    return car(car(cdr(exp)))

def caddr(exp):
    return car(cdr(cdr(exp)))

def cdddr(exp):
    return cdr(cdr(cdr(exp)))

def cadddr(exp):
    return car(cdr(cdr(cdr(exp))))

def cddddr(exp):
    return cdr(cdr(cdr(cdr(exp))))

#
# list
#

class ListIter:
    def __init__(self, x):
        self.x = x
    def __next__(self):
        if is_nil(self.x):
            raise(StopIteration)
        ret = car(self.x)
        self.x = cdr(self.x)
        return ret

def make_list(*args):
    ret = nil
    for arg in reversed(args):
        ret = cons(arg, ret)
    return ret

def nreverse(list):
    if is_nil(list):
        return list
    prev = nil
    expr = list
    while is_cons(expr):
        next = cdr(expr)
        set_cdr(expr, prev)
        prev = expr
        expr = next
    if not is_nil(expr):
        iter = prev
        while not is_nil(cdr(iter)):
            next = car(iter)
            set_car(iter, expr)
            expr = next
        next = car(iter)
        set_car(iter, expr)
        set_cdr(iter, next)
    return prev

#
# gensym
#

class Gensym:
    counter = 0
    def __init__(self):
        self.id = Gensym.counter
        Gensym.counter += 1
    def __repr__(self):
        return format("#:G{}", self.id)

def is_gensym(exp):
    return isinstance(exp, Gensym)

def gensym():
    """
>>> eq(gensym(), gensym())
False
"""
    return Gensym()

def gensym_id(exp):
    return exp.id

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
# core
#

def make_bool(x):
    if x:
        return intern("t")
    else:
        return nil

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
        elif is_gensym(a):
            return gensym_id(a) == gensym_id(b)
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

class StringOutputStream:
    def __init__(self):
        self.value = ""
    def put_string(self, text):
        self.value += text

def make_string_output_stream():
    return StringOutputStream()

def put_string(out, val):
    if out is None:
        print(val, end = "")
    else:
        out.put_string(val)

def put_int(out, val):
    put_string(out, format("{}", val))

#
# printer
#

class PrinterOpts:
    def __init__(self, out):
        self.out = out
        self.pretty = False

def repr_expr(exp):
    """
>>> repr_expr(nil)
'nil'
>>> repr_expr(intern("foo"))
'foo'
>>> repr_expr(cons(intern("foo"), nil))
'(foo)'
>>> repr_expr(cons(intern("foo"), intern("bar")))
'(foo . bar)'
"""
    out = StringOutputStream()
    opts = PrinterOpts(out)
    render_expr(exp, opts)
    return out.value

def render_expr(exp, opts):
    out = opts.out
    if is_nil(exp):
        put_string(out, "nil")
    elif is_symbol(exp):
        put_string(out, symbol_name(exp))
    elif is_gensym(exp):
        put_string(out, "#:G")
        put_int(out, gensym_id(exp))
    elif is_cons(exp):
        render_list(exp, opts)
    else:
        make_error("cannot print " + str(exp))

def render_list(exp, opts):
    out = opts.out
    put_string(out, "(")
    # TODO need to keep a visited set for recursive structures
    render_expr(car(exp), opts)
    tmp = cdr(exp)
    while not is_nil(tmp):
        if is_cons(tmp):
            put_string(out, " ")
            render_expr(car(tmp), opts)
        else:
            put_string(out, " . ")
            render_expr(tmp, opts)
            break
        tmp = cdr(tmp)
    put_string(out, ")")

#
# reader
#

class ReaderOpts:
    def __init__(self):
        self.read_comments = False
        self.read_quote    = True

def read_one_from_string(src, opts=ReaderOpts()):
    """
>>> repr_expr(read_one_from_string("nil"))
'nil'
>>> repr_expr(read_one_from_string("foo"))
'foo'
>>> repr_expr(read_one_from_string("(defun add (a b) (+ a b))"))
'(defun add (a b) (+ a b))'
>>> repr_expr(read_one_from_string("(foo . bar)"))
'(foo . bar)'
>>> repr_expr(read_one_from_string("(foo . nil)"))
'(foo)'
>>> repr_expr(read_one_from_string("(foo)"))
'(foo)'
>>> repr_expr(read_one_from_string("'foo"))
'(quote foo)'
"""
    stream = make_string_input_stream(src)
    return parse_expr(stream, opts)

def parse_expr(stream, opts):
    lexeme = ""
    skip_junk(stream, opts)
    if opts.read_comments and peek(stream) == ";":
        while peek(stream) and peek(stream) != "\n":
            lexeme += consume(stream)
        if peek(stream):
            advance(stream)
        return Comment(lexeme)

    elif peek(stream) == "(":
        return parse_list(stream, opts)

    elif opts.read_quote and peek(stream) == "'":
        advance(stream)
        return cons(intern("quote"), cons(parse_expr(stream, opts), nil))

    elif is_symbol_start(peek(stream)):
        while is_symbol_part(peek(stream)):
            lexeme += consume(stream)

        if re.match("^-?[0-9]+$", lexeme):
            return int(lexeme)

        return intern(lexeme)

    else:
        return make_error("unexpected '" + str(peek(stream)) + "'")

def parse_list(stream, opts):
    if peek(stream) != "(":
        return make_error()
    advance(stream)
    head = tail = nil
    while True:
        skip_junk(stream, opts)
        if peek(stream) == 0:
            return make_error("unexpected end of stream while parsing list")
        if peek(stream) == ")":
            break
        exp = parse_expr(stream, opts)
        if eq(exp, intern(".")):
            exp = parse_expr(stream, opts)
            set_cdr(tail, exp)
            skip_junk(stream, opts)
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

def skip_junk(stream, opts):
    while skip_ws(stream) or not opts.read_comments and skip_comment(stream):
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
# env
#

def make_env(outer):
    return cons(cons(nil, nil), outer)

def env_vars(env):
    return caar(env)

def env_vals(env):
    return cdar(env)

def env_outer(env):
    return cdr(env)

def env_push(env, var, val):
    pair = car(env)
    set_car(pair, cons(var, car(pair)))
    set_cdr(pair, cons(val, cdr(pair)))

def env_find_local(env, var):
    pair = car(env)
    vars = car(pair)
    vals = cdr(pair)
    while not is_nil(vars):
        if eq(car(vars), var):
            return vals
        vars = cdr(vars)
        vals = cdr(vals)
    return nil

def env_find_global(env, var):
    while not is_nil(env):
        iter = env_find_local(env, var)
        if is_nil(iter):
            env = env_outer(env)
        else:
            return iter
    return nil

def env_def(env, var, val):
    vals = env_find_local(env, var)
    if is_nil(vals):
        env_push(env, var, val)
    else:
        set_car(vals, val)

def env_del(env, var):
    pair = car(env)
    vars = car(pair)
    vals = cdr(pair)
    prev_vars = nil
    prev_vals = nil
    while not is_nil(vars):
        if eq(car(vars), var):
            if is_nil(prev_vars):
                set_car(pair, cdr(vars))
                set_cdr(pair, cdr(vals))
            else:
                set_cdr(prev_vars, cdr(vars))
                set_cdr(prev_vals, cdr(vals))
            return
        prev_vars = vars
        prev_vals = vals
        vars = cdr(vars)
        vals = cdr(vals)
    make_error("cannot remove variable " + repr_expr(var))

def env_set(env, var, val):
    vals = env_find_global(env, var)
    if is_nil(vals):
        make_error("unbound variable " + repr_expr(var))
    else:
        set_car(vals, val)

def env_get(env, var):
    iter = env_find_global(env, var)
    if is_nil(iter):
        return make_error("unbound variable " + repr_expr(var))
    else:
        return car(iter)

def env_dbind(env, vars, vals):
    if is_nil(vars):
        return
    while is_cons(vars):
        var = car(vars)
        val = car(vals)
        env_dbind(env, var, val)
        vars = cdr(vars)
        vals = cdr(vals)
    if not is_nil(vars):
        env_def(env, vars, vals)

#
# builtin
#

g_builtin_tag = gensym()

def is_builtin(exp):
    return is_op(exp, g_builtin_tag)

def make_builtin(fun):
    return make_list(g_builtin_tag, fun)

def builtin_fun(exp):
    return cadr(exp)

def builtin_eq(a, b):
    return make_bool(eq(a, b))

#
# function
#

g_function_tag = gensym()

def make_function(env, args, body):
    # TODO macros have essentially the same structure
    return cons(cons(g_function_tag, env), cons(args, body))

def is_function(exp):
    return is_cons(exp) and is_cons(car(exp)) and eq(caar(exp), g_function_tag)

def function_env(exp):
    return cdar(exp)

def function_args(exp):
    return cadr(exp)

def function_body(exp):
    return cddr(exp)

#
# interpreter
#

def make_core_env():
    env = make_env(nil)
    env_def(env, intern("t"), intern("t"))
    env_def(env, intern("eq"), make_builtin(builtin_eq))
    env_def(env, intern("cons"), make_builtin(cons))
    env_def(env, intern("car"), make_builtin(car))
    env_def(env, intern("cdr"), make_builtin(cdr))
    return env

def is_op(exp, sym):
    return is_cons(exp) and eq(car(exp), sym)

def is_named_op(exp, *names):
    for name in names:
        if is_op(exp, intern(name)):
            return name
    return False

def eval(exp, env):
    if is_nil(exp):
        return exp
    elif is_symbol(exp) or is_gensym(exp):
        return env_get(env, exp)
    elif is_named_op(exp, "quote"):
        return cadr(exp)
    elif is_named_op(exp, "lit"):
        return exp
    elif is_named_op(exp, "if"):
        return eval_if(exp, env)
    elif is_cons(exp):
        return eval_cons(exp, env)
    else:
        return make_error("cannot eval " + repr_expr(exp))

def eval_list(exps, env):
    ret = nil
    for exp in exps:
        ret = cons(eval(exp, env), ret)
    return nreverse(ret)

def eval_body(body, env):
    ret = nil
    for stmt in body:
        ret = eval(stmt, env)
    return ret

def make_call_env(fenv, vars, vals, env):
    denv = fenv
    cenv = make_env(denv)
    env_dbind(cenv, vars, vals)
    return cenv

def eval_cons(exp, env):
    name = car(exp)
    args = cdr(exp)
    if is_builtin(name):
        vals = eval_list(args, env)
        fun = builtin_fun(name)
        return fun(*vals)
    elif is_function(name):
        body = function_body(name)
        fenv = function_env(name)
        vars = function_args(name)
        vals = eval_list(args, env)
        cenv = make_call_env(fenv, vars, vals, env)
        return eval_body(body, cenv)
    else:
        return eval(cons(eval(name, env), args), env)

def eval_if(exp, env):
    test = cadr(exp)
    then = caddr(exp)
    if not is_nil(eval(test, env)):
        return eval(then, env)
    if not is_nil(cdddr(exp)):
        return eval(cadddr(exp), env)
    return nil

def eval_src(src, env):
    """
>>> eval_src("nil", nil)
'nil'
>>> eval_src("'nil", nil)
'nil'

>>> eval_src("(quote foo)", nil)
'foo'
>>> eval_src("'foo", nil)
'foo'

>>> eval_src("(lit foo bar baz)", nil)
'(lit foo bar baz)'
>>> eval_src("(lit)", nil)
'(lit)'
>>> eval_src("(lit)", nil)
'(lit)'
>>> eval_src("(if 't 'a 'b)", nil)
'a'
>>> eval_src("(if nil 'a 'b)", nil)
'b'
>>> eval_src("(if nil 'a)", nil)
'nil'

>>> eval_src("t", make_core_env())
't'

>>> eval_src("(eq 'a 'b)", make_core_env())
'nil'
>>> eval_src("(eq 'a 'a)", make_core_env())
't'

>>> eval_src("(cons 'a 'b)", make_core_env())
'(a . b)'
>>> eval_src("(cons 'a nil)", make_core_env())
'(a)'

>>> eval_src("(car (cons 'a 'b))", make_core_env())
'a'
>>> eval_src("(cdr (cons 'a 'b))", make_core_env())
'b'
"""
    return repr_expr(eval(read_one_from_string(src), env))

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
