

# Introduction #

It is possible to debug a python program from outside the program, which can be either from the same computer or from a different computer.


# Details #

There are two parts to out-of-process debugging:

  * Setting up the hook in the debugged program
  * Attaching from outside the process.

## Simple invocation ##

In the simplest case below we'll start out debugging from the outset using a socket and attaching from another process on the same server.

In one shell run:

```
$ trepan2 --server trepan2
Starting TCP server listening on port 1027.
```

(the 2nd _trepan2_ is the name of the program to debug. Since _trepan2_ is just a Python program that's always available, I used that.)

Now in a second shell, run:

```
$ trepan2 --client
Connected.
(/usr/local/bin/trepan2:3): <module>
-> 3 __requires__ = 'trepan==0.2.8-01'
(trepan2*) step
(/usr/local/bin/trepan2:4): <module>
-- 4 import sys
(trepan2*) step
(/usr/local/bin/trepan2:5): <module>
-- 5 from pkg_resources import load_entry_point
```


## Debugging via sockets on a different host ##

Running the server sets up a listener on all network interfaces. Use the `--host` option on the "client" side to specify the name of a server you are running on different computer. By default the server connected to is IP 127.0.0.1

For example on a computer with IP 192.168.1.5:

```
$ trepan2 --server trepan2
Starting TCP server listening on port 1027.
```

Now on a another computer with access to 192.168.1.5:

```
$ trepan2 --client --server 192.168.1.5
Connected.
(/usr/local/bin/trepan2:3): <module>
-> 3 __requires__ = 'trepan==0.2.8-01'
```

Instead of an IP address you can give instead DNS name.

Note: connection to the debugged program will only work after the debugged program goes into "server" mode inside the debugger.

### Explicit Debugger call via sockets ###

If you don't call the debugger from the outset, you can arrange to call the debugger set up to listen on a socket with code inside your Python program.

Here is an example. Change your Python code to include something along the lines below:

```
import trepan.api
from trepan.interfaces.server import ServerInterface

## One-time setup.
connection_opts={'IO': 'TCP'}
intf = ServerInterface(connection_opts=connection_opts)

## work work work

trepan.api.debug(dbg_opts={'interface': intf}, post_mortem=False)

```

As before, to connect to the stopped and debugged program:

```
$ trepan2 --client
```

And as before connection to the debugged program will only work after the debugged program goes into "server" mode inside the debugger.