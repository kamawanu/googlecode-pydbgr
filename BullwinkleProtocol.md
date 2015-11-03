_Note: this code currently exists only in the Bullwinkle git branch_



# Introduction #

This debugger comes with a rather extensive command-line interface -- possibly _the_ most extensive interface. However, it is still a command-line interface. This debugger was designed to enable others to add different-kinds of front-end interfaces. This alternate API is incomplete and experimental. However we summarize here what we have.

# The Bullwinkle Protocol #

For lack of a better name, we're calling this API the Bullwinkle protocol. A similar one is being developed in new Perl debugger called [Devel::Trepan](https://metacpan.org/module/Devel::Trepan).

The basic idea is that you send a Python dictionary as a request which has a 'command' key. Attributes of the command are also keys. For example for the _step_ command, the command name is, well, _step_, and there is an optional key called _step\_count_ which indications how many times you want to run step. In other words you would send a dictionary like this:

```
   {'command': 'step', 'step_count': 3}
```

As with the command-line interface, the specific command names are modelled off of the _gdb_ command set.

In return you will get one or more hashes sent back which are the responses. Each response has a _name_ key. Informative messages are sent back as an array of strings in the _msg_ key. Error messages are sent back as an array of strings in the _errmsg_ key.

Most of the niceties of the command-line interface like being able to repeat the last command, run debugger command scripts, set up aliases or abbreviations of debugger command names, or automatically evaluate text that is not a debugger command you won't find here. If you are writing a front end and want these, you should provide this in the front end. When needed, or course you can cull from the code I've already written. But I suspect largely you'll want different features or will want to do this differently.

# Command Test Interface #

To get things rolling, I show how you interact with this interface in a simple command-line I have written. The front-end is `bwcli.py` which is located in the source under `pydbgr`. It reads from _stdin_, e.g. a terminal. Each input line should be a string representation of one of these dictionary hashes in the form outlined above.

Sorry, no fancy readline editing here or any sort of terminal niceties; you gotta fit the entire dictionary on one line. If the string evaluates to a valid dictionary, the command is run and the dictionary results are printed .

Here is a sample session:

```
    $ python pydbgr/bwcli.py  pydbgr
    pydbgr/bwprocessor/command/base_cmd.py:25: RuntimeWarning: Parent     module 'pydbgr.bwprocessor.command' not found while handling absolute import
    from import_relative import import_relative
    {'errs': [],
     'event': 'call',
     'location': {'filename': '/usr/local/bin/pydbgr',
                  'fn_name': '<module>',
                  'lineno': 3,
                  'text': "__requires__ = 'pydbgr==0.2.2-01'"},
     'msg': [],
     'name': 'status'}
    Bullwinkle read: {'name': 'step'}
    {'errs': ["invalid input, expecting a 'command' key: {'name': 'step'}"],
     'msg': [],
     'name': 'error'}
    Bullwinkle read: {'command': 'step'}
    {'errs': [], 'msg': [], 'name': 'step', 'step_count': 1}
    {'errs': [],
     'event': 'line',
     'location': {'filename': '/usr/local/bin/pydbgr',
                  'fn_name': '<module>',
                  'lineno': 3,
                  'text': "__requires__ = 'pydbgr==0.2.2-01'"},
     'msg': [],
     'name': 'status',
     'step_count': 1}
    Bullwinkle read: {'command': 'step', 'step_count': 2}
    {'errs': [], 'msg': [], 'name': 'step', 'step_count': 2}
    {'errs': [],
     'event': 'line',
     'location': {'filename': '/usr/local/bin/pydbgr',
                  'fn_name': '<module>',
                  'lineno': 4,
                  'text': 'import sys'},
     'msg': [],
     'name': 'status',
     'step_count': 2}
    Bullwinkle read: {'command': 'quit'}
    {'errs': [], 'event': 'terminated', 'msg': [], 'name': 'status'}
    $
```

# Specific Commands #

Right now we have a very small number of commands listed since this is a proof of concept. If someone starts using this, more commands can easily be added.

## Quit ##

Gently exits the debugger and debugged program.

### Input Fields ###

```
   { command     => 'quit'}
```

The program being debugged is exited raising a _DebuggerQuit_ exception.

### Output Fields ###

```
   { name      => 'status',
     event     => 'terminated',
     [errmsg   => <error-message-array>]
     [msg      => <message-text array>]
   }
```

## Step ##

step statements

### Input Fields ###

```
   { command  => 'step',
     [count   => <integer>],
   }
```

If _count\_is given, that many statements will be stepped. If it
is not given, 1 is used, i.e. stop at the next statement._

### Output Fields ###

```
   { name     => 'step',
     count    => <integer>,
     [errmsg  => <error-message-array>]
     [msg     => <message-text array>]
   }
```

# To Do #

This is experimental and incomplete. It will move forward only if there is serious interest (which means work on someone else's part) in using this. What's missing right now is hooking this into the remote access we currently have. This is straight-forward since this has been done in the Perl debugger already and already we have most of the underlying Python modules for remote communication.

Right now the existing remote access is just a glorified read loop on the one side which transports a command-line command via TCP/IP to a command-line processor running on the remote side. This is interesting and useful, but something different.