#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#   Copyright (C) 2013-2014 Rocky Bernstein <rocky@gnu.org>
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

import os, sys
from optparse import OptionParser
from import_relative import import_relative
Mdebugger  = import_relative('debugger', '.')
Mapi       = import_relative('api',      '.')
Mclifns    = import_relative('clifns',   '.')
Mfile      = import_relative('file',     '.lib')
Moutput    = import_relative('output',   '.inout')

def process_options(debugger_name, pkg_version, sys_argv, option_list=None):
    """Handle debugger options. Set `option_list' if you are writing
    another main program and want to extend the existing set of debugger
    options.

    The options dicionary from opt_parser is return. sys_argv is
    also updated."""
    usage_str="""%prog [debugger-options] [python-script [script-options...]]

    Runs the extended python debugger"""

    ## serverChoices = ('TCP','FIFO', None)


    optparser = OptionParser(usage=usage_str, option_list=option_list,
                             version="%%prog version %s" % pkg_version)

    optparser.add_option("-X", "--trace", dest="linetrace",
                         action="store_true", default=False,
                         help="Show lines before executing them. " +
                         "This option also sets --batch")
    optparser.add_option("-F", "--fntrace", dest="fntrace",
                         action="store_true", default=False,
                         help="Show functions before executing them. " +
                         "This option also sets --batch")
    optparser.add_option("--basename", dest="basename",
                         action="store_true", default=False,
                         help="Filenames strip off basename, " +
                         "(e.g. for regression tests)"
                         )
    #     optparser.add_option("--batch", dest="noninteractive",
    #                          action="store_true", default=False,
    #                          help="Don't run interactive commands shell on "+
    #                          "stops.")
    optparser.add_option("--client", dest="client",
                         action='store_true',
                         help="Connect to an existing debugger process " +
                         "started with the --server option. " +
                         "See options for client.")
    optparser.add_option("-x", "--command", dest="command",
                         action="store", type='string', metavar='FILE',
                         help="Execute commands from FILE.")
    optparser.add_option("--cd", dest="cd",
                         action="store", type='string', metavar='DIR',
                         help="Change current directory to DIR.")
    optparser.add_option("--confirm", dest="confirm",
                         action="store_true", default=True,
                         help="Confirm potentially dangerous operations")
    optparser.add_option("--dbg_trepan", dest="dbg_trepan",
                         action="store_true", default=False,
                         help="Debug the debugger")
    optparser.add_option("--different", dest="different",
                         action="store_true", default=True,
                         help="Consecutive stops should have different positions")
    #     optparser.add_option("--error", dest="errors", metavar='FILE',
    #                          action="store", type='string',
    #                          help="Write debugger's error output "
    #                          + "(stderr) to FILE")
    optparser.add_option("-e", "--exec", dest="execute", type="string",
                         help="list of debugger commands to " +
                         "execute. Separate the commands with ;;")

    optparser.add_option("-H", "--host", dest="host", default='127.0.0.1',
                         action="store", type='string', metavar='IP-OR-HOST',
                         help="connect IP or host name. Only valid if --client option given.")

    optparser.add_option("--highlight", dest="highlight",
                         action="store", type='string', metavar='{light|dark|plain}',
                         default='light',
                         help="Use syntax and terminal highlight output. 'plain' is no highlight")
    optparser.add_option("--private", dest="private",
                         action='store_true', default=False,
                         help="Don't register this as a global debugger")

    optparser.add_option("--post-mortem", dest="post_mortem",
                         action='store_true', default=True,
                         help="Enter debugger on an uncaught (fatal) exception")

    optparser.add_option("--no-post-mortem", dest="post_mortem",
                         action='store_false', default=True,
                         help="Don't enter debugger on an uncaught (fatal) exception")

    optparser.add_option("-n", "--nx", dest="noexecute",
                         action="store_true", default=False,
                         help="Don't execute commands found in any " +
                         "initialization files")
    optparser.add_option("-o", "--output", dest="output", metavar='FILE',
                         action="store", type='string',
                         help="Write debugger's output (stdout) "
                         + "to FILE")
    optparser.add_option("-P", "--port", dest="port", default=1027,
                         action="store", type='int',
                         help="Use TCP port number NUMBER for out-of-process connections.")
    optparser.add_option("--server", dest="server",
                         action='store_true',
                         help="Out-of-process server connection mode")
    optparser.add_option("--sigcheck", dest="sigcheck",
                         action="store_true", default=False,
                         help="Set to watch for signal handler changes")
    optparser.add_option("-t", "--target", dest="target",
                         help="Specify a target to connect to. Arguments" \
                         + " should be of form, 'protocol address'."),

    # annotate option produces annotations, used in trepan.el for a better emacs
    # integration. Annotations are similar in purpose to those of GDB (see
    # that manual for a description), although the syntax is different.
    # they have the following format:
    #
    # ^Z^Zannotation-name
    # <arbitrary text>
    # ^Z^Z
    #
    # where ^Z is the ctrl-Z character, and "annotname" is the name of the
    # annotation. A line with only two ^Z ends the annotation (no nesting
    # allowed). See trepan.el for the usage
    optparser.add_option("--annotate", default=0, type="int",
                         help="Use annotations to work inside emacs")

    # Set up to stop on the first non-option because that's the name
    # of the script to be debugged on arguments following that are
    # that scripts options that should be left untouched.  We would
    # not want to interpret and option for the script, e.g. --help, as
    # one one of our own, e.g. --help.

    optparser.disable_interspersed_args()

    sys.argv = list(sys_argv)
    (opts, sys.argv) = optparser.parse_args()
    dbg_opts = {}

    # Handle debugger startup command files: --nx (-n) and --command.
    dbg_initfiles = []
    if not opts.noexecute:
        # Read debugger startup file(s), e.g. $HOME/.trepan2rc and ./.trepan2rc
        startup_file = ".%s2rc" % debugger_name
        # expanded_startup_file = Mclifns.path_expanduser_abs(startup_file)
        if 'HOME' in os.environ:
            startup_home_file = os.path.join(os.environ['HOME'], startup_file)
            expanded_startup_home = \
                                  Mclifns.path_expanduser_abs(startup_home_file)
            if Mfile.readable(expanded_startup_home):
                dbg_initfiles.append(startup_home_file)
                pass
            pass
        #         if Mfile.readable(expanded_startup_file) and \
        #                 expanded_startup_file != expanded_startup_home:
        #             dbg_initfiles.append(debugger_startup)
        #             pass
        pass

    # As per gdb, first we execute user initialization files and then
    # we execute any file specified via --command.
    if opts.command:
        dbg_initfiles.append(opts.command)
        pass

    dbg_opts['proc_opts'] = {'initfile_list': dbg_initfiles}

    if opts.cd:
        os.chdir(opts.cd)
        pass

    if opts.output:
        try:
            dbg_opts['output'] = Moutput.DebuggerUserOutput(opts.output)
        except IOError:
            _, xxx_todo_changeme, _ = sys.exc_info()
            (errno, strerror) = xxx_todo_changeme.args
            print("I/O in opening debugger output file %s" % opts.output)
            print("error(%s): %s" % (errno, strerror))
        except:
            print("Unexpected error in opening debugger output file %s" % \
                  opts.output)
            print(sys.exc_info()[0])
            sys.exit(2)
            pass
        pass

    return opts, dbg_opts, sys.argv

def _postprocess_options(dbg, opts):
    ''' Handle options (`opts') that feed into the debugger (`dbg')'''
    # Set dbg.settings['printset']
    print_events = []
    if opts.fntrace:   print_events = ['c_call', 'c_return', 'call', 'return']
    if opts.linetrace: print_events += ['line']
    if len(print_events):
       dbg.settings['printset'] = frozenset(print_events)
       pass

    for setting in ('annotate', 'basename', 'different',):
       dbg.settings[setting] = getattr(opts, setting)
       pass

    if getattr(opts, 'highlight'):
        dbg.settings['highlight'] = opts.highlight
    else:
        dbg.settings['highlight'] = 'plain'

    # Normally we want to set Mdebugger.debugger_obj so that one can
    # put trepan.debugger breakpoints in a program and not have more
    # than one debugger running. More than one debugger may confuse
    # users, e.g. set different might stop at the same line once for
    # each debugger.
    if not opts.private:
        Mdebugger.debugger_obj = dbg
        pass

    #     if opts.errors:
    #         try:
    #             dbg.stderr = open(opts.errors, 'w')
    #         except IOError, (errno, strerror):
    #             print "I/O in opening debugger output file %s" % opts.errors
    #             print "error(%s): %s" % (errno, strerror)
    #         except ValueError:
    #             print "Could not convert data to an integer."
    #         except:
    #             print "Unexpected error in opening debugger output file %s" % \
    #                   opts.errors
    #             print sys.exc_info()[0]
    #             sys.exit(2)

    #     if opts.execute:
    #         dbg.cmdqueue = list(opts.execute.split(';;'))

    if opts.post_mortem:
        Mapi.debugger_on_post_mortem()
        pass
    return

# Demo it
if __name__=='__main__':
	import pprint

	def doit(prog, version, arg_str):
		print("options '%s'" % arg_str)
		args = arg_str.split()
		opts, dbg_opts, sys_argv = process_options('testing', '1.0', args)
		pp.pprint(vars(opts))
		print('')
		return

	pp = pprint.PrettyPrinter(indent=4)
	doit('testing', '1.1', '')
	doit('testing', '1.2', 'foo bar')
	doit('testing', '1.3', '--server')
	doit('testing', '1.3', '--command %s bar baz' % __file__)
	doit('testing', '1.4', '--server --client')
	doit('testing', '1.5', '--help')
	pass
