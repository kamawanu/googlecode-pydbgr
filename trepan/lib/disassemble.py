# -*- coding: utf-8 -*-
#   Modification of Python's Lib/dis.py
'''Disassembly Routines'''

import inspect, sys, types
from dis import distb, findlabels, findlinestarts
from opcode import cmp_op, hasconst, hascompare, hasfree, hasname, hasjrel, \
    haslocal, opname, EXTENDED_ARG, HAVE_ARGUMENT

from import_relative import import_relative
Mformat   = import_relative('lib.format', '...trepan')
format_token = Mformat.format_token

_have_code = (types.MethodType, types.FunctionType, types.CodeType, type)

def _try_compile(source, name):
    """Attempts to compile the given source, first as an expression and
       then as a statement if the first approach fails.

       Utility function to accept strings in functions that otherwise
       expect code objects
    """
    try:
        c = compile(source, name, 'eval')
    except SyntaxError:
        c = compile(source, name, 'exec')
    return c

# Modified from dis. Changed output to use msg, msg_nocr, section, and pygments.
# Added first_line and last_line parameters
def dis(msg, msg_nocr, section, errmsg, x=None, start_line=-1, end_line=None,
        relative_pos = False, color=True):
    """Disassemble classes, methods, functions, or code.

    With no argument, disassemble the last traceback.

    """
    lasti = -1
    if x is None:
        distb()
        return
    if type(x) is types.InstanceType:
        x = x.__class__
    if hasattr(x, 'im_func'):
        section("Disassembly of %s: " % x)
        x = x.im_func
    if hasattr(x, 'func_code'):
        section("Disassembly of %s: " % x)
        x = x.func_code
    elif hasattr(x, 'f_code'):
        section("Disassembly of %s: " % x)
        if hasattr(x, 'f_lasti'):
            lasti = x.f_lasti
            pass
        x = x.f_code
        pass
    elif inspect.iscode(x):
        pass
    if hasattr(x, '__dict__'): # Class or module
        items = sorted(x.__dict__.items())
        for name, x1 in items:
            if isinstance(x1, _have_code):
                section("Disassembly of %s: " % x)
                try:
                    dis(msg, msg_nocr, section, errmsg, x1,
                        start_line=start_line, end_line=end_line,
                        relative_pos = relative_pos)
                    msg("")
                except TypeError:
                    _, msg, _ = sys.exc_info()
                    errmsg("Sorry:", msg)
                    pass
                pass
            pass
        pass
    elif hasattr(x, 'co_code'): # Code object
        section("Disassembly of %s: " % x)
        disassemble(msg, msg_nocr, section, x, lasti=lasti,
                    start_line=start_line, end_line=end_line,
                    relative_pos = relative_pos)
    elif isinstance(x, str):    # Source code
        disassemble_string(msg, msg_nocr, x,)
    else:
       errmsg("Don't know how to disassemble %s objects." %
              type(x).__name__)
    return

def disassemble(msg, msg_nocr, section, co, lasti=-1, start_line=-1, end_line=None,
                relative_pos=False, color='light'):
    """Disassemble a code object."""
    disassemble_bytes(msg, msg_nocr, co.co_code, lasti, co.co_firstlineno,
                      start_line, end_line, relative_pos,
                      co.co_varnames, co.co_names, co.co_consts,
                      co.co_cellvars, co.co_freevars,
                      dict(findlinestarts(co)), color)
    return

def disassemble_string(source):
    """Compile the source string, then disassemble the code object."""
    disassemble(_try_compile(source, '<dis>'))
    return

def disassemble_bytes(orig_msg, orig_msg_nocr, code, lasti=-1, cur_line=0,
                      start_line=-1, end_line=None, relative_pos=False,
                      varnames=(), names=(), consts=(), cellvars=(),
                      freevars=(), linestarts={}, color='light'):
    """Disassemble byte string of code. If end_line is negative
    it counts the number of statement linestarts to use."""
    statement_count = 10000
    if end_line is None:
        end_line = 10000
    elif relative_pos:
        end_line += start_line -1
        pass
    labels = findlabels(code)
    n = len(code)
    i = 0
    extended_arg = 0
    free = None
    null_print = lambda x: None
    if start_line > cur_line:
        msg_nocr = null_print
        msg = null_print
    else:
        msg_nocr = orig_msg_nocr
        msg = orig_msg
        pass
    while i < n and statement_count >= 0:
        c = code[i]
        op = ord(c)
        if i in linestarts:
            if i > 0:
                msg("")
            cur_line = linestarts[i]
            if start_line and start_line > cur_line:
                msg_nocr = null_print
                msg = null_print
            else:
                statement_count -= 1
                msg_nocr = orig_msg_nocr
                msg = orig_msg
                pass
            if cur_line > end_line: break
            msg_nocr(format_token(Mformat.LineNumber,
                                  "%3d" % cur_line,
                                  highlight=color))
        else:
            msg_nocr('   ')

        if i == lasti: msg_nocr(format_token(Mformat.Arrow, '-->',
                                             highlight=color))
        else: msg_nocr('   ')
        if i in labels: msg_nocr(format_token(Mformat.Arrow, '>>',
                                              highlight=color))
        else: msg_nocr('  ')
        msg_nocr(repr(i).rjust(4))
        msg_nocr(' ')
        msg_nocr(format_token(Mformat.Opcode,
                              opname[op].ljust(20),
                              highlight=color))
        i += 1
        if op >= HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
            extended_arg = 0
            i += 2
            if op == EXTENDED_ARG:
                extended_arg = oparg*65536
            msg_nocr(repr(oparg).rjust(5))
            msg_nocr(' ')
            if op in hasconst:
                msg_nocr('(' +
                         format_token(Mformat.Const,
                                      repr(consts[oparg]),
                                      highlight=color)
                         + ')')
                pass
            elif op in hasname:
                msg_nocr('(' +
                         format_token(Mformat.Name,
                                      names[oparg],
                                      highlight=color)
                         + ')')
            elif op in hasjrel:
                msg_nocr(format_token(Mformat.Label,
                                      '(to ' + repr(i + oparg) + ')',
                                      highlight=color))
            elif op in haslocal:
                msg_nocr('(' +
                         format_token(Mformat.Var,
                                      varnames[oparg],
                                      highlight=color) + ')')
            elif op in hascompare:
                msg_nocr('(' +
                         format_token(Mformat.Compare,
                                      cmp_op[oparg],
                                      highlight=color) + ')')
            elif op in hasfree:
                if free is None:
                    free = cellvars + freevars
                msg_nocr('(' + free[oparg] + ')')
                pass
            pass
        msg("")
    return

# Inspired by show_file from:
# http://nedbatchelder.com/blog/200804/the_structure_of_pyc_files.html
def pyc2code(fname):
    '''Return a code object from a Python compiled file'''
    f = open(fname, "rb")
    magic = f.read(4)
    moddate = f.read(4)
    modtime = time.localtime(struct.unpack('L', moddate)[0])
    code = marshal.load(f)
    f.close()
    return magic, moddate, modtime, code

# Demo it
if __name__ == '__main__':
    def msg(msg_str):
        print(msg_str)
        return
    def msg_nocr(msg_str):
        sys.stdout.write(msg_str)
        return
    def errmsg(msg_str):
        msg('*** ' + msg_str)
        return
    def section(msg_str):
        msg('=== ' + msg_str + ' ===')
        return
    curframe = inspect.currentframe()
    dis(msg, msg_nocr, errmsg, section, curframe,
        start_line=10, end_line=40)
    print('-' * 40)
    dis(msg, msg_nocr, section, errmsg, disassemble)
    print('-' * 40)
    magic, moddate, modtime, co = pyc2code(sys.modules['types'].__file__)
    disassemble(msg, msg_nocr, section, co, -1, 1, 70)
    pass
