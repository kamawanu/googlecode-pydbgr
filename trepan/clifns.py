# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os, linecache

# Our local modules
from import_relative import import_relative
Mfile     = import_relative('file', '.lib')

# FIXME: do a better job of this. Live parsing?
def is_ok_line_for_breakpoint(filename, lineno, errmsg_fn):
    """Check whether specified line seems to be executable.

    Return `lineno` if it is, 0 if not (e.g. a docstring, comment, blank
    line or EOF). Warning: testing is not comprehensive.
    """
    line = linecache.getline(filename, lineno)
    if not line:
        errmsg_fn('End of file')
        return False
    line = line.strip()
    # Don't allow setting breakpoint at a blank line
    if (not line or (line[0] == '#') or
         (line[:3] == '"""') or line[:3] == "'''"):
        errmsg_fn('Blank or comment')
        return False
    return True

def file2module(filename):
    """Given a file name, extract the most likely module name. """
    basename = os.path.basename(filename)
    if '.' in basename:
         pos = basename.rfind('.')
         return basename[:pos]
    else:
         return basename
    return None

def search_file(filename, directories, cdir):
    """Return a full pathname for filename if we can find one. path
    is a list of directories to prepend to filename. If no file is
    found we'll return None"""

    for trydir in directories:

        # Handle $cwd and $cdir
        if trydir =='$cwd': trydir='.'
        elif trydir == '$cdir': trydir = cdir

        tryfile = os.path.abspath(os.path.join(trydir, filename))
        if os.path.isfile(tryfile):
            return tryfile
    return None

def whence_file(py_script):
    """Do a shell-like path lookup for py_script and return the results.
    If we can't find anything return py_script"""
    if py_script.find(os.sep) != -1:
        # Don't search since this name has path separator components
        return py_script
    for dirname in os.environ['PATH'].split(os.pathsep):
        py_script_try = os.path.join(dirname, py_script)
        if os.path.exists(py_script_try):
            return py_script_try
    # Failure
    return py_script

def path_expanduser_abs(filename):
    return os.path.abspath(os.path.expanduser(filename))

# Demo
if __name__=='__main__':
    import sys
    print(file2module(sys.argv[0]), sys.argv[0])
    ok = is_ok_line_for_breakpoint(__file__, 1, sys.stdout.write)
    print("\nCan stop at line 1? ", ok)
    ok = is_ok_line_for_breakpoint(__file__, 2, sys.stdout.write)
    print("\nCan stop at line 2? ", ok)
    print(path_expanduser_abs("./.trepan2rc"))
    print(path_expanduser_abs("~/.trepan2rc"))
