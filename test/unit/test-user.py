#!/usr/bin/env python
'Unit test for trepan.interfaces.user'
import unittest

from import_relative import import_relative
Muser = import_relative('interfaces.user', '...trepan')

from cmdhelper import dbg_setup

class TestInterfaceUser(unittest.TestCase):
    """Tests UserInterface class"""

    def readline(self, answer):
        return answer

    def test_confirm(self):
        """Test interface.user.UserInterface.confirm()"""
        d, cp = dbg_setup()
        u = Muser.UserInterface()
        for s in ['y', 'Y', 'Yes', '  YES  ']:
            u.input.readline = lambda prompt=None: self.readline(s)
            self.assertTrue(u.confirm('Testing', True))
            pass
        for s in ['n', 'N', 'No', '  NO  ']:
            u.input.readline = lambda prompt=None: self.readline(s)
            self.assertFalse(u.confirm('Testing', True))
            pass
        # FIXME: Add checking default values. Checking looping
        # values
        return
    # FIXME: more thorough testing of other routines in user.

if __name__ == '__main__':
    unittest.main()
