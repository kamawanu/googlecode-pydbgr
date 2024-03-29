#!/usr/bin/env python
# -*- coding: utf-8 -*-
'Unit test for trepan.inout.input'
import os, unittest
from import_relative import import_relative, get_srcdir

Minput = import_relative('trepan.inout.input', '...')

class TestDebuggerInput(unittest.TestCase):

    def test_DebuggerInput(self):
        cmdhelper_file=os.path.join(get_srcdir(),'cmdhelper.py')
        inp = Minput.DebuggerUserInput(cmdhelper_file)
        self.assertTrue(inp, 'Should have gotten a DebuggerInput object back')
        line = inp.readline()
        self.assertEqual('# -*- coding: utf-8 -*-', line)
        inp.close()
        # Should be okay
        inp.close()
        return

if __name__ == '__main__':
    unittest.main()
