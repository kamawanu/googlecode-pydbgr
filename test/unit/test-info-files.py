#!/usr/bin/env python
'Unit test for debugger info file'
import inspect, unittest
from import_relative import import_relative

debugger  = import_relative('debugger', '...trepan', 'trepan')
Minfo     = import_relative('trepan.processor.command.info', '...')
MinfoFile = import_relative('trepan.processor.command.info_subcmd.files',
                            '...')
Mdebugger = import_relative('debugger', '...trepan')

from cmdhelper import dbg_setup

class TestInfoFile(unittest.TestCase):

    # FIXME: put in a more common place
    # Possibly fix up Mock to include this
    def setup_io(self, command):
        self.clear_output()
        command.msg = self.msg
        command.errmsg = self.errmsg
        command.msg_nocr = self.msg_nocr
        return

    def clear_output(self):
        self.msgs = []
        self.errmsgs = []
        self.last_was_newline = True
        return

    def msg_nocr(self, msg):
        if len(self.msgs) > 0:
            self.msgs[-1] += msg
        else:
            self.msgs += msg
            pass
        return
    def msg(self, msg):
        self.msgs += [msg]
        return

    def errmsg(self, msg):
        self.errmsgs.append(msg)
        pass

    def test_info_file(self):
        d = Mdebugger.Debugger()
        d, cp = dbg_setup(d)
        command = Minfo.InfoCommand(cp, 'info')

        sub = MinfoFile.InfoFiles(command)
        self.setup_io(sub)
        sub.run([])
        self.assertEqual([], self.msgs)
        cp.curframe = inspect.currentframe()
        for width in (80, 200):
            # sub.settings['width'] = width
            sub.run(['test-info-file.py', 'lines'])
            sub.run([])
            pass
        pass

if __name__ == '__main__':
    unittest.main()
