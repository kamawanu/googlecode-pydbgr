#!/usr/bin/env python
'Unit test for trepan.bytecode'
import inspect, unittest
from import_relative import import_relative

Mcode = import_relative('lib.bytecode', '...trepan')

class TestByteCode(unittest.TestCase):

    def test_contains_make_function(self):
        def sqr(x):
            return x * x
        frame = inspect.currentframe()
        co = frame.f_code
        lineno = frame.f_lineno
        self.assertTrue(Mcode.stmt_contains_opcode(co, lineno-4,
                                                   'MAKE_FUNCTION'))
        self.assertFalse(Mcode.stmt_contains_opcode(co, lineno,
                                                    'MAKE_FUNCTION'))
        return

    def test_op_at_frame(self):
        frame = inspect.currentframe()
        self.assertEqual('CALL_FUNCTION', Mcode.op_at_frame(frame))
        return

    def test_is_def_frame(self):
        # Not a "def" statement because frame is wrong spot
        frame = inspect.currentframe()
        self.assertFalse(Mcode.is_def_stmt('foo(): pass', frame))
        return

if __name__ == '__main__':
    unittest.main()
