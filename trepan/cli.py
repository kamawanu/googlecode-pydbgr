#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#   Copyright (C) 2008-2010, 2013-2014 Rocky Bernstein <rocky@gnu.org>
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
'''The command-line interface to the debugger.
'''
import os, os.path, sys

package='trepan'
if not package in sys.modules:
    __import__('pkg_resources').declare_namespace(package)
    pass

# Our local modules
from import_relative import import_relative, get_srcdir
Minterface = import_relative('interface', '.',   package)
Mapi       = import_relative('api',       '.',   package)
Mclient    = import_relative('client',    '.',   package)
Mclifns    = import_relative('clifns',    '.',   package)
Mdebugger  = import_relative('debugger',  '.',   package)
Mexcept    = import_relative('exception', '..trepan')
Moptions   = import_relative('options',   '.',   package)
Mserver    = import_relative('server', '.interfaces', package)
Mfile      = import_relative('file',   '.lib',   package)
Mmisc      = import_relative('misc',   '.',      package)

# The name of the debugger we are currently going by.
__title__ = package + '2'

# VERSION.py sets variable VERSION.
VERSION='??'
exec(compile(open(os.path.join(get_srcdir(), 'VERSION.py')).read(), os.path.join(get_srcdir(), 'VERSION.py'), 'exec'))
__version__ = VERSION

def main(dbg=None, sys_argv=list(sys.argv)):
    """Routine which gets run if we were invoked directly"""
    global __title__

    # Save the original just for use in the restart that works via exec.
    orig_sys_argv = list(sys_argv)
    opts, dbg_opts, sys_argv  = Moptions.process_options(__title__, __version__,
                                                         sys_argv)

    if opts.server:
        connection_opts={'IO': 'TCP', 'PORT': opts.port}
        intf = Mserver.ServerInterface(connection_opts=connection_opts)
        dbg_opts['interface'] = intf
        if 'FIFO' == intf.server_type:
            print('Starting FIFO server for process %s.' % os.getpid())
        elif 'TCP' == intf.server_type:
            print('Starting TCP server listening on port %s.' % intf.inout.PORT)
            pass
    elif opts.client:
        Mclient.main(opts, sys_argv)
        return

    dbg_opts['orig_sys_argv'] = orig_sys_argv

    if dbg is None:
        dbg = Mdebugger.Debugger(dbg_opts)
        dbg.core.add_ignore(main)
        pass
    Moptions._postprocess_options(dbg, opts)

    # process_options has munged sys.argv to remove any options that
    # options that belong to this debugger. The original options to
    # invoke the debugger and script are in global sys_argv

    if len(sys_argv) == 0:
        # No program given to debug. Set to go into a command loop
        # anyway
        mainpyfile = None
    else:
        mainpyfile = sys_argv[0] # Get script filename.
        if not os.path.isfile(mainpyfile):
            mainpyfile=Mclifns.whence_file(mainpyfile)
            is_readable = Mfile.readable(mainpyfile)
            if is_readable is None:
                print("%s: Python script file '%s' does not exist" \
                      % (__title__, mainpyfile,))
                sys.exit(1)
            elif not is_readable:
                print("%s: Can't read Python script file '%s'" \
                    % (__title__, mainpyfile,))
                sys.exit(1)
                return

        # If mainpyfile is an optimized Python script try to find and
        # use non-optimized alternative.
        mainpyfile_noopt = Mfile.file_pyc2py(mainpyfile)
        if mainpyfile != mainpyfile_noopt \
               and Mfile.readable(mainpyfile_noopt):
            print("%s: Compiled Python script given and we can't use that." % __title__)
            print("%s: Substituting non-compiled name: %s" % (
                __title__, mainpyfile_noopt,))
            mainpyfile = mainpyfile_noopt
            pass

        # Replace trepan's dir with script's dir in front of
        # module search path.
        sys.path[0] = dbg.main_dirname = os.path.dirname(mainpyfile)

    # XXX If a signal has been received we continue in the loop, otherwise
    # the loop exits for some reason.
    dbg.sig_received = False

    # if not mainpyfile:
    #     print('For now, you need to specify a Python script name!')
    #     sys.exit(2)
    #     pass

    while True:

        # Run the debugged script over and over again until we get it
        # right.

        try:
            if dbg.program_sys_argv and mainpyfile:
                normal_termination = dbg.run_script(mainpyfile)
                if not normal_termination: break
            else:
                dbg.core.execution_status = 'No program'
                dbg.core.processor.process_commands()
                pass

            dbg.core.execution_status = 'Terminated'
            dbg.intf[-1].msg("The program finished - quit or restart")
            dbg.core.processor.process_commands()
        except Mexcept.DebuggerQuit:
            break
        except Mexcept.DebuggerRestart:
            dbg.core.execution_status = 'Restart requested'
            if dbg.program_sys_argv:
                sys.argv = list(dbg.program_sys_argv)
                part1 = ('Restarting %s with arguments:' %
                         dbg.core.filename(mainpyfile))
                args  = ' '.join(dbg.program_sys_argv[1:])
                dbg.intf[-1].msg(Mmisc.wrapped_lines(part1, args,
                                                     dbg.settings['width']))
            else: break
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            break
        except:
            ## FIXME: Should be handled above without this mess
            exception_name = str(sys.exc_info()[0])
            if exception_name == str(Mexcept.DebuggerQuit):
                break
            elif exception_name == str(Mexcept.DebuggerRestart):
                dbg.core.execution_status = 'Restart requested'
                if dbg.program_sys_argv:
                    sys.argv = list(dbg.program_sys_argv)
                    part1 = ('Restarting %s with arguments:' %
                             dbg.core.filename(mainpyfile))
                    args  = ' '.join(dbg.program_sys_argv[1:])
                    dbg.intf[-1].msg(Mmisc.wrapped_lines(part1, args,
                                                         dbg.settings['width']))
                    pass
            else:
                raise
        pass

    # Restore old sys.argv
    sys.argv = orig_sys_argv
    return

# When invoked as main program, invoke the debugger on a script
if __name__=='__main__':
    main()
    pass
