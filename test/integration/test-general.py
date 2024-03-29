#!/usr/bin/env python
"General integration tests"
import unittest

from import_relative import import_relative
Mhelper = import_relative('helper', '.')

class GeneralTests(unittest.TestCase):

    def test_step(self):
        """Test stepping, set skip, set trace"""
        result=Mhelper.run_debugger(testname='step',
                                    dbgr_opts='--basename --highlight=plain',
                                    python_file='gcd.py')
        self.assertEqual(True, result, "debugger 'step' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
